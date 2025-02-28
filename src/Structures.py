# Library imports
import numpy as np
from mathutil import *

# Local imports



class Quaternion():
	"""
		Quaternions are here defined as Scalar-First
	"""
	s = 1.0
	v = zeros(3)
	
	def __init__(self,s=None,v=None):
		if s is not None:
			self.s = np.float32(s)
		if v is not None:
			self.v = array(v,dtype=np.float32)
		self.normalize()

	def __str__(self):
		return "[{:.5f}, {:.5f}, {:.5f}, {:.5f}]".format(self.s,self.v[0],self.v[1],self.v[2])
	
	def __repr__(self):
		return self.__str__()

	def toDCM(self):
		dcm = zeros((3,3))
		dcm[0,0] = self.s**2 + self.v[0]**2 - self.v[1]**2 - self.v[2]**2
		dcm[0,1] = 2*(self.v[0]*self.v[1]+self.v[2]*self.s)
		dcm[0,2] = 2*(self.v[0]*self.v[2]-self.v[1]*self.s)
		dcm[1,0] = 2*(self.v[0]*self.v[1]-self.v[2]*self.s)
		dcm[1,1] = self.s**2 - self.v[0]**2 + self.v[1]**2 - self.v[2]**2
		dcm[1,2] = 2*(self.v[1]*self.v[2]+self.v[0]*self.s)
		dcm[2,0] = 2*(self.v[0]*self.v[2]+self.v[1]*self.s)
		dcm[2,1] = 2*(self.v[1]*self.v[2]-self.v[0]*self.s)
		dcm[2,2] = self.s**2 - self.v[0]**2 - self.v[1]**2 + self.v[2]**2
		return dcm

	def fromDCM(self,dcm):
		q1_sq = 0.25*(1+dcm[0,0]-dcm[1,1]-dcm[2,2])
		q2_sq = 0.25*(1-dcm[0,0]+dcm[1,1]-dcm[2,2])
		q3_sq = 0.25*(1-dcm[0,0]-dcm[1,1]+dcm[2,2])
		qs_sq = 0.25*(1+dcm[0,0]+dcm[1,1]+dcm[2,2])
		max_arg = argmax(array([q1_sq,q2_sq,q3_sq,qs_sq]))
		if (max_arg == 0):
			mod = 1/(4*sqrt(q1_sq))
			self.v[0] = mod*(4*q1_sq)
			self.v[1] = mod*(dcm[0,1]+dcm[1,0])
			self.v[2] = mod*(dcm[2,0]+dcm[0,2])
			self.s = mod*(dcm[1,2]-dcm[2,1])
		elif (max_arg == 1):
			mod = 1/(4*sqrt(q2_sq))
			self.v[0] = mod*(dcm[0,1]+dcm[1,0])
			self.v[1] = mod*(4*q2_sq)
			self.v[2] = mod*(dcm[1,2]+dcm[2,1])
			self.s = mod*(dcm[2,0]-dcm[0,2])
		elif (max_arg == 2):
			mod = 1/(4*sqrt(q3_sq))
			self.v[0] = mod*(dcm[2,0]+dcm[0,2])
			self.v[1] = mod*(dcm[1,2]+dcm[2,1])
			self.v[2] = mod*(4*q3_sq)
			self.s = mod*(dcm[0,1]-dcm[1,0])
		elif (max_arg == 3):
			mod = 1/(4*sqrt(qs_sq))
			self.v[0] = mod*(dcm[1,2]-dcm[2,1])
			self.v[1] = mod*(dcm[2,0]-dcm[0,2])
			self.v[2] = mod*(dcm[0,1]-dcm[1,0])
			self.s = mod*(4*qs_sq)
		#print(self.s,self.v)
		self.normalize()

	def normalize(self):
		total = sqrt(self.s**2+self.v[0]**2+self.v[1]**2+self.v[2]**2)
		self.s = self.s/total
		self.v = self.v/total

	def toArray(self):
		return array([self.s,self.v[0],self.v[1],self.v[2]])
	
	def fromArray(self,arr):
		"""
			Assumes that array is set up like: [s,v1,v2,v3]
		"""
		self.s = float(arr[0])
		self.v = np.array(arr[1:4],dtype=float)


def quat_mult(q1,q2):
	"""
		Multiply q1 by q2
	"""
	q3 = Quaternion()
	q3.s = q1.s*q2.s-(np.sum(q1.v*q2.v))
	q3.v = q1.s*q2.v + q2.s*q1.v + np.cross(q1.v,q2.v)
	return q3



class State():
	"""
		Holds onto state information
	"""
	position = zeros(3)
	attitude = Quaternion()

	def __init__(self,position=None,attitude=None):
		if position is not None:
			self.position = array(position,dtype=float)
		if attitude is not None:
			self.attitude = attitude

	def copy(self):
		new_state = State()
		new_state.position = self.position
		new_state.attitude = Quaternion(self.attitude.s,self.attitude.v)
		return new_state
