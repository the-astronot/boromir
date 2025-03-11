# Library imports
import bpy
from tqdm import tqdm
import numpy as np

# Local imports
from Log import critical,warning,info,debug


def build_mesh(verts,faces,colors,outfile):
	"""
		Takes all of the data and builds a mesh
	"""
	# Delete old data, if exists
	if "Moon" in bpy.data.meshes:
		mesh = bpy.data.meshes["Moon"]
		bpy.data.meshes.remove(mesh)
	if "Moon" in bpy.data.objects:
		obj = bpy.data.objects["Moon"]
		bpy.data.objects.remove(obj)
		
	# Create mesh
	mesh = convert_to_mesh(verts,faces,colors)
	obj = bpy.data.objects.new(mesh.name,mesh)
	col = bpy.data.collections["Collection"]
	col.objects.link(obj)
	bpy.context.view_layer.objects.active = obj

	# Save Mainfile
	bpy.ops.wm.save_as_mainfile(filepath=outfile)
	info("Saved blender file")

	return 0


def build_empty_mesh(outfile):
	"""
		Build a file without a mesh
	"""
	# Delete old data, if exists
	if "Moon" in bpy.data.meshes:
		mesh = bpy.data.meshes["Moon"]
		bpy.data.meshes.remove(mesh)
	if "Moon" in bpy.data.objects:
		obj = bpy.data.objects["Moon"]
		bpy.data.objects.remove(obj)

	bpy.ops.wm.save_as_mainfile(filepath=outfile)
	info("Saved blender file")

	return 0


def convert_to_mesh(vertices,faces,colors):
	"""
		This function builds the mesh via lower-level API calls
		NOTE: https://surf-visualization.github.io/blender-course/api/meshes/#creating-a-mesh-high-level had good information about doing this
	"""
	info("Starting Mesh Mapping")
	# Add mesh
	mesh = bpy.data.meshes.new("Moon")
	## Modify data structures
	bl_verts = np.array(vertices,dtype=np.int32).reshape(-1)
	bl_faces = np.array(faces,dtype=np.int32).reshape(-1)
	bl_uv = np.array(colors[bl_faces].reshape(-1),dtype=np.float32)

	# Determining sizes and loops
	loop_length = np.array(3,dtype=np.int32).repeat(faces.shape[0])
	loop_start = np.cumsum(loop_length,dtype=np.int32)-loop_length
	num_vertices = vertices.shape[0]
	num_vertex_indices = bl_faces.shape[0]
	num_loops = loop_start.shape[0]

	# Vertices
	mesh.vertices.add(num_vertices)
	mesh.vertices.foreach_set('co',bl_verts)

	# Polygons
	mesh.loops.add(num_vertex_indices)
	mesh.loops.foreach_set('vertex_index',bl_faces)
	mesh.polygons.add(num_loops)
	mesh.polygons.foreach_set('loop_start',loop_start)
	mesh.polygons.foreach_set('loop_total',loop_length)

	info("Starting UV Mapping")

	# Add UV data
	uv_layer = mesh.uv_layers.new(name="default")
	uv_layer.data.foreach_set("uv",bl_uv)

	info("Finished Mesh Mapping")
	info("Starting Mesh Validation")

	# Update mesh
	mesh.update()
	
	info("Ending Mesh Validation")

	return mesh
