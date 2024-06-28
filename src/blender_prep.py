# Third time's a charm
import os
os.environ["OPENCV_IO_MAX_IMAGE_camera.ncols"] = pow(2,40).__str__()
import cv2
import numpy as np
from numpy import sin,cos,deg2rad,arcsin,arccos,rad2deg,pi,arctan2
from numpy import array,zeros,ones,dot,cross,sqrt,sum
from numpy.linalg import norm
import struct
from Point import *
from Structures import Quaternion,State
import mathutil as mu
import ctypes as ct
from Camera import Camera,get_camera


def rot_about(a,b,theta):
	a_par_b = (dot(a,b)/dot(b,b))*b
	a_perp_b = a - a_par_b
	w = cross(b,a_perp_b)
	x1 = cos(theta)/np.linalg.norm(a_perp_b)
	x2 = sin(theta)/np.linalg.norm(w)
	a_perp_btheta = np.linalg.norm(a_perp_b)*(x1*a_perp_b+x2*w)
	return array(a_perp_btheta + a_par_b)


def get_coverage(pos,los,moon_xyzs,fov):
	shape = array(moon_xyzs.shape)
	shape[2] = 1
	diff = moon_xyzs-pos
	fov_bounds = cos(fov/2)
	max_dist = sqrt(norm(pos)**2+RADIUS**2)
	moon_los = diff/norm(diff,axis=2).reshape(shape)
	angles = np.where(norm(diff,axis=2)<=max_dist,np.dot(moon_los,los),-1)
	blob = np.where(angles>fov_bounds,norm(diff,axis=2),-1)
	return blob


def grassy_knoll(camera):
	### The Grassy Knoll Method

	# Let's Build a Moon
	ra_sections = 360
	decl_sections = 180
	ra = np.linspace(0,2*np.pi,ra_sections,endpoint=False)
	ras = np.tile(ra,decl_sections).reshape(decl_sections,ra_sections)

	decl = np.linspace(-np.pi/2,np.pi/2,decl_sections)
	decls = np.repeat(decl,ra_sections).reshape(decl_sections,ra_sections)

	xyzs = array([RADIUS*cos(decls)*cos(ras),RADIUS*cos(decls)*sin(ras),RADIUS*sin(decls)]).transpose((2,1,0))
	fov_bounds = cos(sqrt(camera.FOV_x**2+camera.FOV_y**2)/2)
	print("FOV Bounds: {:.4f}".format(fov_bounds))

	DCM = camera.state.attitude.toDCM()
	los = DCM@array([0,0,1])
	pos = camera.state.position
	los = los/norm(los)
	print(los)
	TOL = 100000
	OFFNADIR_THRESH = deg2rad(10)
	unity_pos = pos/norm(pos)
	offnadir = arccos(dot(unity_pos,-los))
	print("NADIR Angle = {}".format(rad2deg(offnadir)))
	if offnadir < OFFNADIR_THRESH:
		return camera

	diff = xyzs-pos
	moon_los = diff/norm(diff,axis=2).reshape(ra_sections,decl_sections,1)

	nabla = dot(-moon_los,pos)**2-(norm(pos)**2-RADIUS**2)
	min_dist = abs(-dot(-moon_los,pos)+sqrt(nabla))
	angles = np.where(min_dist+TOL>=norm(diff,axis=2),np.dot(moon_los,los),-1)
	blob_target = np.where(angles>fov_bounds,norm(diff,axis=2),-1)

	# Finding the center of the blob
	blob_xyzs = np.where(blob_target.reshape(360,180,1)>-1,xyzs,array([0,0,0]))
	blob_mask = np.array(np.where(norm(blob_xyzs,axis=2)>0))

	pts_xyzs = blob_xyzs[blob_mask[0,:],blob_mask[1,:],:]
	if len(pts_xyzs) == 0:
		# No good, no Moon here...
		return None
	
	ctr_xyz = np.average(pts_xyzs,axis=0)
	ctr_los = ctr_xyz/norm(ctr_xyz)
	decl = arcsin(ctr_los[2])
	if decl > np.pi/2:
		decl -= np.pi
	ra = arccos(ctr_los[0]/cos(decl))
	print(rad2deg(ra),rad2deg(decl))

	# Finding the furthest extremities
	pos2 = ctr_los*RADIUS*1.2
	los2 = -ctr_los
	blob = get_coverage(pos2,los2,xyzs,min([camera.FOV_x,camera.FOV_y]))
	cont = len(np.where(blob_target>blob)[0])
	while cont > 0:
		pos2*=1.2
		blob = get_coverage(pos2,los2,xyzs,min([camera.FOV_x,camera.FOV_y]))
		cont = len(np.where(blob_target>blob)[0])
		print(cont)

	# Build the Second State
	global_z = los2
	global_x = array([-sin(ra),cos(ra),0])
	global_y = rot_about(global_z,global_x,pi/2)
	local_z = array([0,0,1])
	local_x = array([1,0,0])
	local_y = array([0,-1,0])
	dcm = mu.wahbas_problem(array([global_z,global_x,global_y]),
												array([local_z,local_x,local_y]))

	quat = Quaternion()
	quat.fromDCM(dcm)

	print(dcm.T@global_z)

	camera.set_state(State(pos2,quat))

	return camera


