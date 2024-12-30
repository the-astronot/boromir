#!/bin/python3

# Library Imports
import argparse
import sys
from os.path import abspath,dirname,join,isdir
from functools import partial
import time

# Local Imports
import file_io as fi
from Log import Logger
from error_codes import *


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
	# Add Common Arguments
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
		"--logging",
		type=str,
		default=None,
		help="output logging file"
	)
	parser.add_argument(
		"--blender",
		help="select Blender config file from configs/",
		default=join(BLENDER_CONF_DIR,"blender.conf")
	)
	parser.add_argument(
		"--camera",
		help="select camera config file from configs/cameras/",
		default=join(CAMERA_DIR,"testcam.json")
	)
	parser.add_argument(
		"--log_level",
		help="level of logging from {0..3}->{None..Full}",
		type=int,
		choices=[0,1,2,3],
		default=0
	)
	parser.add_argument(
		"--fo",
		"--forceoverwrite",
		help="force overwrite log file",
		action="store_true"
	)

	# Add SubParsers
	subparsers = parser.add_subparsers(help=None,
																		required=True,
																		dest='command')
	subparsers = build_traj_parser(subparsers)
	subparsers = build_random_parser(subparsers)
	subparsers = build_test_parser(subparsers)

	return parser


def build_traj_parser(parser):
	"""
		Handles arguments related specifically to the trajectory generator
	"""
	parser_traj = parser.add_parser(
		"trajectory",
		help="create images from state data"
	)
	# Add Trajectory-Specific Arguments
	partial_fc = partial(fi.check_for_file,dirname=TRAJECTORY_DIR)
	parser_traj.add_argument(
		"filename",
		help="file of <type of run> in configs/trajectories/",
		type=partial(partial_fc)
	)
	parser_traj.add_argument(
		"--job",
		help="name to give the output directory",
		type=str,
		default=None
	)
	parser_traj.add_argument(
		"--outdir",
		help="directory to store the images to",
		default=IMG_DIR,
		type=fi.check_for_dir
	)

	return parser


def build_random_parser(parser):
	"""
		Handles arguments related specifically to the random generator
	"""
	parser_random = parser.add_parser(
		"random",
		help="create images from random poses"
	)
	# Add Random-Specific Arguments
	parser_random.add_argument(
		"filename",
		help="file of <type of run> in configs/random_poses/",
		type=argparse.FileType("r"),
		default=join(RANDOM_POSE_DIR,"test.csv")
	)
	parser_random.add_argument(
		"--num_imgs",
		help="Number of random images to generate",
		type=int
	)
	return parser


def build_test_parser(parser):
	"""
		Handles arguments related specifically to running tests
	"""
	parser_test = parser.add_parser(
		"test",
		help="run test cases"
	)
	# Add Test-Specific Arguments
	parser_test.add_argument(
		"modules"
	)
	return parser


def process_trajectory(args):
	# Perform required checks and launch job
	log("CONFIGURATION",0)
	log("Job Name: {}".format(args.job),0)
	log("Job Type: Trajectory",0)
	log("Input File: {}".format(args.filename),0)
	log("Output Dir: {}".format(args.outdir),0)
	log("Camera: {}".format(args.camera),0)
	log("Blender Config: {}".format(args.blender),0)
	log("[Log File, Level, Overwrite]: [{}, {}, {}]".format(args.logging,
																											args.log_level,
																											args.fo),
																											0)
	# Check input file for errors and create list of poses
	ret,poses = fi.read_traj_file(args.filename)
	if ret != TrajFileReadError.SUCCESS:
		error("ERROR {}: Reading Trajectory File, Exiting...".format(ret))
		return
	# Run job
	for pose in poses:
		log(pose,0)

	return


def process_random(args):
	# Perform required checks and launch job
	return


def process_test(args):
	# Run tests
	return

# Supplying the functions with a less clunky logger
def log(msg,level,also_print=False):
	LOGGER.log(msg,level,also_print=also_print)

def error(msg):
	LOGGER.error(msg)


# GLOBAL VARS
VERSION = "1.0.0-alpha"
BASE_DIR = dirname(dirname(abspath(__file__)))
CONFIG_DIR = join(BASE_DIR,"configs")
CAMERA_DIR = join(CONFIG_DIR,"cameras")
BLENDER_CONF_DIR = join(CONFIG_DIR,"blender")
TRAJECTORY_DIR = join(CONFIG_DIR,"trajectories")
RANDOM_POSE_DIR = join(CONFIG_DIR,"random_poses")
IMG_DIR = join(BASE_DIR,"outimages")
LOGGER=None
# END GLOBAL VARS
# BOROMIR Main Function
if __name__ == "__main__":
	parser = build_parser()
	args = parser.parse_args()
	LOGGER = Logger(args.logging,
									level=args.log_level,
									verbose=args.verbose,
									force_overwrite=args.fo)
	if args.command == "trajectory":
		process_trajectory(args)
	elif args.command == "random":
		process_random(args)
	elif args.command == "test":
		process_test(args)
	else:
		print(parser.print_help())
