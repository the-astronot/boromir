# Script for finding image mods required to approximate camera image
import cv2 as cv
import numpy as np
from tqdm import tqdm


SIFT = cv.SIFT_create()
BF = cv.BFMatcher()


def contrast(img,mult,median=127.5):
	diff = img-median
	return diff*mult+median

def gain(img,mult):
	return img*mult

def vignette(img,level,strength):
	flip = False
	if level == 0:
		return img
	elif level < 0:
		level = np.abs(level)
		flip = True
	if strength < 0:
		strength = 0
	rows,cols,channels = img.shape[:3]
	kernel = cv.getGaussianKernel(rows,rows/level)*cv.getGaussianKernel(cols,cols/level).T
	mask = np.abs(kernel/kernel.max())
	diff = mask-1.0
	mask = 1.0+diff*strength
	if flip:
		mask = 2.0-mask
	mask = np.where(mask>0,mask,0)
	for i in range(channels):
		img[:,:,i] = img[:,:,i]*mask
	return img


def comp_imgs(img1,img2):
	# TODO: Come up with a better metric
	diff = img2-img1
	mean = np.mean(diff)
	diffdev = (diff-mean)**2
	stddev = np.sqrt(np.mean(diffdev))
	print("Mean is: {}, StdDev is: {}".format(mean,stddev))
	#return np.sum(np.abs(diff))/np.prod(img1.shape[:2])
	#return np.abs(mean)+2*np.abs(stddev)
	return np.sum([np.sum(np.abs(diff[:2,:2])),np.sum(np.abs(diff[h//2-2:h//2+2,w//2-2:w//2+2]))])


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


if __name__ == "__main__":
	MIN_MATCH_COUNT = 120
	image_1 = "approx_test/tree_1.jpg" # The generated image
	image_2 = "approx_test/tree_1_modded.jpg" # The image to match to
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

	# Images have been matched, now lets correct!
	# Lets start by blurring both images
	#img1 = cv.blur(img1,(5,5))
	#img2 = cv.blur(img2,(5,5))

	# Get a sense of the baseline error
	print("Original Score:")
	best_score = comp_imgs(img1,img2)
	print(best_score)

	# Now to set up the modifications
	print("Attempting Modifications:")
	# base_values
	search_gain = [0.25,0.5,1,1.5,2,3]
	search_contrast = [0.5,1,1.5,2]
	search_vignette = [0,2,4]
	search_vignette_str = [0,1,2]
	best_values = [1,0,1.0,0.0,0.0]
	best_image = img1.copy()
	stable_score = 15
	num_iterations = 250
	"""
	for i in search_gain:
		for j in search_contrast:
			for k in search_vignette:
				for l in search_vignette_str:
					gain_mult = i
					contrast_mult = j
					vignette_level = k
					vignette_str = l
					modded_img = img1.copy()
					modded_img = gain(modded_img,gain_mult)
					modded_img = contrast(modded_img,contrast_mult)
					modded_img = vignette(modded_img,vignette_level,vignette_str)
					new_score = comp_imgs(modded_img,img2)
					if new_score < best_score:
						print("\tNew Best Score!: {}".format(new_score))
						best_score = new_score
						best_image = modded_img.copy()
						best_values = [gain_mult,contrast_mult,vignette_level,vignette_str]
	print("Best values: {}".format(best_values))
	"""
	for i in range(num_iterations):
		modded_img = img1.copy()
		print("Attempt {:03d}: ".format(i),end="")
		progress = float(i)/float(num_iterations)
		if (np.random.uniform(0,1)<progress):
			print("BEST Guess, Progress {:02d}% ".format(int(progress*100)),end="")
			gain_mult = best_values[0] + np.random.normal(0,(.1/progress))
			contrast_mult = best_values[1] + np.random.normal(0,.1/progress)
			vignette_level = best_values[2] + np.random.normal(0,.1/progress)
			vignette_str = max(best_values[3] + np.random.normal(0,.1/progress),0)
		else:
			print("RAND Guess, Progress {:02d}% ".format(int(progress*100)),end="")
			if np.random.uniform(0,1)<progress:
				choice = np.random.choice(4)
				gain_mult,contrast_mult,vignette_level,vignette_str = best_values
				if choice == 0:
					gain_mult = np.random.uniform(0,5)
				elif choice == 1:
					contrast_mult = np.random.uniform(0,5)
				elif choice == 2:
					vignette_level = np.random.uniform(-5,5)
				else:
					vignette_str = np.random.uniform(0,2)
			else:
				gain_mult = np.random.uniform(0,5)
				contrast_mult = np.random.uniform(0,5)
				vignette_level = np.random.uniform(-5,5)
				vignette_str = np.random.uniform(0,2)

		modded_img = gain(modded_img,gain_mult)
		modded_img = contrast(modded_img,contrast_mult)
		modded_img = vignette(modded_img,vignette_level,vignette_str)
		new_score = comp_imgs(modded_img,img2)
		if new_score < best_score:
			print("\tNew Best Score!: {}".format(new_score))
			best_score = new_score
			best_image = modded_img.copy()
			best_values = [gain_mult,contrast_mult,vignette_level,vignette_str]
	print("Writing Best Image with Score {} to file...".format(best_score))
	print("Best Values are: {}".format(best_values))
	cv.imwrite("best_mod.png",best_image)
	cv.imwrite("vignette_test.png",vignette(img1,2.5,0.4))

