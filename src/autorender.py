import os
import sys
import bpy
import numpy as np
from numpy import pi,cos,sin,arccos,arcsin,arctan,deg2rad,rad2deg,array
import time
import mathutils as mu
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


def render(camera,pos,sun_angles,moon_config,sun_config,render_config,outdir):
	global isRendering
	if not os.path.exists(outdir):
		os.makedirs(outdir)
	scene = setup(moon_config,sun_config,camera,render_config)
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
	

def setup(moon_config,sun_config,camera,render_config):
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
	cam.data.angle_x = camera.FOV_x
	cam.data.angle_y = camera.FOV_y
	cam.data.clip_end = np.inf
	cam.data.sensor_fit = "AUTO"
	cam.data.dof.use_dof=False
	scene.render.resolution_x = camera.Ncols
	scene.render.resolution_y = camera.Nrows
	scene.render.resolution_percentage = 100

	# Config Moon Material
	if not "MoonRocks" in bpy.data.materials:
		print("Cannot find Moon Material")
		return None
	moon_mat = bpy.data.materials["MoonRocks"]
	nodes = moon_mat.node_tree.nodes
	principled_bsdf = nodes.get("Principled BSDF")
	principled_bsdf.inputs.get("Roughness").default_value = moon_config[0]
	principled_bsdf.inputs.get("Metallic").default_value = moon_config[1]
	principled_bsdf.inputs.get("IOR").default_value = moon_config[2]
	principled_bsdf.inputs.get("Coat Weight").default_value = 0
	principled_bsdf.inputs.get("Sheen Weight").default_value = 0
	principled_bsdf.inputs.get("Emission Strength").default_value = 0
	contrast_node = nodes.get("Brightness/Contrast")
	if contrast_node is None:
		print("No Contrast Node Found")
	else:
		contrast_node.inputs.get("Bright").default_value = 1.0
		contrast_node.inputs.get("Contrast").default_value = 2.0

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

	sun.data.energy = sun_config[0]
	sun.data.color = sun_config[1]
	sun.data.angle = sun_config[2]
	sun.data.use_contact_shadow = True
	#sun.data.shadow_buffer_bias = 100
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
	scene.render.threads_mode = "AUTO"
	scene.render.threads = render_config[0]
	scene.cycles.device = render_config[1]
	scene.cycles.samples = render_config[2]
	scene.cycles.use_denoising = True

	return scene


def moveObject(obj,state):
	obj.rotation_quaternion = mu.Quaternion(state.attitude.toArray())
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


# Globals
isRendering = False


if __name__ == "__main__":
	RADIUS = 1737400
	# Moon config = [roughness, metallic, IOR, ]
	moon_config = [1.0,0.0,1.450]
	# Sun config = [Irradiance (W/m^2), Color(RGB 0-1), Angle(Rad)]
	sun_config = [20,[1,1,1],0.009304]
	#sun_config = [100,[1,1,1],0.009304]
	# Cam config = [focal_length,HNumPix,VNumPix,]
	#cam_config = [102.1,1024,1024]
	#cam_config = [102.1,3840,2160]
	cam_config = [102.1,2592,2048]
	# Render config = [num_threads,CPUvsGPU]
	render_config	= [8,"GPU",1024]
	#render([3237.4],[[0,0]],[0,30,60,90],moon_config,sun_config,cam_config,render_config,"./outimages")
	#lons = [0,30,60,90,120,150,180,210,240,270,300,330]
	lons = [0]
	#lats = [90,60,30,0,-30,-60,-90]
	lats = [0]
	locations = []
	for lat in lats:
		for lon in lons:
			locations.append([lat,lon])
	sun_angles = [x for x in range(0,31,5)]
	
	quatWorldtoCam = Quaternion(0.5,[0.5,-0.5,-0.5])
	sc_quat = Quaternion(0,[0,0,1])
	#sc_quat = Quaternion(.707,[0,0,-.707])
	#sc_quat = Quaternion(0.707,[0,-0.707,0])
	#sc_quat = Quaternion(0.1,[0,0,-0.995])
	#sc_quat = Quaternion(1,[0,0,0])
	quat = Quaternion()
	#dcm = sc_quat.toDCM()@quatWorldtoCam.toDCM()
	dcm = quatWorldtoCam.toDCM()@sc_quat.toDCM()
	print(sc_quat.toDCM())
	print(quatWorldtoCam.toDCM())
	print(dcm)
	quat.fromDCM(dcm)
	pos = array([RADIUS+1500000,0,0])
	state = State(pos,quat)
	camera = get_camera("../configs/cameras/testcam.json")
	camera.set_state(state)


	render(camera,locations,sun_angles,moon_config,sun_config,render_config,"../outimages")
	#old_render([3237.4],locations,sun_angles,moon_config,sun_config,cam_config,render_config,"./outimages")
	# Save Mainfile
	#bpy.ops.wm.save_mainfile()
	exit(0)
