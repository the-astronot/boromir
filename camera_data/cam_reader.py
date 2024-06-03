import json
import numpy as np
from numpy import array


def read_cam_file(filename):
	cam_json = {}
	with open(filename,"r") as f:
		cam_json = json.load(f)["camera"]
	print(cam_json)
	if "name" not in cam_json:
		return None
	return Camera(cam_json)


class Camera():
	def __init__(self,cam_json):
		self.name = cam_json["name"]
		self.json = cam_json
		self.px = cam_json["px"]
		self.py = cam_json["py"]
		self.n_sub_pix = cam_json["n_sub_pix"]
		self.dx = -1
		self.dy = -1
		self.alpha = 0
		self.up = -1
		self.vp = -1
		self.k1 = 0
		self.k2 = 0
		self.p1 = 0
		self.p2 = 0
		self.p3 = 0
		if "params" in cam_json:
			self.dx = cam_json["params"]["dx"]
			self.dy = cam_json["params"]["dy"]
			self.alpha = cam_json["params"]["alpha"]
			self.up = cam_json["params"]["up"]
			self.vp = cam_json["params"]["vp"]
			self.k1 = cam_json["params"]["k1"]
			self.k2 = cam_json["params"]["k2"]
			self.p1 = cam_json["params"]["p1"]
			self.p2 = cam_json["params"]["p2"]
			self.p3 = cam_json["params"]["p3"]
		self.calc_dx()
		self.calc_dy()
		self.calc_up()
		self.calc_vp()
		return
	
	def __str__(self):
		return "Camera: {}\n{}".format(self.name,
																 	array([[self.dx,self.alpha,self.up],
																				[0,self.dy,self.vp],
																				[0,0,1]]))

	def calc_dx(self):
		if self.dx == -1:
			return
		return
		
	def calc_dy(self):
		if self.dy == -1:
			return
		return
	
	def calc_up(self):
		if self.up == -1:
			return
		return
	
	def calc_vp(self):
		if self.vp == -1:
			return
		return


if __name__ == "__main__":
	print(read_cam_file("cam.json"))
