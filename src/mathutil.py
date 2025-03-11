"""
	All the math functions to make this work...
"""
# Library imports
import numpy as np
from numpy import (array,ones,zeros,eye,rad2deg,deg2rad,sin,cos,tan,arcsin,arccos,arctan,arctan2,sqrt,argmax,argmin,cross,dot)
from numpy.linalg import (svd,det,norm)

# Local imports



def wahbas_problem(ref_los, body_los):
	"""
		Returns R rotation matrix from body to reference frame
	"""
	A = ref_los.T
	E = body_los.T
	B = A@E.T
	U,S,Vt = svd(B)
	M = eye(3)
	M[2,2] = det(U)*det(Vt.T)
	return U@M@Vt


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


def rand_norm3():
	v = np.random.uniform(-1,1,(3,1))
	return v/norm(v)


def rot_about(a,b,theta):
	a_par_b = (dot(a,b)/dot(b,b))*b
	a_perp_b = a - a_par_b
	w = cross(b,a_perp_b)
	x1 = cos(theta)/np.linalg.norm(a_perp_b)
	x2 = sin(theta)/np.linalg.norm(w)
	a_perp_btheta = np.linalg.norm(a_perp_b)*(x1*a_perp_b+x2*w)
	return array(a_perp_btheta + a_par_b)
