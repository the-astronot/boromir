# Script for finding image mods required to approximate camera image
import cv2 as cv
import numpy as np
from tqdm import tqdm
from scipy.optimize import least_squares
from skimage import exposure


SIFT = cv.SIFT_create()
BF = cv.BFMatcher()


def contrast(img,mult,median=127.5):
	diff = img-median
	return diff*mult+median

def gain(img,mult):
	return img*mult

def vignette(img,level):
	flip = False
	if level == 0:
		return img
	elif level < 0:
		level = np.abs(level)
		flip = True
	rows,cols,channels = img.shape[:3]
	kernel = cv.getGaussianKernel(rows,rows/level)*cv.getGaussianKernel(cols,cols/level).T
	mask = np.abs(kernel/kernel.max())
	if flip:
		mask = 2.0-mask
	mask = np.where(mask>0,mask,0)
	for i in range(channels):
		img[:,:,i] = img[:,:,i]*mask
	return img

def offset(img,value):
	return img+value


def comp_imgs(img1,img2):
	# TODO: Come up with a better metric
	diff = img2-img1
	#mean = np.mean(diff)
	#diffdev = (diff-mean)**2
	#stddev = np.sqrt(np.mean(diffdev))
	#print("Mean is: {}, StdDev is: {}".format(mean,stddev))
	#return np.sum(np.abs(diff))/np.prod(img1.shape[:2])
	#return np.abs(mean)+2*np.abs(stddev)
	#return np.sum([np.sum(np.abs(diff[:2,:2])),np.sum(np.abs(diff[h//2-2:h//2+2,w//2-2:w//2+2]))])
	return diff.flatten()


def build_map(img_gen,img_ref):
	map = np.zeros((256,256,256,4))
	rows,cols,channels = img_gen.shape
	print("Rows: {}, Cols: {}, Chs: {}".format(rows,cols,channels))
	for row in range(rows):
		for col in range(cols):
			gen_color = img_gen[row,col]
			ref_color = img_ref[row,col]
			map_color = map[gen_color[0],gen_color[1],gen_color[2],:3]
			count = map[gen_color[0],gen_color[1],gen_color[2],3]
			if count == 0:
				map[gen_color[0],gen_color[1],gen_color[2],:3] = ref_color
				map[gen_color[0],gen_color[1],gen_color[2],3] = 1
			else:
				map[gen_color[0],gen_color[1],gen_color[2],:3] = (count/(count+1))*map[gen_color[0],gen_color[1],gen_color[2],:3] + (1/(count+1))*ref_color
				map[gen_color[0],gen_color[1],gen_color[2],3] += 1
	print(map)
	return map


def apply_map(img_gen,map):
	rows,cols,channels = img_gen.shape
	for row in range(rows):
		for col in range(cols):
			colors = img_gen[row,col]
			img_gen[row,col] = map[colors[0],colors[1],colors[2],:3].astype(int)
	return img_gen


def find_keypoints(img):
	if len(img.shape) > 2:
		gray = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
	else:
		gray = img
	kp, desc = SIFT.detectAndCompute(gray,None)
	return kp, desc


def img_info(img):
	dimensions = img.shape
	height,width = img.shape[0],img.shape[1]
	if len(dimensions) > 2:
		channels = img.shape[2]
	else:
		channels = 1
	print("Image Dimensions: ({},{}), Channels: {}".format(height,width,channels))
	return


def cvt8to16bit(img):
	return (img*256).astype('uint16')


def cvt16to8bit(img):
	return (img//256).astype('uint8')


def model(img,vals):
	g,c,o = vals
	img_old = img.copy()
	img = offset(img,o)
	img = contrast(img,c)
	img = gain(img,g)
	img = np.where(img<255,np.where(img>0,img,0),255)
	return img


def fun(x,u,y):
	z = (y-model(u,x)).flatten()**2
	#print("z.shape: {}".format(z))
	return z


if __name__ == "__main__":
	MIN_MATCH_COUNT = 120
	image_1 = "approx_test/art1_match_im2_15.png" # The generated image
	image_2 = "approx_test/parth2_artemis.jpg" # The image to match to
	img1 = cv.imread(image_1)
	img2 = cv.imread(image_2)
	img_info(img1)
	print(np.min(img1),np.max(img1))
	img_info(img2)
	print(np.min(img2),np.max(img2))
	kp1,desc1 = find_keypoints(img1)
	kp2,desc2 = find_keypoints(img2)
	print("Finding Matches:")
	matches = BF.knnMatch(desc1,desc2,k=2)
	# Apply ratio test
	good = []
	drawn_good = []
	for m,n in matches:
		if m.distance < 0.75*n.distance:
			good.append(m)
			drawn_good.append([m])
	print("Found {} Matches".format(len(good)))
	if not len(good) > MIN_MATCH_COUNT:
		print("Too few pts found, quitting...")
		img3 = cv.drawMatchesKnn(img1,kp1,img2,kp2,drawn_good,None,flags=cv.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
		cv.imwrite("comp.png",img3)
		exit()
	src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
	dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)
	
	M, mask = cv.findHomography(src_pts, dst_pts, cv.RANSAC,5.0)
	h,w = img2.shape[:2]
	img1 = cv.warpPerspective(img1,M,(w,h))
	#img1 = (img1*256).astype('uint16')
	#img2 = (img2*256).astype('uint16')
	cv.imwrite("img1_aligned.png",img1)

	# Darken all the outlying regions of img2
	img2 = np.where(img1==0,0,img2)

	# Images have been matched, now lets correct!
	# Lets start by blurring both images
	img1b = cv.blur(img1,(5,5))
	img2b = cv.blur(img2,(5,5))

	# Get a sense of the baseline error
	print("Original Score:")
	best_score = comp_imgs(img1,img2)
	print(best_score)

	# Now to set up the modifications
	print("Attempting Modifications:")

	#x0 = np.array([1,1,0])
	#res = least_squares(fun,x0,args=(img1b,img2b),verbose=1)
	#print(res.x)
	#best_values = res.x
	#best_values = [1.06522339, 0.78893892, 0.]
	#best_image = model(img1,best_values)
	#img2 = np.where(img1<5,0,img2)
	#img1 = img1[500:-500,500:-500]
	#img2 = img2[500:-500,500:-500]
	map = build_map(img1,img2)
	best_image = apply_map(img1,map)

	#cv.imwrite("tsiolkovsky_mod.png",img2)

	#best_image = exposure.match_histograms(img1,img2,channel_axis=-1)
	
	#print("Writing Best Image with Score {} to file...".format(best_score))
	#print("Best Values are: {}".format(best_values))
	cv.imwrite("best_mod.png",best_image)

