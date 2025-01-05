# Library imports
import bpy
import bmesh
from tqdm import tqdm
import os

# Local imports
from Log import log,error


def build_mesh(verts,faces,colors,texture_file,outfile):
	"""
		Takes all of the data and builds a mesh
	"""
	# Delete old data
	if "Moon" in bpy.data.meshes:
		mesh = bpy.data.meshes["Moon"]
		bpy.data.meshes.remove(mesh)
	if "Moon" in bpy.data.objects:
		obj = bpy.data.objects["Moon"]
		bpy.data.objects.remove(obj)
	# Create mesh
	mesh = bpy.data.meshes.new("Moon")
	obj = bpy.data.objects.new(mesh.name,mesh)
	col = bpy.data.collections["Collection"]
	col.objects.link(obj)
	bpy.context.view_layer.objects.active = obj
	# Fill in data
	mesh.from_pydata(verts,[],faces)
	log("Mesh Created Successfully",1)
	# UV mapping
	me = obj.data
	bpy.ops.object.mode_set(mode='EDIT')
	bm = bmesh.from_edit_mesh(me)
	#bpy.ops.object.mode_set(mode='OBJECT')

	uv_layer = bm.loops.layers.uv.verify()

	# adjust uv coordinates
	if True:
		faces = tqdm(bm.faces)
	else:
		faces = bm.faces
	log("Building UV Loops",2)
	for face in faces:
			for loop in face.loops:
					loop_uv = loop[uv_layer]
					# use id position of the vertex as a uv coordinate id
					loop_uv.uv = colors[loop.vert.index]

	bmesh.update_edit_mesh(me)
	bpy.ops.object.mode_set(mode='OBJECT')

	# Save Mainfile
	bpy.ops.wm.save_as_mainfile(filepath=outfile)
	return 0