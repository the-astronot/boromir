import os
os.environ["OPENCV_IO_MAX_IMAGE_PIXELS"] = pow(2,40).__str__()
import cv2
import numpy as np
import struct
from tqdm import tqdm

typs = ["short","int","float","double"]

def open_dem(filename,typ):
	"""
		Converts image file to bin.
	"""
	assert(typ in typs)
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
				if np.isnan(value):
					value = 0
				if typ=="short" or typ=="int":
					value = int(round(value,0))
				if typ == "short":
					f.write(struct.pack("h",value))
				elif typ == "int":
					f.write(struct.pack("i",value))
				elif typ == "float":
					f.write(struct.pack("f",value))
				elif typ == "double":
					f.write(struct.pack("d",value))
		f.close()
		del img
	return


if __name__ == "__main__":
	filenames = ["ldem_87s_5mpp.tif",
							"Lunar_LRO_LOLA_Global_LDEM_118m_Mar2014.tif"]
	types = ["float",
					"short"]
	for i in range(len(filenames)):
		open_dem(filenames[i],types[i])
