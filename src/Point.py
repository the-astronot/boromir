import math
import numpy as np

class Point():
	def __init__(self,lat,lon,radius,id):
		self.pcoords = np.array([lat,lon,radius])   # Polar Coordinates (deg,deg,km)
		self.xcoords = np.zeros(3,dtype=np.float64)	# Cartesian Coordinates (km,km,km)
		self.normals = np.zeros(3)
		self.pix = np.array([0,0])
		self.neighbors = [None,None,None,None,None,None] # T,TR,R,B,BL,L
		self.id = id
		self.generate_cartesian()

	def __str__(self):
		neighbors = [-1,-1,-1,-1,-1,-1]
		for i in range(6):
			if self.neighbors[i] is not None:
				neighbors[i] = self.neighbors[i].id
		return "Point {}: PCoords-[{},{},{}], XCoords-[{},{},{}], Normals-[{},{},{}], Texture-[{},{}], Neighbors={}".format(self.id,self.pcoords[0],self.pcoords[1],self.pcoords[2],self.xcoords[0],self.xcoords[1],self.xcoords[2],self.normals[0],self.normals[1],self.normals[2],self.pix[0],self.pix[1],neighbors)

	def generate_cartesian(self):
		lat_r = math.radians(self.pcoords[0])
		lon_r = math.radians(self.pcoords[1])
		radius = self.pcoords[2]
		self.xcoords[0] = radius*math.cos(lat_r)*math.cos(lon_r)
		self.xcoords[1] = radius*math.cos(lat_r)*math.sin(lon_r)
		self.xcoords[2] = radius*math.sin(lat_r)
	
	def add_normals(self, normals):
		self.normals = np.add(self.normals,normals)

	def zero_normals(self):
		self.normals = np.zeros(3)

	def normalize(self):
		normal = np.linalg.norm(self.normals)
		if normal == 0:
			return self.normals
		self.normals/=normal

	def set_pixel(self,x,y):
		self.pix = np.array([x,y])

	def assign_neighbors(self,top,top_right,right,bottom,bottom_left,left):
		self.neighbors = [top,top_right,right,bottom,bottom_left,left]

	def get_faces(self):
		self.zero_normals()
		faces = []
		order = [[0,1,2],[0,2,1],[2,0,1],[2,1,0],[1,2,0],[1,0,2]]
		for i in range(6):
			if self.neighbors[i] is not None and self.neighbors[(i+1)%6] is not None:
				face_combo = [self.neighbors[i],self.neighbors[(i+1)%6],self]
				self.normals += calc_normal(face_combo[2].xcoords,face_combo[1].xcoords,face_combo[0].xcoords)
				faces.append([face_combo[order[i][0]],face_combo[order[i][1]],face_combo[order[i][2]]])
		self.normalize()
		return faces

def get_neighbor(by_pcoords,point,n_id,deltas):
	# n_ids:	0	1	2	3	4	5
	#						T	TR	R	B	BL	L
	lat_mods = [1,1,0,-1,-1,0]
	lon_mods = [0,1,1,0,-1,-1]
	new_lat = point.pcoords[0]+lat_mods[n_id]*deltas[0]
	new_lon = ((540+point.pcoords[1]+lon_mods[n_id]*deltas[1])%360)-180
	n_pcoords = (new_lat,new_lon)
	if n_pcoords in by_pcoords:
		return by_pcoords[n_pcoords]
	else:
		if lon_mods[n_id] != 0:
			return None
		elif np.abs(point.pcoords[0]) == 90:
			return None
		elif n_pcoords[0] > 90:
			return by_pcoords[(90,0)]
		elif n_pcoords[0] < -90:
			return by_pcoords[(-90,0)]
		return None

def calc_normal(a,b,c):
	ba = b-a
	ca = c-a
	return np.cross(ba,ca)
