# Generate a bunch of random images
import numpy as np
from numpy import arccos,arcsin,deg2rad,rad2deg,cos,sin,pi,arctan2
from numpy import array,zeros,ones,cross,dot,sum,sqrt,fmin,fmax
from numpy.linalg import norm
import subprocess as sp
import json
import os
from os.path import join,exists,dirname,abspath
from mathutil import wahbas_problem,angle_betw_los
from Structures import Quaternion,State
from Camera import get_camera
from blender_prep import find_mesh
from blender_test_redux import build_mesh


MOON_RADIUS = 1737400 # m


def rand_norm3():
	v = np.random.uniform(-1,1,(3,1))
	return v/norm(v)


def random_state(rad_range,lat_range=[-pi/2,pi/2],lon_range=[0,2*pi]):
	"""
		Moving fast and breaking things. This code should be heavily revised.
	"""
	found = False
	while not found:
		v = rand_norm3()
		los = -v
		lat = arcsin(v[2])
		lon = arctan2(v[1],v[0])
		if not (lat>=lat_range[0] and lat<=lat_range[1]):
			continue
		if not (lon>=lon_range[0] and lon<=lon_range[1]):
			continue
		r = rad_range[0]*(np.random.random()*(rad_range[1]/rad_range[0]-1) + 1)
		pos = v*r
		found = True
		print("Found Position!")
	# Position has been found, now need attitude
	theta_max = arcsin(MOON_RADIUS/(r))
	print("Theta_Max is: {}".format(theta_max))
	found = False
	while not found:
		l = rand_norm3()
		theta = angle_betw_los(los,l)
		if theta<theta_max:
			found = True
			los = l
			print("Found LoS!")
	# Position and LoS have been found
	# Now for DCM from LoS
	Cam_Z = los.reshape(3)
	interlock = 0
	# Why yes, I do hate myself
	## But I love Wahba, so it cancels out
	while interlock < .1 or interlock > pi-.1:
		Cam_Helper = rand_norm3()
		interlock = angle_betw_los(Cam_Z,Cam_Helper)
		print("Interlock is: {}".format(interlock))
	Cam_Helper = Cam_Helper.reshape(3)
	Cam_X = cross(Cam_Helper,Cam_Z)
	Cam_Y = cross(Cam_Z,Cam_X)
	Z = array([0,0,1])
	X = array([1,0,0])
	Y = array([0,1,0])
	DCM = wahbas_problem(array([X,Y,Z]),array([Cam_X,Cam_Y,Cam_Z])).T
	quat = Quaternion()
	quat.fromDCM(DCM)
	state = State(pos,quat)
	return state, los, theta


def get_intersection(pos,los):
	nabla = dot(los,pos)**2-(sum(pos**2-MOON_RADIUS**2))
	if nabla < 0:
		return None
	d = fmin(-dot(los,pos)-sqrt(nabla),-dot(los,pos)+sqrt(nabla))
	return pos + (los*d)


if __name__ == "__main__":

	# Configs
	n_mesh = 100
	n_sun = 10
	min_sun_angle = deg2rad(-5)
	max_csi = pi
	blend_file = "../blends/mass.blend"
	albedo_map = "../maps/lroc_color_poles.tif"
	camera_file = "testcam.json"
	outdir = "../outimages/batch/"
	interactive = False # Are you gonna sit there and watch it?
	# End configs

	camera = get_camera("../configs/cameras/{}".format(camera_file))
	for i in range(3,n_mesh):
		filename = "../configs/batch_{}.json".format(i)
		state, los, offnadir = random_state([MOON_RADIUS+1500000,3*MOON_RADIUS])
		print("STATE:\nPosition = {}\nAttitude = {}\nLoS = {}\nOffNadir = {}".format(state.position,state.attitude,los,offnadir))
		camera.set_state(state)
		intersection = get_intersection(state.position.reshape(3),los.reshape(3))
		if intersection is None:
			print("Bad Moon_Intersection")
			continue
		moon2int = intersection/norm(intersection)
		print("MOON2INT = {}".format(moon2int))
		j = 0
		render_data = {}
		render_data["CAMERA"] = camera_file
		render_data["OUTDIR"] = join(outdir,"{:03d}".format(i))
		render_data["STATES"] = []
		while j < n_sun:
			sun_los = rand_norm3()
			moon_sun_interlock = angle_betw_los(moon2int,sun_los)
			cam_sun_interlock = angle_betw_los(los,sun_los)
			if moon_sun_interlock < pi/2+min_sun_angle or cam_sun_interlock > max_csi:
				continue
			print("CAM LoS: {}, SUN LoS: {}, Interlock: {}".format(los.T,sun_los.T,cam_sun_interlock))
			data = {}
			data["NAME"] = "image_{}".format(j)
			data["TIME"] = "The Year 3000"
			data["CAM"] = {}
			data["CAM"]["POS"] = camera.state.position.reshape(3).tolist()
			data["CAM"]["LOS"] = los.reshape(3).tolist()
			data["CAM"]["OFFNADIR"] = offnadir
			data["CAM"]["QUAT"] = {}
			data["CAM"]["QUAT"]["s"] = camera.state.attitude.s
			data["CAM"]["QUAT"]["v"] = camera.state.attitude.v.reshape(3).tolist()
			data["CAM"]["SUN_INTERLOCK"] = angle_betw_los(los,sun_los)
			data["SUN"] = sun_los.reshape(3).tolist()
			render_data["STATES"].append(data)
			j += 1
		with open(filename,"w+") as f:
			json.dump(render_data,f,indent=2)
		if not os.path.exists(render_data["OUTDIR"]):
			os.makedirs(render_data["OUTDIR"])
		mesh,tris,colors = find_mesh(camera)
		print("Mesh is of size: {}".format(mesh.shape))
		build_mesh(mesh,tris,colors,albedo_map,blend_file,interactive=interactive)
		print("Sent to the Renderer")
		sp.run(["blender","-b",blend_file,"-P","autorender.py",filename])
