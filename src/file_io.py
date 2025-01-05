# All the code for dealing with reading/writing
# Library imports
import json
import os
from os.path import exists,join,abspath,dirname,basename,isdir,isfile
import contextlib
import numpy as np

# Local imports
from error_codes import *
from Structures import Quaternion,State
from Pose import Pose
from Log import log,error
from file_io_util import *


# CHECK IF FILE EXISTS ON LOCAL OR SPECIFIED PATH
def check_for_file(filename,dirname):
	if exists(filename) and isfile(filename):
		return filename
	if exists(join(dirname,filename)) and isfile(join(dirname,filename)):
		return join(dirname,filename)
	error("ERROR: File {} Not Found".format(filename))
	exit()


# CHECK IF DIRECTORY EXISTS
def check_for_dir(dirname):
	if exists(dirname) and isdir(dirname):
		return dirname
	error("ERROR: Directory {} Not Found".format(dirname))
	exit()


# IF FILENAME IS BASENAME, ADD PATH
def basename2path(filename,path):
	if basename(filename) == filename:
		return join(path,filename)
	return filename


# TRY TO MAKE DIRECTORY IF IT DOESN'T EXIST
def try_makedir(path):
	if not exists(path):
		try:
			os.makedirs(path)
		except:
			return 2
		finally:
			return 0
	return 1


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
		cam_pos = np.array(data[1:4],dtype=float)
		cam_quat = Quaternion(data[4],np.array(data[5:8],dtype=float))
		cam_state = State(position=cam_pos,attitude=cam_quat)
		time = None
		sun_los = None
		earth_state = None
		# Check if time exists
		if len(data[8]) > 0:
			time = data[8].strip("\"").strip("\'")
		# Check if sun los exists
		if len(data) > 11:
			if len(data[9])>0 and len(data[10])>0 and len(data[11])>0:
				sun_los = np.array(data[9:12],dtype=float)
		# Check if Earth pos exists
		if len(data) > 18:
			earth_pos = None
			earth_quat = None
			if len(data[12])>0 and len(data[13])>0 and len(data[14])>0:
				earth_pos = np.array(data[12:15],dtype=float)
		# Check if Earth quat exists
			if len(data[15])>0 and len(data[16])>0 and len(data[17])>0 and len(data[18])>0:
				earth_quat = Quaternion(data[15],np.array(data[16:19],dtype=float))
			if earth_pos is not None and earth_quat is not None:
				earth_state = State(position=earth_pos,attitude=earth_quat)
		# Create pose
		pose = Pose(name,cam_state,time=time,sun_los=sun_los,earth_state=earth_state)
		log(pose,3)
		if not pose.complete:
			error("Incomplete Pose on entry {}".format(i))
			return TrajFileReadError.INCOMPLETEPOSE, poses
		poses.append(pose)
	log("Completed Pose Reading",0,also_print=True)
	return TrajFileReadError.SUCCESS, poses


# CHECK RANDOM POSE FILE
def read_rand_file(filename):
	return


# READING JSON DATA
def load_config(filename,old_config=None):
	new_config = {}
	if not exists(filename):
		error("Config: {} Not Found...".format(filename))
	with open(filename,"r") as f:
		new_config = json.load(f)
	if old_config is not None:
		for key in new_config:
			old_config[key] = new_config[key]
		return old_config
	return new_config

