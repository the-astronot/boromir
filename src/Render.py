################################################################################
# NOTE: You should never call this file directly!                              #
#       This file is run by other scripts within Blender                       #
################################################################################
# Library imports
import sys
import os
from os.path import exists,basename,dirname,abspath,join
################################################################################
#..I'm sorry, Blender sucks and it requires this workaround....................#
if __name__ == "__main__":
	ROOT_DIR = dirname(dirname(abspath(__file__)))
	version = "{}.{}".format(sys.version_info.major,sys.version_info.minor)
	site_pkgs = join(ROOT_DIR,".venv","lib","python{}".format(version),"site-packages")
	sys.path.append(site_pkgs)
	import mathutils as mu
################################################################################
import pickle
import bpy
import numpy as np
from numpy.linalg import norm
import time

SRC_DIR = dirname(abspath(__file__))
sys.path.append(SRC_DIR)

# Local imports
from paths import *
from Structures import Quaternion,State
from metadata import create_metadata
from error_codes import RenderError, RenderSetupError


# Render object
class Render:
	def __init__(self,camera,poses,mesh_state,configs):
		self.camera = camera
		self.poses = poses
		self.mesh_state = mesh_state
		self.configs = configs


# All of the Blender rendering code
def startRender():
	global isRendering
	isRendering = True


def endRender(a,b):
	global isRendering
	isRendering = False


def enable_gpus(device_type):
	"""
		Enable the GPU
		Taken from: https://blender.stackexchange.com/questions/156503/rendering-on-command-line-with-gpu
	"""
	prefs = bpy.context.preferences
	cycles_prefs = prefs.addons["cycles"].preferences
	cycles_prefs.refresh_devices()
	devices = cycles_prefs.devices
	use_cpus = False
	if device_type == "CPU":
		use_cpus = True
	
	activated_gpus = []
	for device in devices:
		if device.type == "CPU":
			device.use = use_cpus
		else:
			device.use=True
			activated_gpus.append(device.name)
	
	if len(activated_gpus) > 0:
		cycles_prefs.compute_device_type = device_type
		bpy.context.scene.cycles.device = "GPU"
	
	return activated_gpus


def render(render_obj,i,scene):
	global isRendering
	camera = render_obj.camera
	config = render_obj.configs
	pose = render_obj.poses[i]
	camera.set_state(pose.cam_state)
	if scene is None:
		return RenderError.NO_SCENE
	# Get everything
	sun = bpy.data.objects["Light"]
	earth = bpy.data.objects["EARTH"]
	earth.hide_render = not pose.render_earth
	earth.rotation_mode = 'QUATERNION'
	cam = scene.camera
	cam.rotation_mode = 'QUATERNION'
	#  Move eveything into place
	moveObject(cam,camera.state)
	moveObject(earth,pose.earth_state,iscamera=False)
	moveSun(sun,pose.sun_los)
	# Prepare renderer
	filename =  os.path.join(config["outdir"],pose.name)
	scene.render.image_settings.color_mode = config["color_mode"]
	scene.render.image_settings.color_depth = str(config["color_depth"])
	scene.render.image_settings.file_format = config["file_ext"]
	scene.render.filepath = filename
	if exists(filename) and config["re_render"]==0: # Don't re-render rendered image
		print("File: {} already exists, skipping...".format(basename(filename)))
		return RenderError.RE_RENDER
	startRender()
	bpy.ops.render.render("INVOKE_DEFAULT",write_still=True)
	return RenderError.SUCCESS
	

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
		#print("No Camera, Adding Camera")
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
	#cam.data.dof.focus_distance = norm(camera.state.position)
	cam.data.dof.aperture_blades = camera.NumBlades
	cam.data.dof.aperture_fstop = camera.F_Stop
	scene.render.resolution_x = camera.Ncols
	scene.render.resolution_y = camera.Nrows
	exposure_offset = int(config["exposure_offset"])
	scene.view_settings.exposure = np.log2((camera.F_Stop**2)/(camera.Exposure_Time))+np.log2(camera.iso/100)+exposure_offset
	#print("Exposure = {}".format(scene.view_settings.exposure))

	# Config Moon
	status = setup_Moon(config)
	if status != 0:
		return RenderSetupError.MOON_BUILD_FAIL, None
	# Config Earth
	status = setup_Earth(config)
	if status != 0:
		return RenderSetupError.EARTH_BUILD_FAIL, None

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
	sun.data.color = np.array(config["sun"]["color"],dtype=np.float32)
	sun.data.angle = float(config["sun"]["angle"])
	sun.data.use_contact_shadow = True
	sun.data.shadow_trace_distance = np.inf
	sun.data.shadow_cascade_max_distance = np.inf
	sun.rotation_mode = "YXZ"

	# Configure Background
	bg = scene.world.node_tree.nodes["Background"]
	image = bpy.data.images.load(STARS_MAP)
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
	#scene.cycles.device = config["device"]
	scene.cycles.samples = int(config["samples"])
	scene.cycles.use_denoising = bool(config["denoise"]=="true")

	return RenderSetupError.SUCCESS, scene


