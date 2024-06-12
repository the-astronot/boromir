"""
	All the math functions to make this work...
"""
from numpy import (array,ones,zeros,eye,rad2deg,deg2rad,sin,cos,tan,arcsin,arccos,arctan,arctan2,sqrt,argmax,argmin)
from numpy.linalg import (svd,det)


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
