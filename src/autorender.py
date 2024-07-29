import os
from os.path import join,abspath,dirname,basename,exists
import sys
import bpy
import numpy as np
from numpy import pi,arccos,deg2rad,rad2deg,array,arctan2,arcsin
from numpy.linalg import norm
import time
import mathutils as mu
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# Local imports
from Structures import Quaternion,State
from Camera import Camera,get_camera
from metadata import create_metadata,camera2config


def startRender():
	global isRendering
	isRendering = True


def endRender(a,b):
	global isRendering
	isRendering = False


def render(camera,sun_state,earth_state,config,name):
	global isRendering
	outdir = config["OUTDIR"]
	if not os.path.exists(outdir):
		os.makedirs(outdir)
	scene = setup(camera,config)
	if scene is None:
		return 2
	sun = bpy.data.objects["Light"]
	cam = scene.camera
	cam.rotation_mode = 'QUATERNION'
	moveObject(cam,camera.state)
	moveSunObject(sun,[0,0,0],sun_state)
	filename =  os.path.join(outdir,name)
	scene.render.image_settings.color_mode = config["color_mode"]
	scene.render.image_settings.color_depth = str(config["color_depth"])
	scene.render.image_settings.file_format = config["file_ext"]
	scene.render.filepath = filename
	if exists(filename) and int(config["re_render"])==0: # Don't re-render rendered image
		print("File: {} already exists, skipping...".format(basename(filename)))
		return 1
	startRender()
	bpy.ops.render.render("INVOKE_DEFAULT",write_still=True)
	return 0
	

def setup(camera,config):
	"""
	Taking care of all of the boring setup stuff
	"""
	# Remove the CUBE
	if "Cube" in bpy.data.objects:
		cube = bpy.data.objects["Cube"]
		bpy.data.objects.remove(cube)

	# Check for camera existence, if not existant, add one
	if not "Camera" in bpy.data.objects:
		print("No Camera, Adding Camera")
		bpy.ops.object.camera_add()
	cam = bpy.data.objects["Camera"]
	scene = bpy.data.scenes["Scene"]
	scene.camera = cam
	# Config Camera
	cam.data.lens_unit = "FOV"
	cam.data.angle = camera.FOV_x
	cam.data.clip_end = np.inf
	cam.data.sensor_fit = "HORIZONTAL"
	#cam.data.dof.use_dof = True
	cam.data.dof.focus_distance = norm(camera.state.position)
	cam.data.dof.aperture_blades = camera.NumBlades
	cam.data.dof.aperture_fstop = camera.F_Stop
	scene.render.resolution_x = camera.Ncols
	scene.render.resolution_y = camera.Nrows
	scene.view_settings.exposure = -8 # EV, testing

	# Config Moon Material
	if not "MoonRocks" in bpy.data.materials:
		print("Cannot find Moon Material")
		return None
	moon_mat = bpy.data.materials["MoonRocks"]
	nodes = moon_mat.node_tree.nodes
	principled_bsdf = nodes.get("Principled BSDF")
	principled_bsdf.inputs.get("Roughness").default_value = float(config["moon"]["roughness"])
	principled_bsdf.inputs.get("Metallic").default_value = float(config["moon"]["metallic"])
	principled_bsdf.inputs.get("IOR").default_value = float(config["moon"]["ior"])
	principled_bsdf.inputs.get("Coat Weight").default_value = 0
	principled_bsdf.inputs.get("Sheen Weight").default_value = 0
	principled_bsdf.inputs.get("Emission Strength").default_value = 0
	principled_bsdf.distribution = "MULTI_GGX" # Added for testing
	contrast_node = nodes.get("Brightness/Contrast")
	if contrast_node is None:
		print("No Contrast Node Found")
	else:
		contrast_node.inputs.get("Bright").default_value = float(config["moon"]["bright"])
		contrast_node.inputs.get("Contrast").default_value = float(config["moon"]["contrast"])

	# Config Sun
	if "Light" in bpy.data.objects:
		light = bpy.data.objects["Light"]
		bpy.data.objects.remove(light)
	view_layer = bpy.context.view_layer
	# Create new light datablock.
	sun_data = bpy.data.lights.new(name="Light", type='SUN')
	# Create new object with our light datablock.
	sun = bpy.data.objects.new(name="Light", object_data=sun_data)
	view_layer.active_layer_collection.collection.objects.link(sun)
	# And finally select it and make it active.
	sun.select_set(True)
	view_layer.objects.active = sun

	sun.data.energy = float(config["sun"]["energy"])
	sun.data.color = array(config["sun"]["color"],dtype=np.float32)
	sun.data.angle = float(config["sun"]["angle"])
	sun.data.use_contact_shadow = True
	sun.data.shadow_trace_distance = np.inf
	sun.data.shadow_cascade_max_distance = np.inf
	sun.rotation_mode = "YXZ"

	# Configure Background
	bg = scene.world.node_tree.nodes["Background"]
	image = bpy.data.images.load("../maps/hipp8.tif")
	sky_texture_node = scene.world.node_tree.nodes.new(type="ShaderNodeTexImage")
	sky_texture_node.image = image
	sky_texture_node.projection = "SPHERE"
	scene.world.node_tree.links.new(sky_texture_node.outputs["Color"], bg.inputs["Color"])
	scene.world.use_nodes = True

	# Config Rendering
	bpy.app.handlers.render_post.append(endRender)
	scene.render.engine = "CYCLES"
	scene.render.threads_mode = config["threads_mode"]
	scene.render.use_persistent_data = True
	scene.render.threads = int(config["threads"])
	scene.cycles.device = config["device"]
	scene.cycles.samples = int(config["samples"])
	scene.cycles.use_denoising = True

	return scene


