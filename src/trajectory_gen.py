# Library Imports
import numpy as np
import pickle
import os
from os.path import join,exists,isfile
import subprocess as sp

# Local Imports
from Log import critical,warning,info,debug
from Camera import get_camera
from Render import Render
import file_io as io
from find_mesh import find_mesh
from build_mesh import build_mesh
from paths import TMP_DIR,MAP_DIR,SRC_DIR
from Structures import State
from gkmethod import gkmethod
import pose_combiner as pc



def print_config(args):
	info("CONFIGURATION")
	info("Job Name: {}".format(args.job))
	info("Job Type: Trajectory")
	info("Input File: {}".format(args.filename))
	info("Output Dir: {}".format(args.outdir))
	info("Camera: {}".format(args.camera))
	info("Blender Config: {}".format(args.blender))
	info("GKM {}abled".format(["En","Dis"][args.disable_gkm]))
	info("[Log File, Level, Overwrite]: [{}, {}, {}]".format(args.logging,
																													args.log_level,
																													args.fo))
	return


def run(args,poses):
	"""
	
	"""
	# Unpack required args
	BLENDER_CONF_FILE = args.blender
	CAMERA_CONF_FILE = args.camera
	IMG_LOC = join(args.outdir,args.job)
	BLEND_FILE = "{}.blend".format(join(TMP_DIR,args.job))
	ALLOW_GK = not args.disable_gkm
	PICKLE_FILE = join(TMP_DIR,"{}.pkl".format(args.job))

	# Create Camera
	camera = get_camera(CAMERA_CONF_FILE)

	# Load blender configs
	configs = io.load_config(BLENDER_CONF_FILE)

	# Add img dir to configs
	configs["outdir"] = IMG_LOC

	# Check out the desired maps
	if "albedo_map" not in configs["moon"]:
		critical("\"moon/albedo_map\" not in Blender config file, exiting...")
		return 1
	if "albedo_map" not in configs["earth"]:
		critical("\"earth/albedo_map\" not in Blender config file, exiting...")
		return 2
	if "star_map" not in configs:
		critical("\"star_map\" not in Blender config file, exiting...")
		return 3
	MOON_ALBEDO_MAP = join(MAP_DIR,configs["moon"]["albedo_map"])
	if not (exists(MOON_ALBEDO_MAP) and isfile(MOON_ALBEDO_MAP)):
		critical("Moon albedo_map: {} not found, exiting...".format(MOON_ALBEDO_MAP))
		return 4
	EARTH_ALBEDO_MAP = join(MAP_DIR,configs["earth"]["albedo_map"])
	if not (exists(EARTH_ALBEDO_MAP) and isfile(EARTH_ALBEDO_MAP)):
		critical("Earth albedo_map: {} not found, exiting...".format(EARTH_ALBEDO_MAP))
		return 5
	STAR_MAP = join(MAP_DIR,configs["star_map"])
	if not (exists(STAR_MAP) and isfile(STAR_MAP)):
		critical("Star map: {} not found, exiting...".format(STAR_MAP))
		return 6

	# Create Render Objects
	renders = create_render_objs(poses,camera,configs,ALLOW_GK,True)

	info("Created {} Render Objects".format(len(renders)))

	#return 0

	for i,render in enumerate(renders):
		# Pass data to blender code via pickle file
		with open(PICKLE_FILE,"wb+") as f:
			pickle.dump(render,f,protocol=pickle.HIGHEST_PROTOCOL)

		# Set the camera to render the mesh
		if render.mesh_state is None:
			# Get Blender to render the scene
			info("Sent Render {}/{} to be rendered".format(i,len(renders)))
			complete_proc = sp.run(["blender","-P",join(SRC_DIR,"Render.py"),PICKLE_FILE],capture_output=False,stdout=sp.DEVNULL)

			# Check for success
			if complete_proc.returncode != 0:
				critical("Render #{} failed with error code {}\n\tPickle and Blender files have been left for inspection".format(i,complete_proc.returncode))
				return 3
			else:
				info("Render #{} Completed".format(i))
				os.remove(PICKLE_FILE)

		else:
			camera.set_state(render.mesh_state)

			# Find and build the mesh
			debug("Camera Position is: {}".format(camera.state.position))
			debug("Camera Attitude is: {}".format(camera.state.attitude))
			mesh,tris,colors = find_mesh(camera)
			build_mesh(mesh,tris,colors,BLEND_FILE)

			# Get Blender to render the scene
			info("Sent Render {}/{} to be rendered".format(i+1,len(renders)))
			complete_proc = sp.run(["blender","-b",BLEND_FILE,"-P",join(SRC_DIR,"Render.py"),PICKLE_FILE],capture_output=False,stdout=sp.DEVNULL)

			# Check for success
			if complete_proc.returncode != 0:
				critical("Render #{} failed with error code {}\n\tPickle and Blender files have been left for inspection".format(i,complete_proc.returncode))
				return 3
			else:
				info("Render #{} Completed".format(i))
				os.remove(PICKLE_FILE)
				os.remove(BLEND_FILE)
	return 0


def create_render_objs(poses,camera,configs,allow_gk,allow_combine):
	"""
		Find method for creating render objects from poses
	"""
	# Starting with the naive method
	renders = []
	if allow_combine:
		combined_poses,mesh_cameras = pc.combine_poses(poses,camera)
		for i,pose_set in enumerate(combined_poses):
			mesh_cam_state = None
			if mesh_cameras[i] is not None:
				mesh_cam_state = mesh_cameras[i].state
			renders.append(Render(camera,pose_set,mesh_cam_state,configs))
	else:
		for pose in poses:
			mesh_cam_state = pose.cam_state
			if allow_gk:
				camera.set_state(pose.cam_state)
				mesh_cam_state = gkmethod(camera)
				if mesh_cam_state is None:
					continue # Don't render non-Moon images
				mesh_cam_state = mesh_cam_state.state
			render = Render(camera,[pose],mesh_cam_state,configs)
			renders.append(render)
	return renders
