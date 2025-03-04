# Library imports
import numpy as np

# Local imports
import gkmethod as gk
from Log import debug,info


# TODO: Write a function to combine similar poses
def combine_poses(poses,camera,threshold=.7,ra=360):
	if len(poses) == 0:
		return []
	comb_poses = []
	comb_maps = []
	cameras = []
	#info("Base Camera Position: {}".format(camera.state.position))
	for i,pose in enumerate(poses):
		added = False
		fov_max = np.sqrt(camera.FOV_y**2+camera.FOV_x**2)
		coverage = gk.get_coverage_from_state(pose.cam_state,fov_max,ra)
		coverage = np.where(coverage>0,1,0)
		for j,exist_pose in enumerate(comb_poses):
			# Compare: if match, add pose and continue
			if compare_poses(coverage,comb_maps[j],threshold=threshold):
				debug("Combined 2 Maps!")
				comb_poses[j].append(pose)
				comb_maps[j] = np.where(comb_maps[j]+coverage>0,1,0)
				added = True
				break
		if not added:
			debug("Added new map!")
			comb_poses.append([pose])
			comb_maps.append(coverage)
	for map in comb_maps:
		cameras.append(gk.get_camera_from_coverage(map,camera.copy()))
		#info("Mesh Camera Position: {}".format(cameras[-1].state.position))
	return comb_poses, cameras

def compare_poses(map1,map2,threshold):
	"""
		Checks whether visible maps for separate poses should be combined
	"""
	total1 = np.sum(map1)
	total2 = np.sum(map2)
	if total1 == 0 or total2 == 0:
		if total1 != total2:
			return False
		return True
	mask1 = np.where(map1>0,1,0)
	mask2 = np.where(map2>0,1,0)
	union1 = np.sum(map1*mask2)
	union2 = np.sum(map2*mask1)
	if (union1/total1)>threshold and (union2/total2)>threshold:
		return True 
	return None
