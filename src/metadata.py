# Library imports
import json
import sys
import os
from os.path import join,basename,relpath

# Local imports



def get_data(_to,_to_name,_from,_from_name):
	# Check _from for _from_name, set _to_name in _to if found
	## Can search multiple levels of _from by adding "/" separator
	## between keys/indices in _from_name
	data = None
	spl_from_name = _from_name.split("/",1)
	if type(_from) == list:
		data = _from[int(spl_from_name[0])]
	elif spl_from_name[0] in _from:
		data = _from[spl_from_name[0]]
	if len(spl_from_name) == 1:
		if data is not None:
			_to[_to_name] = data
	elif data is not None:
		_to = get_data(_to,_to_name,data,spl_from_name[1])
	return _to


def camera2config(camera,old_config=None):
	config = {}
	if old_config is not None:
		config = old_config
	data = camera.to_dict()
	for key in data:
		config[key] = data[key]
	return config


def create_metadata(render,idx):
	# Spitting out all of the metadata into a file
	#state_data = config["STATES"][state_idx]
	config = render.configs
	pose = render.poses[idx]
	meta_file = join(config["outdir"],"{}.json".format(pose.name))
	data = {}
	config = camera2config(render.camera,old_config=config)
	## World Data
	if pose.time is None:
		data["Time (s)"] = "N/A"
	else:
		data["Time (s)"] = pose.time
	#data = get_data(data,"Time (s)",state_data,"TIME")
	# Sun
	data["Sun LoS"] = pose.sun_los.tolist()
	#data = get_data(data,"SUN LoS",state_data,"SUN")
	# Earth
	if pose.render_earth:
		data["Earth Pos (m)"] = pose.earth_state.position.tolist()
		data["Earth Quat (s)"] = pose.earth_state.attitude.s
		data["Earth Quat (v)"] = (-1*pose.earth_state.attitude.v).tolist()
	## SC/CAM 6-DOF
	data["Cam Pos (m)"] = pose.cam_state.position.tolist()
	data["Cam Quat (s)"] = pose.cam_state.attitude.s
	data["Cam Quat (v)"] = (-1*pose.cam_state.attitude.v).tolist()
	## Camera Settings
	data = get_data(data,"FOV X (rad)",config,"FOV_x")
	data = get_data(data,"FOV Y (rad)",config,"FOV_y")
	data = get_data(data,"F_Stop",config,"F_Stop")
	data = get_data(data,"Num_Blades",config,"NumBlades")
	data = get_data(data,"Nrows",config,"Nrows")
	data = get_data(data,"Ncols",config,"Ncols")
	data = get_data(data,"Subsamples",config,"SubSamples")
	data = get_data(data,"Exposure_Time",config,"Exposure_Time")
	data = get_data(data,"ISO",config,"iso")
	if "OffsetPixels" in config:
		data["OffsetPix"] = [int(config["OffsetPix"][0]),int(config["OffsetPix"][1])]
	## Blender Settings
	data = get_data(data,"Render Samples",config,"samples")
	data = get_data(data,"Light_Bounces",config,"bounces")
	data = get_data(data,"Denoise",config,"denoise")
	data = get_data(data,"Bit_Depth",config,"color_depth")
	data = get_data(data,"Color_Mode",config,"color_mode")
	data = get_data(data,"Moon_Albedo_File",config,"moon/albedo_map")
	data = get_data(data,"Earth_Albedo_File",config,"earth/albedo_map")
	## Render Settings
	with open(meta_file,"w+") as f:
		json.dump(data,f,indent=2)
	return


def group_to_tsv(filepath,outfile="all_data.tsv",delimiter="\t"):
	"""
		This function was hastily written to combine metadata files
		into a single (c/t)sv file (Needs rewrite)
	"""
	all_keys = {"filename":1}
	all_data = []
	all_jsons = []
	# Load all data in
	for(root,_,files) in os.walk(filepath):
		for file in files:
			if file.endswith(".json"):
				all_jsons.append(join(root,file))
	for file in all_jsons:
		basefile = relpath(file,filepath).split(".")[0]
		data = {}
		with open(file,"r") as f:
			data = json.load(f)
		for key in data:
			if not key in all_keys:
				all_keys[key] = 1
		data["filename"] = basefile
		all_data.append(data)
	# Write to (C)SV
	with open(outfile,"w+") as f:
		# Set up Header
		header = ""
		for key in all_keys:
			header += "{}{}".format(key,delimiter)
		header = header[:-1]+"\n" # Skip the last delimiter, finish table
		f.write(header)
		for filedata in all_data:
			line = ""
			for key in all_keys:
				data = "N/A"
				if key in filedata:
					data = filedata[key]
				line += "{}{}".format(data,delimiter)
			line = line[:-1]+"\n"
			f.write(line)
	return


if __name__ == "__main__":
	filepath = sys.argv[1]
	group_to_tsv(filepath)
