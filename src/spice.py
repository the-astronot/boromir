# Library imports
import spiceypy as sp
from os.path import join
import numpy as np

# Local imports
from boromir import BASE_DIR
from Structures import Quaternion
from file_io import quick_cd

# Kernel Setup
KERNEL_DIR=join(BASE_DIR,"spicedata")
METAKRNL=join(KERNEL_DIR,"boromir.tm")
with quick_cd(KERNEL_DIR):
	sp.furnsh(METAKRNL)


def time2SunLOS(utc_time):
	"""
		Converts time in UTC to Normalized Sun Line-of-Sight Vector
	"""
	etime = sp.str2et(utc_time)
	[pos,ltime] = sp.spkpos("MOON",etime,"MOON_ME","LT+S","SUN")
	pos = np.array(pos)
	los = pos/np.linalg.norm(pos)
	return los


def time2EarthPose(utc_time):
	etime = sp.str2et(utc_time)
	[pos,ltime] = sp.spkpos("EARTH",etime,"MOON_ME","LT+S","MOON")
	pos_m = pos*1000
	quatE2M = Quaternion()
	quatE2M.fromDCM(sp.pxform("ITRF93","MOON_ME",etime))
	return pos_m,quatE2M


if __name__ == "__main__":
	dt = "12:00:00 January 1 2025"
	sun_los = time2SunLOS(dt)
	print("The Sun LOS at {} is: {}".format(dt,sun_los))
	earth_pos,earth_quat = time2EarthPose(dt)
	print("The Earth Position in MOON_ME at {} is: {}".format(dt,earth_pos))
	print("The Earth's Rotation at {} is: [{},{}]".format(dt,earth_quat.s,earth_quat.v))
	print("The distance from the Earth to the Moon at {} is: {:.1f} km".format(dt,np.linalg.norm(earth_pos)/1000))
