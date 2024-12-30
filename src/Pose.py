# Global imports
import numpy as np

# Local imports
from error_codes import *
from spice import time2SunLOS, time2EarthPose
from Structures import Quaternion


class Pose:
	"""
		The pose class contains all the data related to the position and rotation of the requisite bodies.
	"""
	def __init__(self,name,sc_pos,sc_quat,time=None,sun_los=None,earth_pos=None,earth_quat=None):
		self.name = name
		self.complete = False
		self.sc_pos = sc_pos
		self.sc_quat = sc_quat
		self.time = time
		self.sun_los = sun_los
		self.earth_pos = earth_pos
		self.earth_quat = earth_quat
		self.render_earth = False
		# Make sure that either a time is specified or a sun position is
		if time is None and sun_los is None:
			pass
		elif time is not None:
			self.sun_los = np.array(time2SunLOS(time))
			self.earth_pos,self.earth_quat = time2EarthPose(time)
			self.complete = True
		else:
			pass

	def __str__(self):
		comp = ["Inc","C"]
		return "POSE: {} -- {}omplete\
						\nSC_Pos = {} (m)\
						\nSC_Quat = {}\
						\nTime = {}\
						\nSun_LOS = {}\
						\nEarth_Pos = {} (m)\
						\nEarth_Quat = {}".format(self.name,
																		comp[self.complete],
																		self.sc_pos,
																		self.sc_quat,
																		self.time,
																		self.sun_los,
																		self.earth_pos,
																		self.earth_quat)

	def __repr__(self):
		return self.__str__()


if __name__ == "__main__":
	pose = Pose("Test",
						 	np.zeros(3),
						 	Quaternion(1,[0,0,0]),
							"Dec 24 2024 12:00:00")
	print(pose)
