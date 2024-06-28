import os
from os.path import join,abspath,dirname
import sys
import bpy
import numpy as np
from numpy import pi,cos,sin,arccos,arcsin,arctan,deg2rad,rad2deg,array
import time
import mathutils as mu
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# Local imports
from Structures import Quaternion,State
from Camera import Camera,get_camera


def startRender():
	global isRendering
	isRendering = True


def endRender(a,b):
	global isRendering
	isRendering = False


def render(camera,pos,sun_angles,config,outdir):
	global isRendering
	if not os.path.exists(outdir):
		os.makedirs(outdir)
	scene = setup(camera,config)
	if scene is None:
		return
	# Lets try for a quick set of images
	sun = bpy.data.objects["Light"]
	cam = scene.camera
	cam.rotation_mode = 'QUATERNION'
	moveObject(cam,camera.state)
	dcm = state.attitude.toDCM()
	for sa in sun_angles:
		sunAngleXYZ = [90,0,90+pos[0][1]-(90-sa)]
		print(sunAngleXYZ)
		moveSunObject(sun,[0,0,0],sunAngleXYZ)
		filename =  os.path.join(outdir,"{:.0f}X_{:.0f}Y_{:.0f}Z_sa{:.0f}_dcm{}".format(camera.state.position[0],camera.state.position[1],camera.state.position[2],sa,str(dcm).replace("\n","")))
		scene.render.filepath = filename
		if os.path.exists(filename): # Don't re-render rendered image
			print("File: {} already exists, skipping...".format(os.basename(filename)))
			continue
		startRender()
		bpy.ops.render.render("INVOKE_DEFAULT",write_still=True)
		while isRendering is True:
			time.sleep(0.1)
		print("Finished Rendering Image!")
	return
	

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
	cam.data.angle = np.max([camera.FOV_x,camera.FOV_y])
	cam.data.clip_end = np.inf
	cam.data.sensor_fit = "AUTO"
	#cam.data.dof.use_dof = True
	cam.data.dof.focus_distance = np.inf
	cam.data.dof.aperture_blades = camera.NumBlades
	cam.data.dof.aperture_fstop = camera.F_Stop
	cam.data.clip_end = np.inf
	scene.render.resolution_x = camera.Ncols
	scene.render.resolution_y = camera.Nrows

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
	offset = np.array([[1,0,0],
										[0,-1,0],
										[0,0,-1]])
	cam_quat = Quaternion()
	cam_quat.fromDCM(offset@dcm)
	obj.rotation_quaternion = mu.Quaternion(cam_quat.toArray())
	#obj.rotation_quaternion = mu.Quaternion(state.attitude.toArray())
	print(obj.rotation_quaternion)
	obj.location.x = state.position[0]
	obj.location.y = state.position[1]
	obj.location.z = state.position[2]
	return


def moveSunObject(obj, pos, angles):

	# Position in km, angles in degrees
	
	obj.rotation_euler[0] = angles[0] * (pi / 180.0)
	obj.rotation_euler[1] = angles[1] * (pi / 180.0)
	obj.rotation_euler[2] = angles[2] * (pi / 180.0)

	obj.location.x = pos[0]
	obj.location.y = pos[1]
	obj.location.z = pos[2]
	return


def load_config(filename,old_config=None):
	new_config = {}
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
	for i,arg in enumerate(sys.argv[5:]):
		print("Loading config {}: {}...".format(i,arg))
		config = load_config(join(CONFIG_PATH,arg),old_config=config)
	lons = [0]
	lats = [0]
	locations = []
	for lat in lats:
		for lon in lons:
			locations.append([lat,lon])
	sun_angles = [x for x in range(180,360,10)]
	
	#quatWorldtoCam = Quaternion(0.5,[0.5,0.5,0.5])
	quatWorldtoCam = Quaternion()
	quatWorldtoCam.fromDCM(array([[0,0,1],
																[-1,0,0],
																[0,-1,0]]))
	#quatWorldtoCam = Quaternion(0.5,[0.5,-0.5,-0.5])
	#sc_quat = Quaternion(0,[0,0,1])
	#sc_quat = Quaternion(.707,[0,0,-.707])
	#sc_quat = Quaternion(0.707,[0,-0.707,0])
	#sc_quat = Quaternion(0.1,[0,0,-0.995])
	sc_quat = Quaternion(1,[0,0,0])
	
	#pos = array([2450487.68,-1768944.776,951442.2338])
	quat = Quaternion()
	dcm = quatWorldtoCam.toDCM().T@sc_quat.toDCM()
	print(sc_quat.toDCM())
	print(quatWorldtoCam.toDCM())
	print(dcm)
	quat.fromDCM(dcm)
	#quat = Quaternion(0.216668887,[-0.702665992,0.161286356,0.658256643])
	pos = array([-RADIUS*7,0,0])
	state = State(pos,quat)
	camera = get_camera("../configs/cameras/testcam.json")
	camera.set_state(state)
	print(np.rad2deg(camera.FOV_x),np.rad2deg(camera.FOV_y))


	render(camera,locations,sun_angles,config,"../outimages")
	# Save Mainfile
	#bpy.ops.wm.save_mainfile()
	exit(0)
