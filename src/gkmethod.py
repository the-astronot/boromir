# Library imports
import numpy as np
from numpy import array,sin,cos,arcsin,arccos,sqrt,deg2rad,rad2deg,dot
from numpy.linalg import norm

# Local imports
import mathutil as mu
from Structures import Quaternion,State


# Global Vars
RADIUS = 1737400 # meters


def gkmethod(camera):
	"""
		Alternative method for establishing a mesh.
		Rather than making a mesh from what the camera can see, an imaginary 
		NADIR-pointing camera is created which can see everything in the FoV
		of the actual camera. Useful for situations when the real camera is 
		VERY non-NADIR pointing.
	"""
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
	los = (los/norm(los))
	print(los)
	TOL = 100000
	OFFNADIR_THRESH = deg2rad(10)
	unity_pos = (pos/norm(pos)).reshape(3,)
	offnadir = arccos(dot(unity_pos,-los))
	print("NADIR Angle = {}".format(rad2deg(offnadir)))
	if offnadir < OFFNADIR_THRESH:
		return camera

	diff = xyzs-pos.reshape(3,)
	print(diff.shape)
	moon_los = diff/norm(diff,axis=2).reshape(ra_sections,decl_sections,1)

	nabla = dot(-moon_los,pos)**2-(norm(pos)**2-RADIUS**2)
	min_dist = abs(-dot(-moon_los,pos)+sqrt(nabla))
	angles = np.where((min_dist+TOL).reshape(360,180)>=norm(diff,axis=2),np.dot(moon_los,los),-1)
	blob_target = np.where(angles>fov_bounds,norm(diff,axis=2),-1)

	# Finding the center of the blob
	blob_xyzs = np.where(blob_target.reshape(360,180,1)>-1,xyzs,array([0,0,0]))
	blob_mask = np.array(np.where(norm(blob_xyzs,axis=2)>0))

	pts_xyzs = blob_xyzs[blob_mask[0,:],blob_mask[1,:],:]
	if len(pts_xyzs) == 0:
		print("No Moon in View")
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
	global_y = mu.rot_about(global_z,global_x,np.pi/2)
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