# Library imports
import bpy
import bmesh
from tqdm import tqdm

# Local imports
from Log import critical,warning,info,debug


def build_mesh(verts,faces,colors,outfile):
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
	mesh.from_pydata(verts,[],faces,shade_flat=True)
	del verts
	del faces
	info("Mesh Created from Verts and Faces")

	# UV mapping
	me = obj.data
	bpy.ops.object.mode_set(mode='EDIT')
	bm = bmesh.from_edit_mesh(me)

	uv_layer = bm.loops.layers.uv.verify()

	# adjust uv coordinates
	if False:
		# Old code from when codebase had interactive sessions
		faces = tqdm(bm.faces)
	else:
		faces = bm.faces
	
	# Actually fill in the UV data
	## WARNING: This double for loop is a major constraint on runtime
	## Optimization of this section via some fancy bpy magic would help a lot
	## Alternatively, at some point I'd like to try and replicate Blender's
	## structs in C and just use C for loops to increase speed
	info("Building Mesh UV Loops")
	for face in faces:
			for loop in face.loops:
					loop_uv = loop[uv_layer]
					# use id position of the vertex as a uv coordinate id
					loop_uv.uv = colors[loop.vert.index]
	info("Finished Building Mesh UV Loops")

	bmesh.update_edit_mesh(me)
	bpy.ops.object.mode_set(mode='OBJECT')

	# Save Mainfile
	bpy.ops.wm.save_as_mainfile(filepath=outfile)
	info("Saved blender file")

	return 0
