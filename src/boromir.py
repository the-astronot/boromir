#!/bin/python3


# Imports
import argparse
import sys
from os.path import abspath,dirname,join

# Local Imports


def build_parser():
	"""
		Handles all the argument parsing.
	"""
	# Build Argparse
	parser = argparse.ArgumentParser(
		prog="boromir",
		description="BOROMIR: The Blender-based Open-source Repository for Opnav\
									Moon Image Rendering"
	)
	# Add Arguments
	parser.add_argument(
		"--version",
		action="version",
		version="%(prog)s {}".format(VERSION)
	)
	parser.add_argument(
		"-v",
		"--verbose",
		action="store_true",
		help="toggles output to terminal"
	)
	parser.add_argument(
		"type",
		help="type of run",
		choices=["trajectory","random"]
	)
	parser.add_argument(
		"filename",
		help="file of <type of run> in configs/pose_data/",
		type=argparse.FileType("r")
	)
	parser.add_argument(
		"--output",
		type=argparse.FileType("w+"),
		default=sys.stdout,
		help="output logging file"
	)
	parser.add_argument(
		"--blender",
		help="select Blender config file from configs/",
		default="blender.conf"
	)
	parser.add_argument(
		"--camera",
		help="select camera config file from configs/cameras/",
		default="testcam.json"
	)
	parser.add_argument(
		"--log_level",
		help="level of logging from {0..3}->{None..Full}",
		choices=[0,1,2,3],
		default=0
	)

	return parser

# GLOBAL VARS
VERSION = "1.0.0"
BASE_DIR = dirname(dirname(abspath(__file__)))
CONFIG_DIR = join(BASE_DIR,"configs")
CAMERA_DIR = join(CONFIG_DIR,"cameras")
BLENDER_CONF_DIR = join(CONFIG_DIR,"blender")
POSE_DIR = join(BASE_DIR,"pose_data")
# BOROMIR Main Function
if __name__ == "__main__":
	parser = build_parser()
	args = parser.parse_args()
