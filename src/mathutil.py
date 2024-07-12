"""
	All the math functions to make this work...
"""
from numpy import (array,ones,zeros,eye,rad2deg,deg2rad,sin,cos,tan,arcsin,arccos,arctan,arctan2,sqrt,argmax,argmin,cross,dot)
from numpy.linalg import (svd,det,norm)


def wahbas_problem(ref_los, body_los):
	"""
		Returns R rotation matrix from body to reference frame
	"""
	A = ref_los.T
	E = body_los.T
	B = A@E.T
	U,S,V = svd(B)
	M = eye(3)
	M[2,2] = det(U)*det(V.T)
	return U@M@V


def within(value,target,epsilon=10e-5):
	delta = abs(value-target)
	if delta < epsilon:
		return True
	return False


def angle_betw_los(vec1,vec2):
	# Finds angle (in radians) between 2 LoS vectors
	if not within(norm(vec1),1.0):
		vec1 = vec1/norm(vec1)
	if not within(norm(vec2),1.0):
		vec2 = vec2/norm(vec2)
	angle = arccos(vec1.T@vec2)
	return float(angle)
