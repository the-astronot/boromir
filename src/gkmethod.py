# Library imports
import numpy as np
from numpy import array,sin,cos,arcsin,arccos,sqrt,deg2rad,rad2deg,dot
from numpy.linalg import norm

# Local imports
import mathutil as mu
from Structures import Quaternion,State
from file_io import critical,warning,info,debug


# Global Vars
RADIUS = 1737400 # meters
TOL = 100000 # meters
OFFNADIR_THRESH = deg2rad(10) # radians


def gkmethod(camera):
	"""
		Alternative method for establishing a mesh.
		Rather than making a mesh from what the camera can see, an imaginary 
		NADIR-pointing camera is created which can see everything in the FoV
		of the actual camera. Useful for situations when the real camera is 
		VERY non-NADIR pointing and would cause excessive tearing/artifacts.
	"""
	info("Using GK Method")
	# Let's Build a Lower-Poly Moon
	ra_sections = 360
	decl_sections = 180

	# Create arrays of ra and decl values
	ra = np.linspace(0,2*np.pi,ra_sections,endpoint=False)
	ras = np.tile(ra,decl_sections).reshape(decl_sections,ra_sections)
	decl = np.linspace(-np.pi/2,np.pi/2,decl_sections)
	decls = np.repeat(decl,ra_sections).reshape(decl_sections,ra_sections)

	# Convert ra and decls to xyz coords
	xyzs = array([RADIUS*cos(decls)*cos(ras),RADIUS*cos(decls)*sin(ras),RADIUS*sin(decls)]).transpose((2,1,0))

	# Find camera FOV bounds
	fov_bounds = cos(sqrt(camera.FOV_x**2+camera.FOV_y**2)/2)
	debug("FOV Bounds: {:.4f}".format(fov_bounds))

	# Convert camera state data 
	DCM = camera.state.attitude.toDCM()
	los = DCM@array([0,0,1])
	pos = camera.state.position
	los = (los/norm(los))
	debug("Line of Sight: {}".format(los))
	
	# Calculate offnadir angle
	unity_pos = (pos/norm(pos)).reshape(3,)
	offnadir = arccos(dot(unity_pos,-los))
	debug("NADIR Angle = {}".format(rad2deg(offnadir)))
	if offnadir < OFFNADIR_THRESH:
		info("NADIR Angle within tolerance, aborted GKM")
		return camera

	# Calculate Line of sights to Moon segments
	diff = xyzs-pos.reshape(3,)
	moon_los = diff/norm(diff,axis=2).reshape(ra_sections,decl_sections,1)

	# Determine what "blob" of the Moon surface can be seen by the camera
	nabla = dot(-moon_los,pos)**2-(norm(pos)**2-RADIUS**2)
	min_dist = abs(-dot(-moon_los,pos)+sqrt(nabla))
	angles = np.where((min_dist+TOL).reshape(360,180)>=norm(diff,axis=2),np.dot(moon_los,los),-1)
	blob_target = np.where(angles>fov_bounds,norm(diff,axis=2),-1)

	# Finding the center of the blob
	blob_xyzs = np.where(blob_target.reshape(360,180,1)>-1,xyzs,array([0,0,0]))
	blob_mask = np.array(np.where(norm(blob_xyzs,axis=2)>0))

	pts_xyzs = blob_xyzs[blob_mask[0,:],blob_mask[1,:],:]
	if len(pts_xyzs) == 0:
		# Typically not good, no Moon found in sight
		warning("No Moon in View")
		return camera
	
	ctr_xyz = np.average(pts_xyzs,axis=0)
	ctr_los = ctr_xyz/norm(ctr_xyz)
	decl = arcsin(ctr_los[2])
	if decl > np.pi/2:
		decl -= np.pi
	ra = arccos(ctr_los[0]/cos(decl))
	debug("GKM CAMERA LOCATION = {} N, {} E".format(rad2deg(ra),rad2deg(decl)))

	# Finding the furthest extremities
	pos2 = ctr_los*RADIUS*1.2
	los2 = -ctr_los
	blob_prev = 0
	blob = get_coverage(pos2,los2,xyzs,min([camera.FOV_x,camera.FOV_y]))
	cont = len(np.where(blob_target>blob)[0])
	while cont > 0 and np.sum(blob) != np.sum(blob_prev):
		blob_prev = blob
		pos2*=1.2
		blob = get_coverage(pos2,los2,xyzs,min([camera.FOV_x,camera.FOV_y]))
		cont = len(np.where(blob_target>blob)[0])
	if np.sum(blob) == np.sum(blob_prev):
		warning("GK Method reached Maximum View without covering Target Area")

	# Build the GKM camera state
	global_z = los2
	global_x = array([-sin(ra),cos(ra),0])
	global_y = mu.rot_about(global_z,global_x,np.pi/2)
	local_z = array([0,0,1])
	local_x = array([1,0,0])
	local_y = array([0,-1,0])
	dcm = mu.wahbas_problem(array([global_z,global_x,global_y]),
												array([local_z,local_x,local_y]))
	
	# Convert to Quaternion and assign to camera
	quat = Quaternion()
	quat.fromDCM(dcm)
	camera.set_state(State(pos2,quat))

	return camera


def get_coverage(pos,los,moon_xyzs,fov):
	"""
		Determine how much of the moon can be seen with the current camera state
	"""
	shape = array(moon_xyzs.shape)
	shape[2] = 1
	diff = moon_xyzs-pos
	fov_bounds = cos(fov/2)
	max_dist = sqrt(norm(pos)**2+RADIUS**2)
	moon_los = diff/norm(diff,axis=2).reshape(shape)
	angles = np.where(norm(diff,axis=2)<=max_dist,np.dot(moon_los,los),-1)
	blob = np.where(angles>fov_bounds,norm(diff,axis=2),-1)
	return blob
