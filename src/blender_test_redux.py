# Large image size stuff
import os
os.environ["OPENCV_IO_MAX_IMAGE_PIXELS"] = pow(2,40).__str__()

import bpy
import bmesh
import numpy as np
import time
from tqdm import tqdm


def save_to_file(filename,data):
	f = open(filename,"w+")
	for triple in data:
		f.write("{},{},{}\n".format(triple[0],triple[1],triple[2]))
	f.close()


def read_from_file(filename,dtype=np.float32,cols=3):
	f = open(filename,"r")
	text = f.read()
	f.close()
	lines = text.strip("\n").split("\n")
	data = np.zeros((len(lines),cols),dtype=dtype)
	for i in range(len(lines)):
		line = lines[i].split(",")
		for j in range(cols):
			data[i][j] = line[j]
	return data


if __name__ == "__main__":
	print("{}:Starting!".format(time.localtime()))

	data_path = "/home/the-astronot/code/grad_school/project/src/"
	image_path = os.path.join(data_path,"../images")
	image_name = "lroc_color_poles.tif"
	verts_file = "verts.bin"
	faces_file = "faces.bin"
	colors_file = "colors.bin"

	mesh = bpy.data.meshes.new("Moon")  # add the new mesh
	obj = bpy.data.objects.new(mesh.name, mesh)
	col = bpy.data.collections["Collection"]
	col.objects.link(obj)
	bpy.context.view_layer.objects.active = obj

	verts = np.fromfile(verts_file,dtype=np.float32)
	num_pts = int(verts.shape[0]/3)
	verts = verts.reshape(num_pts,3)
	print(verts.shape)
	print("{}:Loaded Vertices!".format(time.localtime()))
	edges = []
	faces = np.fromfile(faces_file,dtype=np.uint64)
	num_faces = int(faces.shape[0]/3)
	faces = faces.reshape(num_faces,3)
	print(faces.shape)
	print("{}:Loaded Faces!".format(time.localtime()))
	
	colors = np.fromfile(colors_file,dtype=np.float32)
	num_colors = int(colors.shape[0]/2)
	colors = colors.reshape(num_colors,2)
	print(colors.shape)

	mesh.from_pydata(verts, edges, faces)

	print("{}:Mesh Created!".format(time.localtime()))

	# UV mapping
	me = obj.data
	bpy.ops.object.mode_set(mode='EDIT')
	bm = bmesh.from_edit_mesh(me)
	#bpy.ops.object.mode_set(mode='OBJECT')

	uv_layer = bm.loops.layers.uv.verify()

	# adjust uv coordinates
	for face in tqdm(bm.faces):
			for loop in face.loops:
					loop_uv = loop[uv_layer]
					# use id position of the vertex as a uv coordinate id
					loop_uv.uv = colors[loop.vert.index]

	bmesh.update_edit_mesh(me)

	# Material Creation
	mat = bpy.data.materials.new(name="MoonRocks")
	obj.data.materials.append(mat)

	# Set the material to use the Principled BSDF shader
	mat.use_nodes = True
	nodes = mat.node_tree.nodes
	principled_bsdf = nodes.get("Principled BSDF")
	if principled_bsdf is None:
			principled_bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
	material_output = nodes.get("Material Output")
	if material_output is None:
			material_output = nodes.new(type="ShaderNodeOutputMaterial")
	links = mat.node_tree.links
	links.new(principled_bsdf.outputs["BSDF"], material_output.inputs["Surface"])

	# Add an image texture to the material and connect it to the Base Color of the Principled BSDF
	texture_path = os.path.join(image_path, image_name)
	if os.path.exists(texture_path):
		print("Found moon albedo file!")
		image = bpy.data.images.load(texture_path)
		texture_node = nodes.new(type="ShaderNodeTexImage")
		texture_node.image = image
		contrast_node = nodes.new(type="ShaderNodeBrightContrast")
		contrast_node.inputs.get("Bright").default_value = 1.0
		contrast_node.inputs.get("Contrast").default_value = 2.5
		links.new(texture_node.outputs["Color"], contrast_node.inputs["Color"])
		links.new(contrast_node.outputs["Color"], principled_bsdf.inputs["Base Color"])

	bpy.ops.object.mode_set(mode='OBJECT')

	bpy.ops.file.pack_all()

	# Save Mainfile
	bpy.ops.wm.save_as_mainfile(filepath=data_path+"moon_test.blend")

	print("{}:Finishing!".format(time.localtime()))
