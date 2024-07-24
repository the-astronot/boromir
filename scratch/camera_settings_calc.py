import numpy as np
from numpy import array,zeros,sin,cos,tan,deg2rad,arctan


def from_sensor_and_focal_length(sensor_size,num_pixels,focal_length):
	mu = sensor_size/num_pixels
	K = array([[focal_length/mu[0],0,(num_pixels[0]-1)/2],
						[0,focal_length/mu[1],(num_pixels[1]-1)/2],
						[0,0,1]])
	return K


def from_fov_and_num_pixels(fov,num_pixels):
	fh = calc_fh(fov)
	K = array([[fh[0]*num_pixels[0],0,(num_pixels[0]-1)/2.0],
						[0,fh[1]*num_pixels[1],(num_pixels[1]-1)/2.0],
						[0,0,1]])
	return K


def calc_AFOV(sensor_size,focal_length):
	return 2*arctan(sensor_size/(2*focal_length))


def calc_fh(fov):
	return 1/(2*tan(fov/2))


def calculate_K_matrix(sensor_size,
											 num_pixels,
											 camera_fov,
											 focal_length):
	# Setup/checking
	if sensor_size is not None:
		sensor_size = array(sensor_size,dtype=float)
	if num_pixels is not None:
		num_pixels = array(num_pixels,dtype=float)
	if camera_fov is not None:
		camera_fov = array(camera_fov,dtype=float)
	if focal_length is not None:
		focal_length = float(focal_length)
	# Determine from sensor and focal length
	if sensor_size is not None and \
			num_pixels is not None and \
			focal_length is not None:
		return from_sensor_and_focal_length(sensor_size,num_pixels,focal_length)
	# Determine from fov and num_pixels
	if camera_fov is not None and \
			num_pixels is not None:
		return from_fov_and_num_pixels(camera_fov,num_pixels)


if __name__ == '__main__':
	## INPUTS
	# Sensor Data
	sensor_size = None #[0.06,0.06] # (meters,meters)
	num_pixels = [3900,3900] # (unitless,unitless)
	# FoV Data
	camera_fov = [12.5,12.5] # (units,units)
	camera_fov_units = "degrees"
	# Lens Data
	focal_length = .250 # meters

	## PRE-PROCESSING
	# Convert degrees to radians
	if camera_fov_units.lower()[0] == "d" and camera_fov is not None:
		camera_fov = deg2rad(array(camera_fov,dtype=float))

	K = calculate_K_matrix(sensor_size,num_pixels,camera_fov,focal_length)
	print("BEHOLD, THE K MATRIX:\n{}".format(K))
