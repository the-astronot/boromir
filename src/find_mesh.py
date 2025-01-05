# Library imports
import ctypes as ct
from os.path import join
import numpy as np

# Local imports
from paths import CPP_DIR
from Log import log,error


# Declare CTypes function
libPoints = ct.cdll.LoadLibrary(join(CPP_DIR,"libPoints.so"))
create_mesh = libPoints.findPoints
create_mesh.argtypes = [(ct.c_float*3),
												(ct.c_float*9),
												(ct.c_int*2),
												(ct.c_float*2),
												ct.POINTER(ct.c_float),
												ct.POINTER(ct.c_float),
												ct.POINTER(ct.c_uint64),
												ct.POINTER(ct.c_uint64),
												(ct.c_ulong*2),
												ct.c_float,
												(ct.c_float*2),
												ct.c_char_p]


def find_mesh(camera):
	"""
		Use the known camera data to find the verts, triangles, and colors of the mesh
	"""
	mesh=np.zeros(shape=(camera.SubSamples*(2*camera.OffsetPix[0]+camera.Ncols),
												camera.SubSamples*(2*camera.OffsetPix[1]+camera.Nrows),
												3))
	colors=np.zeros(shape=(camera.SubSamples*(2*camera.OffsetPix[0]+camera.Ncols),
										  	camera.SubSamples*(2*camera.OffsetPix[1]+camera.Nrows),
										  	2))
	# Setup data
	log("Setting Up Data",1)
	pos_c = (ct.c_float*3)(*(camera.state.position))
	dcm_c = (ct.c_float*9)(*(camera.state.attitude.toDCM().flatten()))
	camsize_c = (ct.c_int*2)(*[camera.Ncols,camera.Nrows])
	offset_c = (ct.c_float*2)(*camera.OffsetPix)
	meshsize = np.array(mesh.shape)
	colorsize = np.array(colors.shape)
	meshsize_flt = np.prod(meshsize)
	colorsize_flt = np.prod(colorsize)
	mesh_c = (ct.c_float*meshsize_flt)()
	colors_c = (ct.c_float*colorsize_flt)()
	tris_c = (ct.c_uint64*(meshsize_flt*2))()
	count_c = ct.c_uint64(0)
	meshsize_c = (ct.c_ulong*2)(*meshsize[:2])
	SubSamples_c = ct.c_float(camera.SubSamples)
	fov_c = (ct.c_float*2)(camera.FOV_x,camera.FOV_y)
	dirname_c = ct.create_string_buffer("./".encode())
	# Calling the C script
	log("Calling create_mesh",1)
	status = create_mesh(pos_c,dcm_c,camsize_c,offset_c,mesh_c,colors_c,tris_c,ct.byref(count_c),meshsize_c,SubSamples_c,fov_c,dirname_c)
	if status != 0:
		error("create_mesh (C++ Script) returned status {}".format(status))
	else:
		log("create_mesh (C++ Script) returned status: {}".format(status),1)
	meshsize = np.array([meshsize[1]*meshsize[0],meshsize[2]])
	colorsize = np.array([colorsize[1]*colorsize[0],colorsize[2]])
	mesh = np.frombuffer(mesh_c,dtype=np.float32).reshape(meshsize)
	colors = np.frombuffer(colors_c,dtype=np.float32).reshape(colorsize)
	tris = np.frombuffer(tris_c,dtype=np.uint64).reshape((-1,3))
	count = count_c.value
	tris = tris[:count]
	return mesh,tris,colors
