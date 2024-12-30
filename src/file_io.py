# All the code for dealing with reading/writing
# Library imports
import json
import os
from os.path import exists,join,abspath,dirname,basename,isdir,isfile
import contextlib
import numpy as np

################################################################################
# CONTEXT MANAGER, for performing required actions at file locations
# This is required to be high so as to avoid a circular import
@contextlib.contextmanager
def quick_cd(path):
	"""
		Save current path, temporarily cd into specified path,
		perform required actions, and cd back to the original path
	"""
	old_dir = os.getcwd()
	try:
		os.chdir(path)
		yield
	except NotADirectoryError:
		raise NotADirectoryError(path)
	finally:
		os.chdir(old_dir)
	return
################################################################################

# Local imports
from error_codes import *
from Structures import Quaternion
from Pose import Pose


# CHECK IF FILE EXISTS ON LOCAL OR SPECIFIED PATH
def check_for_file(filename,dirname):
	if exists(filename) and isfile(filename):
		return filename
	if exists(join(dirname,filename)) and isfile(join(dirname,filename)):
		return join(dirname,filename)
	raise FileNotFoundError(filename)


# CHECK IF DIRECTORY EXISTS
def check_for_dir(dirname):
	if exists(dirname) and isdir(dirname):
		return dirname
	raise NotADirectoryError(dirname)


# CHECK TRAJECTORY FILE
def read_traj_file(filename):
	"""
		Reads the ${filename}$ csv file and parses poses
	"""
	poses = []
	# Check if file exists
	if not (exists(filename) and isfile(filename)):
		return TrajFileReadError.FILENOTFOUND
	# Read the data
	text = ""
	with open(filename,"r") as f:
		text = f.read().strip("\n")
	entries = text.split("\n")
	for i,entry in enumerate(entries):
		if i == 0: # File header
			continue
	
		# Unpack all the pose data
		data = entry.strip(",").split(",")
		name = data[0]
		sc_pos = np.array(data[1:4],dtype=float)
		sc_quat = Quaternion(data[4],np.array(data[5:8],dtype=float))
		time = None
		sun_los = None
		earth_pos = None
		earth_quat = None
		# Check if time exists
		if len(data[8]) > 0:
			time = data[8].strip("\"").strip("\'")
		# Check if sun los exists
		if len(data) > 11:
			if len(data[9])>0 and len(data[10])>0 and len(data[11])>0:
				sun_los = np.array(data[9:12],dtype=float)
		# Check if Earth pos exists
		if len(data) > 14:
			if len(data[12])>0 and len(data[13])>0 and len(data[14])>0:
				earth_pos = np.array(data[12:15],dtype=float)
		# Check if Earth quat exists
		if len(data) > 18:
			if len(data[15])>0 and len(data[16])>0 and len(data[17])>0 and len(data[18])>0:
				earth_quat = Quaternion(data[15],np.array(data[16:19],dtype=float))
		# Create pose
		pose = Pose(name,sc_pos,sc_quat,time,sun_los,earth_pos,earth_quat)
		if not pose.complete:
			return TrajFileReadError.INCOMPLETEPOSE, poses
		poses.append(pose)
	return TrajFileReadError.SUCCESS, poses


# CHECK RANDOM POSE FILE
def read_rand_file(filename):
	return


# READING JSON DATA
def load_config(filename,old_config=None):
	new_config = {}
	if not exists(filename):
		print("Config: {} Not Found...".format(filename))
	with open(filename,"r") as f:
		new_config = json.load(f)
	if old_config is not None:
		for key in new_config:
			old_config[key] = new_config[key]
		return old_config
	return new_config

