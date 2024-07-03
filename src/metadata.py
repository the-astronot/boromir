import json
from os.path import join


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


def create_metadata(config,state_idx):
	# Spitting out all of the metadata into a file
	state_data = config["STATES"][state_idx]
	filename = state_data["NAME"]
	md_file = filename.split(".")[0]+".json"
	data = {}
	## World Data
	data = get_data(data,"Time (s)",state_data,"TIME")
	# Sun
	data = get_data(data,"SUN LoS",state_data,"SUN")
	# Earth
	data = get_data(data,"Earth Pos (m)",state_data,"EARTH/POS")
	data = get_data(data,"Earth Quat (s)",state_data,"EARTH/QUAT/s")
	data = get_data(data,"Earth Quat (v)",state_data,"EARTH/QUAT/v")
	## SC/CAM 6-DOF
	data = get_data(data,"SC Pos (m)",state_data,"SC/POS")
	data = get_data(data,"SC Quat (s)",state_data,"SC/QUAT/s")
	data = get_data(data,"SC Quat (v)",state_data,"SC/QUAT/v")
	data = get_data(data,"SC LoS",state_data,"SC/LOS")
	data = get_data(data,"Cam Pos (m)",state_data,"CAM/POS")
	data = get_data(data,"Cam Quat (s)",state_data,"CAM/QUAT/s")
	data = get_data(data,"Cam Quat (v)",state_data,"CAM/QUAT/v")
	data = get_data(data,"Cam LoS",state_data,"CAM/LOS")
	## Camera Settings
	data = get_data(data,"FOV X (rad)",config,"FOV_x")
	data = get_data(data,"FOV Y (rad)",config,"FOV_y")
	data = get_data(data,"Nrows",config,"Nrows")
	data = get_data(data,"Ncols",config,"Ncols")
	## Render Settings

	with open(join(config["OUTDIR"],md_file),"w+") as f:
		json.dump(data,f,indent=2)
	return