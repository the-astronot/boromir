# Library imports
from numpy import deg2rad,array
import json

# Local imports
from Log import log,error


class Camera():
	types = {"FOV_x":deg2rad,
					"FOV_y":deg2rad,
					"F_Stop":float,
					"NumBlades":int,
					"Nrows":int,
					"Ncols":int,
					"SubSamples":int,
					"OffsetPix":array,
					"Exposure_Time":float,
					"iso":float
					}
	
	def __init__(self,json=None,state=None):
		self.default_init()
		if json is not None:
			self.from_json(json)
		if state is not None:
			self.state = state

	def default_init(self):
		self.FOV_x = 10.0
		self.FOV_y = 10.0
		self.iso = 100
		self.F_Stop = 2.8
		self.NumBlades = 5
		self.Nrows = 1024
		self.Ncols = 1024
		self.SubSamples = 1
		self.OffsetPix = array([20,20])
		self.Exposure_Time = 1/250
		self.state = None

	def from_json(self,json):
		for key in json:
			if key in self.types:
				setattr(self,key,self.types[key](json[key]))
		self.check_camera()

	def to_dict(self):
		data = {}
		for attr in self.__dict__:
			data[attr] = getattr(self,attr)
		return data

	def set_state(self,state):
		self.state = state

	def check_camera(self):
		pix_ratio = self.Ncols/self.Nrows
		fov_ratio = self.FOV_x/self.FOV_y
		if pix_ratio != fov_ratio:
			error("WARNING: FOV and Pixel Ratios Don't Match")
			self.FOV_y = self.FOV_x/pix_ratio
			error("         FOV_y Set to {}".format(self.FOV_y))
		if self.FOV_x < 0 or self.FOV_y < 0:
			error("ERROR: Camera FOV(s) are negative")
			return 1
		return 0


def get_camera(filename):
	cam_data=None
	with open(filename,"r") as f:
		cam_data = json.load(f)
	the_camera = Camera(json=cam_data)
	return the_camera
