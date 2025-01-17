# Library imports
import cv2
import numpy as np
import sys
from os.path import dirname,abspath,join
import subprocess as sp

sys.path.append(join(dirname(dirname(abspath(__file__))),"src"))
# Local imports
from paths import *


def construct_mosaic(shape):
	img = np.zeros(shape,dtype=int)
	return img


def prev_main():
	img_data = []
	for img in imgs:
		img_data.append(cv2.imread(join(MAP_DIR,img)))
	mosaic = construct_mosaic((23040,46080,3))
	side_length = 11520
	for i in range(4):
		for j in range(2):
			print(i*2+j)
			mosaic[j*side_length:(j+1)*side_length,i*side_length:(i+1)*side_length,:] = img_data[j*4+i][:,:,:]
	cv2.imwrite(join(MAP_DIR,"moon_albedo.png"),mosaic)
	small_mosaic = cv2.resize(mosaic,(2048,1024))
	cv2.imwrite(join(MAP_DIR,"small_Moon_albedo.png"),small_mosaic)


def download_img(filename):
	"""
		Use wget to download a file
	"""
	sp.run(["wget","-c","-P",SAVEDIR,"--tries=0","{}{}".format(link,filename),"--show-progress","--random-wait","-a","img.log"])


def fix_map(img,nsbounds):
	height,width = img.shape
	mask = np.where(img>0,1,0)
	min_noise,max_noise = [-10,11]
	# Replace lack of data at North Pole
	top = nsbounds[0]
	top_avg = np.average(img[top:top+10],weights=mask[top:top+10]) 
	#print(top_avg)
	img[:top+1,:] = top_avg + np.random.randint(min_noise,max_noise,(top+1,width))
	# Replace lack of data at South Pole
	bottom = nsbounds[1]-1
	bottom_avg = np.average(img[bottom-10:bottom],weights=mask[bottom-10:bottom])
	#print(bottom_avg)
	img[bottom-1:,:] = bottom_avg + np.random.randint(min_noise,max_noise,(height-(bottom-1),width))

	return img


def main():
	mosaic_shape = (13680,27360,3)
	tile_size = (int(mosaic_shape[1]/4),int((7/9)*(mosaic_shape[1]/4)))
	print("Tile Size is: {}".format(tile_size))
	mosaic = np.zeros(mosaic_shape)
	bound_70 = [tile_size[0]-tile_size[1],tile_size[0]+tile_size[1]]
	for i,wavelength in enumerate(wavelengths):
		for j,img in enumerate(imgs):
			filename = img.replace("WAVELENGTH",str(wavelength))
			# Download image
			download_img(filename)
			# Read Image
			image = cv2.imread(join(SAVEDIR,filename),flags=0)
			res_image = cv2.resize(image,tile_size,interpolation=cv2.INTER_CUBIC)
			# Calculate Bounds
			north_bounds = [bound_70[0],tile_size[0]]
			south_bounds = [tile_size[0],bound_70[1]]
			nsbounds = [north_bounds,south_bounds][j//4]
			ewbounds = [(j%4)*tile_size[0],((j%4)+1)*tile_size[0]]
			#print(nsbounds,ewbounds)
			mosaic[nsbounds[0]:nsbounds[1],ewbounds[0]:ewbounds[1],i] = res_image
		mosaic[:,:,i] = fix_map(mosaic[:,:,i],bound_70)
	cv2.imwrite("moon_mosaic.png",mosaic)
	return


# Globals vars
SAVEDIR = join(MAP_DIR,"WAC")
link = "https://pds.lroc.asu.edu/data/LRO-L-LROC-5-RDR-V1.0/LROLRC_2001/EXTRAS/BROWSE/WAC_HAPKE/"
imgs = [
	"WAC_HAPKE_WAVELENGTHNM_E350N2250.TIF",
	"WAC_HAPKE_WAVELENGTHNM_E350N3150.TIF",
	"WAC_HAPKE_WAVELENGTHNM_E350N0450.TIF",
	"WAC_HAPKE_WAVELENGTHNM_E350N1350.TIF",
	"WAC_HAPKE_WAVELENGTHNM_E350S2250.TIF",
	"WAC_HAPKE_WAVELENGTHNM_E350S3150.TIF",
	"WAC_HAPKE_WAVELENGTHNM_E350S0450.TIF",
	"WAC_HAPKE_WAVELENGTHNM_E350S1350.TIF"
]
wavelengths = [
	415,
	566,
	643
]

if __name__ == "__main__":
	main()