def setup_Moon(config):
	# Material Creation
	obj = bpy.data.objects["Moon"]
	mat = bpy.data.materials.new(name="MoonRocks")
	obj.data.materials.append(mat)

	# Set the material to use the Principled BSDF shader
	mat.use_nodes = True
	nodes = mat.node_tree.nodes
	principled_bsdf = nodes.get("Principled BSDF")
	if principled_bsdf is None:
			principled_bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
	principled_bsdf.inputs.get("Roughness").default_value = float(config["moon"]["roughness"])
	principled_bsdf.inputs.get("Metallic").default_value = float(config["moon"]["metallic"])
	principled_bsdf.inputs.get("IOR").default_value = float(config["moon"]["ior"])
	principled_bsdf.inputs.get("Coat Weight").default_value = 0
	principled_bsdf.inputs.get("Sheen Weight").default_value = 0
	principled_bsdf.inputs.get("Emission Strength").default_value = 0
	principled_bsdf.distribution = "MULTI_GGX" # Added for testing

	material_output = nodes.get("Material Output")
	if material_output is None:
			material_output = nodes.new(type="ShaderNodeOutputMaterial")
	links = mat.node_tree.links
	links.new(principled_bsdf.outputs["BSDF"], material_output.inputs["Surface"])

	# Add an image texture to the material and connect it to the Base Color of the Principled BSDF
	if os.path.exists(MOON_ALBEDO_MAP):
		print("Found moon albedo file!")
		image = bpy.data.images.load(MOON_ALBEDO_MAP)
		texture_node = nodes.new(type="ShaderNodeTexImage")
		texture_node.image = image
		contrast_node = nodes.new(type="ShaderNodeBrightContrast")
		contrast_node.inputs.get("Bright").default_value = config["moon"]["bright"]
		contrast_node.inputs.get("Contrast").default_value = config["moon"]["contrast"]
		links.new(texture_node.outputs["Color"], contrast_node.inputs["Color"])
		links.new(contrast_node.outputs["Color"], principled_bsdf.inputs["Base Color"])
	else:
		print("Could not find moon albedo file. Something is wrong.")
		return 1
	return 0


