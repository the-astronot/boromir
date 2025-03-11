# Library imports
import numpy as np
from numpy.linalg import norm

# Local imports
import gkmethod as gk
from Log import debug,info


# TODO: Write a function to combine similar poses
def combine_poses(poses,camera,threshold=.9,ra=360):
	if len(poses) == 0:
		return [], []
	comb_poses = []
	comb_maps = []
	cameras = []
	# Sort poses by distance from Moon
	poses.sort(key=lambda x:norm(x.cam_state.position),reverse=True)
	#info("Base Camera Position: {}".format(camera.state.position))
	for i,pose in enumerate(poses):
		added = False
		fov_max = max([camera.FOV_y,camera.FOV_x])
		coverage = gk.get_coverage_from_state(pose.cam_state,fov_max,ra)
		coverage = np.where(coverage>0,1,0)
		for j,exist_pose in enumerate(comb_poses):
			if threshold >= 1.0:
				# If threshold this high, only allow perfect matches
				this_attitude = pose.cam_state.attitude
				other_attitude = exist_pose[0].cam_state.attitude
				this_position = pose.cam_state.position
				other_position = exist_pose[0].cam_state.position
				if np.all(this_attitude==other_attitude) and np.all(this_position==other_position):
					comb_poses[j].append(pose)
					added = True
					break
			# Compare: if match, add pose and continue
			elif compare_poses(coverage,comb_maps[j],threshold):
				combined_coverage = np.where(comb_maps[j]+coverage>0,1,0)
				debug("Added {} to Map {}, now {} squares!".format(i,j,np.sum(combined_coverage)))
				comb_poses[j].append(pose)
				comb_maps[j] = combined_coverage
				added = True
				break
		if not added:
			debug("Converted {} to Map {} with {} squares!".format(i,len(comb_maps),np.sum(coverage)))
			comb_poses.append([pose])
			comb_maps.append(coverage)
	for i,map in enumerate(comb_maps):
		if threshold >= 1.0:
			# Replace camera pose with known pose
			new_cam = camera.copy()
			new_cam.state = comb_poses[i][0].cam_state.copy()
			cameras.append(new_cam)
		else:
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
		#debug("New Map Union: {}%, Old Map Union: {}%".format((union1/total1)*100,(union2/total2)*100))
		return True 
	return False