def moveObject(obj,state):
	dcm = state.attitude.toDCM()
	# Offset is used to account for blenders atrocious starting quaternion
	offset = np.array([[1,0,0],
										[0,-1,0],
										[0,0,-1]])
	cam_quat = Quaternion()
	cam_quat.fromDCM(offset@dcm)
	obj.rotation_quaternion = mu.Quaternion(cam_quat.toArray())
	#obj.rotation_quaternion = mu.Quaternion(state.attitude.toArray())
	#print(obj.rotation_quaternion)
	obj.location.x = state.position[0]
	obj.location.y = state.position[1]
	obj.location.z = state.position[2]
	return


def moveSunObject(obj, pos, angles):
	# Position in km, angles in radians
	obj.rotation_euler[0] = angles[0]
	obj.rotation_euler[1] = angles[1]
	obj.rotation_euler[2] = angles[2]

	obj.location.x = pos[0]
	obj.location.y = pos[1]
	obj.location.z = pos[2]
	return


def load_config(filename,old_config=None):
	new_config = {}
	if not exists(filename):
		print("Config: {} Not Found...".format(filename))
	with open(filename,"r") as f:
		new_config = json.load(f)
	if old_config is not None:
		for key in new_config:
			old_config[key] = new_config[key]
		return old_config
	return new_config


# Globals
isRendering = False


if __name__ == "__main__":
	RADIUS = 1737400
	BASE_PATH = dirname(dirname(abspath(__file__)))
	CONFIG_PATH = join(BASE_PATH,"configs")
	default_config = "blender.conf"
	config = load_config(join(CONFIG_PATH,default_config))
	start = False
	for i,arg in enumerate(sys.argv):
		if arg == basename(__file__):
			start = True
		elif start:
			print("Loading config {}: {}...".format(i,arg))
			print(join(CONFIG_PATH,arg))
			config = load_config(join(CONFIG_PATH,arg),old_config=config)
	
	quatWorldtoCam = Quaternion()
	quatWorldtoCam.fromDCM(array([[0,0,1],
																[-1,0,0],
																[0,-1,0]]))
	if "CAMERA" not in config:
		print("ERROR: Camera not specified, exiting...")
		exit(0)
	camera = get_camera(join(CONFIG_PATH,"cameras",config["CAMERA"]))
	config = camera2config(camera,old_config=config)
	print(np.rad2deg(camera.FOV_x),np.rad2deg(camera.FOV_y))
	quat = Quaternion()
	for i,state_data in enumerate(config["STATES"]):
		if "NAME" in state_data:
			name = state_data["NAME"]
		else:
			print("ERROR: No Image Name Specified, Skipping")
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
				print("ERROR: SC has no attitude data, Skipping...")
				continue
			pos = array(sc_data["POS"])
			quat.fromDCM(dcm)
		elif "CAM" in state_data:
			# Boresight aligned with Z axis, X is right
			cam_data = state_data["CAM"]
			if "QUAT" in cam_data:
				quat = Quaternion(-float(cam_data["QUAT"]["s"]),array(cam_data["QUAT"]["v"]))
			elif "DCM" in cam_data:
				dcm = array(cam_data["DCM"],dtype=np.float32)
				quat.fromDCM(dcm)
			else:
				print("ERROR: Cam has no attitude data, Skipping...")
				continue
			pos = array(cam_data["POS"])
		else:
			print("ERROR: Camera Not Found, Skipping...")
			continue
		camera.set_state(State(pos,quat))
		if "SUN" in state_data:
			sun_los = array(state_data["SUN"],dtype=np.float32)
			sun_los /= norm(sun_los)
			sun_ra = arctan2(sun_los[1],sun_los[0])
			sun_decl = arcsin(sun_los[2])
			print("RA: {}, Decl: {}".format(sun_ra,sun_decl))
			sun_state = array([pi/2+sun_decl,0,sun_ra-pi/2])
		else:
			print("ERROR: Sun Not Found, Skipping...")
			continue
		if "EARTH" in state_data:
			earth_data = state_data["EARTH"]
			# TODO: Add Earth Stuff
			earth_state = None
		else:
			earth_state = None
		if render(camera,sun_state,earth_state,config,name) == 0:
			create_metadata(config,i)
		while isRendering is True:
			time.sleep(0.1)

	exit(0)
