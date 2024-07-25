import numpy as np
from numpy import arccos,arcsin,deg2rad,rad2deg,cos,sin,pi,arctan2
from numpy import array,zeros,ones,cross,dot,sum,sqrt,fmin,fmax
from numpy.linalg import norm
import subprocess as sp
import json
import os
from os.path import join,exists,dirname,abspath
from mathutil import wahbas_problem,angle_betw_los,rand_norm3
from Structures import Quaternion,State
from Camera import get_camera
from blender_prep import find_mesh
from blender_test_redux import build_mesh
from file_io import load_config


MOON_RADIUS = 1737400 # m


def get_state(config):
	quatWorldtoCam = Quaternion()
	quatWorldtoCam.fromDCM(array([[0,0,1],
																[-1,0,0],
																[0,-1,0]]))
	if not "STATES" in config:
		# No states found
		print("ERROR: STATES not found")
		return None
	states_data = config["STATES"]
	if len(states_data) > 1:
		# Too many states
		print("ERROR: Too many states found")
		return None
	if len(states_data) == 0:
		# No states found
		print("ERROR: No states found")
		return None
	state_data = states_data[0]
	if "SC" in state_data:
		# Boresight aligned with X axis, Z is up
		sc_data = state_data["SC"]
		if "QUAT" in sc_data:
			sc_quat = Quaternion(float(sc_data["QUAT"]["s"]),array(sc_data["QUAT"]["v"]))
			dcm = quatWorldtoCam.toDCM().T@sc_quat.toDCM()
		elif "DCM" in sc_data:
			sc_dcm = array(sc_data["DCM"],dtype=np.float32)
			dcm = quatWorldtoCam.toDCM()@sc_dcm
		else:
			print("ERROR: SC has no attitude data")
			return None
		pos = array(sc_data["POS"])
		quat.fromDCM(dcm)
	elif "CAM" in state_data:
		# Boresight aligned with Z axis, X is right
		cam_data = state_data["CAM"]
		if "QUAT" in cam_data:
			quat = Quaternion(float(cam_data["QUAT"]["s"]),array(cam_data["QUAT"]["v"]))
		elif "DCM" in cam_data:
			dcm = array(cam_data["DCM"],dtype=np.float32)
			quat.fromDCM(dcm)
		else:
			print("ERROR: Cam has no attitude data")
			return None
		pos = array(cam_data["POS"])
	else:
		print("ERROR: Camera Not Found")
		return None
	return State(pos,quat)



if __name__ == "__main__":

	# Configs
	base_dir = dirname(__file__)
	blend_file = "../blends/oneshot.blend"
	albedo_map = "../maps/lroc_color_poles.tif"
	config_dir = "../configs"
	config = "parth2.conf"
	use_grassyknoll = True
	# End configs

	data = load_config(join(config_dir,config))
	if not "CAMERA" in data:
		print("Camera not found, exiting...")
		exit()
	else:
		print("Camera Loaded!")
	camera_file = data["CAMERA"]
	camera = get_camera(join(base_dir,"../configs/cameras",camera_file))
	state = get_state(data)
	if state is None:
		print("State not found, exiting...")
		exit()
	camera.set_state(state)
	mesh,tris,colors = find_mesh(camera,gk=use_grassyknoll)
	print("Mesh is of size: {}".format(mesh.shape))
	build_mesh(mesh,tris,colors,albedo_map,blend_file)
	print("Sent to the Renderer")
	sp.run(["blender","-b",blend_file,"-P","autorender.py",config])