def setup_Earth(config):
	bpy.ops.mesh.primitive_uv_sphere_add(radius=6371000,
																			enter_editmode=False,
																			align="WORLD",
																			segments=500,
																			ring_count=250,
																			location=(0,0,0),
																			scale=(1,1,1))
	earth_obj = bpy.context.active_object
	earth_obj.name = "EARTH"
	mat = bpy.data.materials.new(name="EARTH")
	earth_obj.data.materials.append(mat)

	# Set the material to use the Principled BSDF shader
	mat.use_nodes = True
	nodes = mat.node_tree.nodes
	principled_bsdf = nodes.get("Principled BSDF")
	if principled_bsdf is None:
			principled_bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
	principled_bsdf.inputs.get("Roughness").default_value = float(config["earth"]["roughness"])
	principled_bsdf.inputs.get("Metallic").default_value = float(config["earth"]["metallic"])
	principled_bsdf.inputs.get("IOR").default_value = float(config["earth"]["ior"])
	principled_bsdf.inputs.get("Coat Weight").default_value = 0
	principled_bsdf.inputs.get("Sheen Weight").default_value = 0
	principled_bsdf.inputs.get("Emission Strength").default_value = 0
	principled_bsdf.distribution = "MULTI_GGX" # Added for testing

	material_output = nodes.get("Material Output")
	if material_output is None:
			material_output = nodes.new(type="ShaderNodeOutputMaterial")
	links = mat.node_tree.links
	links.new(principled_bsdf.outputs["BSDF"], material_output.inputs["Surface"])

	# Add an image texture to the material and connect it to the Base Color of the Principled BSDF
	if os.path.exists(EARTH_ALBEDO_MAP):
		print("Found earth albedo file!")
		image = bpy.data.images.load(EARTH_ALBEDO_MAP)
		texture_node = nodes.new(type="ShaderNodeTexImage")
		texture_node.image = image
		contrast_node = nodes.new(type="ShaderNodeBrightContrast")
		contrast_node.inputs.get("Bright").default_value = config["earth"]["bright"]
		contrast_node.inputs.get("Contrast").default_value = config["earth"]["contrast"]
		links.new(texture_node.outputs["Color"], contrast_node.inputs["Color"])
		links.new(contrast_node.outputs["Color"], principled_bsdf.inputs["Base Color"])
	else:
		print("Could not find earth albedo file. Something is wrong.")
		return 1
	return 0


def moveObject(obj,state,iscamera=True):
	dcm = state.attitude.toDCM().T
	# Offset is used to account for blenders atrocious starting quaternion
	offset = np.array([[1,0,0],
										[0,-1,0],
										[0,0,-1]])
	cam_quat = Quaternion()
	cam_quat.fromDCM(offset@dcm)
	quat = Quaternion()
	quat.fromDCM(dcm)
	if iscamera:
		obj.rotation_quaternion = mu.Quaternion(cam_quat.toArray())
	else:
		obj.rotation_quaternion = mu.Quaternion(quat.toArray())
	obj.location.x = state.position[0]
	obj.location.y = state.position[1]
	obj.location.z = state.position[2]
	return


def moveSun(obj, sun_los):
	# Convert from los to angles
	sun_los /= norm(sun_los)
	sun_ra = np.arctan2(sun_los[1],sun_los[0])
	sun_decl = np.arcsin(sun_los[2])
	angles = np.array([np.pi/2+sun_decl,0,sun_ra-np.pi/2])

	# Rotate object
	obj.rotation_euler[0] = angles[0]
	obj.rotation_euler[1] = angles[1]
	obj.rotation_euler[2] = angles[2]

	obj.location.x = 0
	obj.location.y = 0
	obj.location.z = 0
	return


# Global vars
isRendering = False
MOON_ALBEDO_MAP = None
EARTH_ALBEDO_MAP = None
STARS_MAP = None


if __name__ == "__main__":
	pickle_file = sys.argv[-1]
	render_obj = None
	
	# Read the data from the pickle file
	try:
		with open(pickle_file,"rb") as f:
			render_obj = pickle.load(f)
	except KeyboardInterrupt:
		exit(2)
	except Exception:
		pass

	if render_obj is None:
		print("Render pickle not found, exiting...")
		exit(1)

	# Get Albedo Maps
	MOON_ALBEDO_MAP = join(MAP_DIR,render_obj.configs["moon"]["albedo_map"])
	EARTH_ALBEDO_MAP= join(MAP_DIR,render_obj.configs["earth"]["albedo_map"])
	STARS_MAP = join(MAP_DIR,render_obj.configs["star_map"])
	
	# Enable GPUs
	enable_gpus(render_obj.configs["device"])

	# Create scene
	status, scene = setup(render_obj.camera,render_obj.configs)
	if status != 0: # Issue with setup
		exit(3)

	# Render each image
	for i in range(len(render_obj.poses)):
		status = render(render_obj,i,scene)
		create_metadata(render_obj,i)
		while isRendering is True:
			time.sleep(0.1)
	exit(0)
