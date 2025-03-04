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
	xyzs = generate_moon_map(ra_sections=ra_sections,decl_sections=decl_sections)

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
	offnadir = arccos(min(1,max(dot(unity_pos,-los),-1)))
	debug("NADIR Angle = {}".format(rad2deg(offnadir)))
	if offnadir < OFFNADIR_THRESH:
		info("NADIR Angle within tolerance, aborted GKM")
		return camera

	blob_target = get_coverage(pos,los,sqrt(camera.FOV_x**2+camera.FOV_y**2))
	
	# Get camera pose from coverage blob
	camera = get_camera_from_coverage(blob_target,camera)

	return camera


def get_coverage(pos,los,fov,ra=360):
	"""
		Determine how much of the moon can be seen with the current camera state
	"""
	moon_xyzs = generate_moon_map(ra_sections=ra,decl_sections=ra//2)
	shape = array(moon_xyzs.shape)
	#info("Shape is: {}".format(shape))
	shape[2] = 1
	diff = moon_xyzs-pos
	fov_bounds = cos(fov/2)
	max_dist = sqrt(norm(pos)**2+RADIUS**2)
	moon_los = diff/norm(diff,axis=2).reshape(shape)
	angles = np.where(norm(diff,axis=2)<=max_dist,np.dot(moon_los,los),0)
	blob = np.where(angles>fov_bounds,norm(diff,axis=2),0)
	return blob


def get_coverage_from_state(state,fov,ra=360):
	"""
		Determine how much of the Moon can be seen with the current camera pose
	"""
	position = state.position
	los = state.attitude.toDCM()@np.array([0,0,1])
	#print("Pos,Los = {},{}".format(position,los))
	return get_coverage(position,los,fov,ra)


def get_camera_from_coverage(coverage,camera):
	"""
		Generate a NADIR-pointing state for a moon map
	"""
	ra_sec,decl_sec = coverage.shape
	#info("Coverage shape: {},{}".format(ra,decl))
	# Generate Moon coords again
	xyzs = generate_moon_map(ra_sections=ra_sec,decl_sections=decl_sec)

	# Finding the center of the coverage
	cov_xyzs = np.where(coverage.reshape(360,180,1)>0,xyzs,array([0,0,0]))
	cov_mask = np.array(np.where(norm(cov_xyzs,axis=2)>0))

	pts_xyzs = cov_xyzs[cov_mask[0,:],cov_mask[1,:],:]
	if len(pts_xyzs) == 0:
		# Typically not good, no Moon found in sight
		warning("No Moon in View")
		return None

	ctr_xyz = np.average(pts_xyzs,axis=0)
	ctr_los = ctr_xyz/norm(ctr_xyz)
	#info("CTR_XYZ: {}".format(ctr_xyz))
	decl = arcsin(ctr_los[2])
	if decl > np.pi/2:
		decl -= np.pi
		ra -= np.pi
	ra = arccos(ctr_los[0]/cos(decl))
	#debug("GKM CAMERA LOCATION = {} N, {} E".format(rad2deg(decl),rad2deg(ra)))

	# Finding the furthest extremities
	pos = ctr_los*RADIUS*1.2
	los = -ctr_los
	blob_prev = 0
	blob = get_coverage(pos,los,min([camera.FOV_x,camera.FOV_y]),ra=ra_sec)
	#info("Blob shape: {}".format(blob.shape))
	cont = len(np.where(coverage>blob)[0])
	count = 0
	while cont > 0 and count < 5:
		blob_prev = blob
		pos*=1.2
		blob = get_coverage(pos,los,min([camera.FOV_x,camera.FOV_y]),ra=ra_sec)
		#info("Blob shape: {}".format(blob.shape))
		cont = len(np.where(coverage>blob)[0])
		if np.sum(blob) != np.sum(blob_prev):
			count += 1
		else:
			count = 0
	if np.sum(blob) == np.sum(blob_prev):
		warning("GK Method reached Maximum View without covering Target Area")
	
	debug("GKM CAMERA LOCATION = {}".format(pos))
	# Build the GKM camera state
	global_z = los
	global_x = array([-sin(ra),cos(ra),0])
	global_y = mu.rot_about(global_z,global_x,np.pi/2)
	local_z = array([0,0,1])
	local_x = array([1,0,0])
	local_y = array([0,-1,0])
	dcm = mu.wahbas_problem(array([global_z,global_x,global_y]),
												array([local_z,local_x,local_y]))
	
	# Convert to Quaternion and assign to camera
	quat = Quaternion()
	quat.fromDCM(dcm.T)
	debug("GKM CAMERA QUAT = {}".format(quat))
	camera.set_state(State(pos,quat))

	return camera


def generate_moon_map(ra_sections=360,decl_sections=180):
	# Let's build a Moon model
	ra_sections = int(ra_sections)
	decl_sections = int(decl_sections)

	#info("RA,Decl = {},{}".format(ra_sections,decl_sections))

	# Create arrays of ra and decl values
	ra = np.linspace(0,2*np.pi,ra_sections,endpoint=False)
	ras = np.tile(ra,decl_sections).reshape(decl_sections,ra_sections)
	decl = np.linspace(-np.pi/2,np.pi/2,decl_sections)
	decls = np.repeat(decl,ra_sections).reshape(decl_sections,ra_sections)

	# Convert ra and decls to xyz coords
	xyzs = array([RADIUS*cos(decls)*cos(ras),RADIUS*cos(decls)*sin(ras),RADIUS*sin(decls)]).transpose((2,1,0))
	return xyzs


if __name__ == "__main__":
	# Quick checks
	quat = Quaternion()
	quat.fromArray(np.array([0.50000,0.50000,0.50000,-0.50000]))
	state = State(position=np.array([3237400,0,0]),attitude=quat)
	moon_map = generate_moon_map(ra_sections=20,decl_sections=10)
	fov = np.deg2rad(20)
	get_coverage_from_state(state,fov)
