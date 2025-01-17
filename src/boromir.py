#!/bin/python3
################################################################################
##                                                                            ##
##   ####   ###  ####   ###  #   # ##### ####                                 ##
##   #   # #   # #   # #   # ## ##   #   #   #                                ##
##   ####  #   # ####  #   # # # #   #   ####                                 ##
##   #   # #   # #  #  #   # #   #   #   #  #                                 ##
##   ####   ###  #   #  ###  #   # ##### #   #                                ##
##                                                                            ##
################################################################################
## Blender-based Open-source Repository for Opnav Image Rendering             ##
################################################################################
## Author: Max Marshall                                                       ##
################################################################################
##                                                                            ##
##  This is free and unencumbered software released into the public domain.   ##
##                                                                            ##
##  Anyone is free to copy, modify, publish, use, compile, sell, or           ##
##  distribute this software, either in source code form or as a compiled     ##
##  binary, for any purpose, commercial or non-commercial, and by any         ##
##  means.                                                                    ##
##                                                                            ##
##  In jurisdictions that recognize copyright laws, the author or authors     ##
##  of this software dedicate any and all copyright interest in the           ##
##  software to the public domain. We make this dedication for the benefit    ##
##  of the public at large and to the detriment of our heirs and              ##
##  successors. We intend this dedication to be an overt act of               ##
##  relinquishment in perpetuity of all present and future rights to this     ##
##  software under copyright law.                                             ##
##                                                                            ##
##  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,           ##
##  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF        ##
##  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.    ##
##  IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR         ##
##  OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,     ##
##  ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR     ##
##  OTHER DEALINGS IN THE SOFTWARE.                                           ##
##                                                                            ##
##  For more information, please refer to <https://unlicense.org/>            ##
##                                                                            ##
################################################################################

# Library Imports
import argparse
import sys
from os.path import abspath,dirname,join,isdir,basename
from functools import partial

# Local Imports
import file_io as io
import trajectory_gen as traj_gen
from Log import LOGGER,critical,warning,info,debug
from error_codes import *
from paths import *
sys.path.append(TESTS_DIR)
from test_runner import test_main


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
	## VERSION
	parser.add_argument(
		"--version",
		action="version",
		version="%(prog)s {}".format(VERSION)
	)
	## VERBOSE
	parser.add_argument(
		"-v",
		"--verbose",
		action="store_true",
		help="toggles output to terminal"
	)
	## LOG FILE
	log_check = partial(io.basename2path,path=LOG_DIR)
	parser.add_argument(
		"--logging",
		default=None,
		help="output logging file",
		type=partial(log_check)
	)
	## BLENDER CONFIG FILE
	blender_check = partial(io.basename2path,path=BLENDER_CONF_DIR)
	parser.add_argument(
		"--blender",
		help="select Blender config file from configs/",
		default=join(BLENDER_CONF_DIR,"blender.json"),
		type=partial(blender_check)
	)
	## CAMERA CONFIG FILE
	cam_check = partial(io.basename2path,path=CAMERA_DIR)
	parser.add_argument(
		"--camera",
		help="select camera config file from configs/cameras/",
		default=join(CAMERA_DIR,"testcam.json"),
		type=partial(cam_check)
	)
	## LOG LEVEL
	parser.add_argument(
		"--log_level",
		help="level of logging from {0..3}->{Critical,Warning,Info,Debug}",
		type=int,
		choices=[0,1,2,3],
		default=2
	)
	## FORCE OVERWRITE LOG FILE
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
	partial_fc = partial(io.check_for_file,dirname=TRAJECTORY_DIR)
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
		type=io.check_for_dir
	)
	parser_traj.add_argument(
		"--disable_gkm",
		help="disables sharing meshes (can increase run-time and artifacts)",
		action="store_true"
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
	parser_random.add_argument(
		"--disable_gkm",
		help="disables sharing meshes (can increase run-time and artifacts)",
		action="store_true"
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
		"--modules"
	)
	return parser


def process_trajectory(args):
	# Perform required checks and launch job
	
	# Perform file checks
	args.camera = io.check_for_file(args.camera,CAMERA_DIR)
	args.blender = io.check_for_file(args.blender,BLENDER_CONF_DIR)
	if args.job is None: # If not supplied, job name is filename w/o ext
		args.job = basename(args.filename).rsplit(".")[0]

	# Confirm job name/image directory
	status = io.try_makedir(join(args.outdir,args.job))
	while status != 0:
		renamed = (io.ask_overwrite(args.job,args.outdir))
		if renamed == args.job:
			status = 0
			continue
		status = io.try_makedir(join(dirname(renamed),basename(renamed)))
		if status == 0:
			args.job = basename(renamed)
			args.outdir = abspath(dirname(renamed))

	# Print configs
	traj_gen.print_config(args)

	# Check input file for errors and create list of poses
	ret,poses = io.read_traj_file(args.filename)
	if ret != TrajFileReadError.SUCCESS:
		critical("ERROR {}: Reading Trajectory File, Exiting...".format(ret))
		return
	
	# Run job
	status = traj_gen.run(args,poses)
	if status != 0:
		critical("trajectory_gen.run returned error code {}".format(status))
	else:
		info("Finished run")
	return status


def process_random(args):
	# Perform required checks and launch job
	return


def process_test(args):
	# Run tests
	test_main()
	return


def main():
	parser = build_parser()
	args = parser.parse_args()
	LOGGER.re_init(args.logging,
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
	return


# GLOBAL VARS
VERSION = "1.0.0"
# END GLOBAL VARS


# BOROMIR Main Function
if __name__ == "__main__":
	main()
