# Global imports
import numpy as np

# Local imports
from error_codes import *
from spice import time2SunLOS, time2EarthPose
from Structures import Quaternion,State


class Pose:
	"""
		The pose class contains all the data related to the position and rotation of the requisite bodies.
	"""
	def __init__(self,name,cam_state,time=None,sun_los=None,earth_state=None):
		self.name = name
		self.complete = False
		self.cam_state = cam_state
		self.time = time
		self.sun_los = sun_los
		self.earth_state = earth_state
		self.render_earth = False
		# Make sure that either a time is specified or a sun position is
		if time is None and sun_los is None:
			return
		elif time is not None:
			self.sun_los = np.array(time2SunLOS(time))
			self.earth_state = time2EarthPose(time)
			self.render_earth = True
		else:
			if self.earth_state is not None:
				self.render_earth = True
			else:
				self.earth_state = State()
		self.complete = True
		return

	def __str__(self):
		comp = ["Inc","C"]
		return "POSE: {} -- {}omplete\
						\nCam_Pos = {} (m)\
						\nCam_Quat = {}\
						\nTime = {}\
						\nSun_LOS = {}\
						\nEarth_Pos = {} (m)\
						\nEarth_Quat = {}".format(self.name,
																		comp[self.complete],
																		self.cam_state.position,
																		self.cam_state.attitude,
																		self.time,
																		self.sun_los,
																		self.earth_state.position,
																		self.earth_state.attitude)

	def __repr__(self):
		return self.__str__()


if __name__ == "__main__":
	pose = Pose("Test",
						 	np.zeros(3),
						 	Quaternion(1,[0,0,0]),
							"Dec 24 2024 12:00:00")
	print(pose)