# Globals
RADIUS = 1737400 # m

if __name__ == "__main__":
	## Testing
	camera = get_camera("../configs/cameras/testcam.json")
	quatWorldtoCam = Quaternion()
	quatWorldtoCam.fromDCM(array([[0,0,1],
																[-1,0,0],
																[0,-1,0]]))
	#sc_quat = Quaternion(0,[0,0,1])
	#sc_quat = Quaternion(0.707,[0,-0.707,0])
	#sc_quat = Quaternion(.707,[0,0,-.707])
	#sc_quat = Quaternion(0.1,[0,0,-0.995])
	sc_quat = Quaternion(1,[0,0,0])
	#sc_quat = Quaternion(0.216668887,[0.702665992,-0.161286356,-0.658256643])
	#pos = array([2450487.68,-1768944.776,951442.2338])
	quat = Quaternion()
	#print(sc_quat)
	dcm = sc_quat.toDCM().T@quatWorldtoCam.toDCM()
	#print(sc_quat.toDCM())
	#print(quatWorldtoCam.toDCM())
	#print(dcm)
	quat.fromDCM(dcm)
	#quat = Quaternion(0.216668887,[-0.702665992,0.161286356,0.658256643])
	pos = array([-RADIUS*7,0,0])
	state = State(pos,quat)
	camera.set_state(state)

	print("Running Grassy Knoll")
	#camera = grassy_knoll(camera)
	if camera is None:
		print("No Moon to be Visualized")
		exit(0)
	print("Pos: {}".format(camera.state.position))
	print("Quat: {}".format(camera.state.attitude))
	print("DCM:\n{}".format(camera.state.attitude.toDCM()))

	
	print(np.rad2deg(camera.FOV_x),np.rad2deg(camera.FOV_y))
	print(camera.F_Stop)
	print(camera.OffsetPix)

	#exit()
	
	print("Finished Loading DEM")
	mesh = zeros(shape=(camera.SubSamples*(2*camera.OffsetPix[0]+camera.Ncols),
										  camera.SubSamples*(2*camera.OffsetPix[1]+camera.Nrows),
										  3))
	colors = zeros(shape=(camera.SubSamples*(2*camera.OffsetPix[0]+camera.Ncols),
										  	camera.SubSamples*(2*camera.OffsetPix[1]+camera.Nrows),
										  	2))
	print("Building Mesh")
	## Trying out the Cpp Library
	libPoints = ct.cdll.LoadLibrary("cpp/libPoints.so")
	create_mesh = libPoints.findPoints
	create_mesh.argtypes = [(ct.c_float*3),
												 	(ct.c_float*9),
													(ct.c_int*2),
													(ct.c_float*2),
													ct.POINTER(ct.c_float),
													ct.POINTER(ct.c_float),
													(ct.c_ulong*2),
													ct.c_float,
													(ct.c_float*2),
													ct.c_char_p]
	# Setup data
	print("Setting Up Data")
	pos_c = (ct.c_float*3)(*(camera.state.position))
	dcm_c = (ct.c_float*9)(*(camera.state.attitude.toDCM().flatten()))
	camsize_c = (ct.c_int*2)(*[camera.Ncols,camera.Nrows])
	offset_c = (ct.c_float*2)(*camera.OffsetPix)
	meshsize = np.array(mesh.shape)
	colorsize = np.array(colors.shape)
	meshsize_flt = np.prod(meshsize)
	#meshsize_flt = meshsize[0]*meshsize[1]*meshsize[2]
	colorsize_flt = np.prod(colorsize)
	#colorsize_flt = colorsize[0]*colorsize[1]*colorsize[2]
	mesh_c = (ct.c_float*meshsize_flt)()
	colors_c = (ct.c_float*colorsize_flt)()
	meshsize_c = (ct.c_ulong*2)(*meshsize[:2])
	SubSamples_c = ct.c_float(camera.SubSamples)
	fov_c = (ct.c_float*2)(camera.FOV_x,camera.FOV_y)
	dirname_c = ct.create_string_buffer("./".encode())
	status = create_mesh(pos_c,dcm_c,camsize_c,offset_c,mesh_c,colors_c,meshsize_c,SubSamples_c,fov_c,dirname_c)
	print("Status: {}".format(status))
	meshsize = np.array([meshsize[1],meshsize[0],meshsize[2]])
	colorsize = np.array([colorsize[1],colorsize[0],colorsize[2]])
	mesh = np.frombuffer(mesh_c,dtype=np.float32).reshape(meshsize)
	colors = np.frombuffer(colors_c,dtype=np.float32).reshape(colorsize)
	print(mesh)
	print(colors)
	#print(norm(mesh,axis=2))
