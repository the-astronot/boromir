# Library Imports
import numpy as np
import pickle
import os
from os.path import join,exists,isfile
import subprocess as sp

# Local Imports
from Log import log,error
from Camera import get_camera
from Render import Render
import file_io as io
from find_mesh import find_mesh
from build_mesh import build_mesh
from paths import TMP_DIR,MAP_DIR,SRC_DIR
from Structures import State
from gkmethod import gkmethod



def print_config(args):
	log("CONFIGURATION",0)
	log("Job Name: {}".format(args.job),0)
	log("Job Type: Trajectory",0)
	log("Input File: {}".format(args.filename),0)
	log("Output Dir: {}".format(args.outdir),0)
	log("Camera: {}".format(args.camera),0)
	log("Blender Config: {}".format(args.blender),0)
	log("GKM {}abled".format(["En","Dis"][args.disable_gkm]),0)
	log("[Log File, Level, Overwrite]: [{}, {}, {}]".format(args.logging,
																													args.log_level,
																													args.fo),
																													0)
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
	error("ImgLoc is {}".format(IMG_LOC))

	# Create Camera
	camera = get_camera(CAMERA_CONF_FILE)
	error("Loaded Camera")

	# Load blender configs
	configs = io.load_config(BLENDER_CONF_FILE)
	configs["outdir"] = IMG_LOC
	if "albedo_map" not in configs:
		error("\"albedo_map\" not in Blender config file, exiting...")
		return 1
	ALBEDO_MAP = join(MAP_DIR,configs["albedo_map"])
	if not (exists(ALBEDO_MAP) and isfile(ALBEDO_MAP)):
		error("File albedo_map: {} not found, exiting...".format(ALBEDO_MAP))

	# Create Render Objects
	renders = create_render_objs(poses,camera,configs,ALLOW_GK)
	error("Renders created")

	for i,render in enumerate(renders):
		# Pickle the render objects
		pickle_file = join(IMG_LOC,"{:05d}.pkl".format(i))
		#if exists(IMG_LOC) and render.configs["re_render"] == 0:
		#	log("{} already exists, skipping...".format(IMG_LOC),0)
		#	continue
		with open(pickle_file,"wb+") as f:
			pickle.dump(render,f,protocol=pickle.HIGHEST_PROTOCOL)
		# Set the camera to render the mesh
		camera.set_state(render.mesh_state)
		# Find and build the mesh
		mesh,tris,colors = find_mesh(camera)
		build_mesh(mesh,tris,colors,ALBEDO_MAP,BLEND_FILE)
		# Get Blender to render the scene
		log("Sent Render {}/{} to be rendered".format(i,len(renders)),2)
		sp.run(["blender","-b",BLEND_FILE,"-P",join(SRC_DIR,"Render.py"),pickle_file])
		os.remove(pickle_file)
		os.remove(BLEND_FILE)
	return 0


def create_render_objs(poses,camera,configs,allow_gk):
	"""
		Find method for creating render objects from poses
	"""
	# Starting with the naive method
	renders = []
	for pose in poses:
		mesh_cam_state = pose.cam_state
		if allow_gk:
			camera.set_state(pose.cam_state)
			mesh_cam_state = gkmethod(camera)
			if mesh_cam_state is None:
				continue
			mesh_cam_state = mesh_cam_state.state
		render = Render(camera,[pose],mesh_cam_state,configs)
		renders.append(render)
	return renders
