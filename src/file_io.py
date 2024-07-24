# All the code for dealing with reading/writing
import json
from os.path import exists,join,abspath,dirname,basename


# Read in json data
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
