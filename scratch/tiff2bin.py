import os
os.environ["OPENCV_IO_MAX_IMAGE_PIXELS"] = pow(2,40).__str__()
import cv2
import math
import struct
from tqdm import tqdm

def open_dem(filename):
	"""
		Reads in the TIF DEM file, converts to bin for easy parsing,
		without having to keep the whole thing in memory. Defines 
		width and height of the sphere in pixels.
	"""
	bin_name = filename.replace(".tif",".bin")
	if not os.path.exists(bin_name):
		print("Loading Img File. This may take a while...")
		img = cv2.imread(filename,2)
		print("Image Loaded!")
		height, width = img.shape
		f = open(bin_name,"wb+")
		for j in tqdm(range(height)):
			for i in range(width):
				value = img[j][i]
				if math.isnan(value):
					value = 0
				value = int(round(value,0))
				f.write(struct.pack("h",value))
		f.close()
		del img
	return


if __name__ == "__main__":
	filename = "../maps/ldem_87s_5mpp.tif"
	open_dem(filename)
