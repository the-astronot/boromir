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


	def fromDCM(self,dcm,k=0.25):
		# Calculate the tmp vars
		tmps = 1 + dcm[0,0] + dcm[1,1] + dcm[2,2]
		tmpi = 1 + dcm[0,0] - dcm[1,1] - dcm[2,2]
		tmpj = 1 - dcm[0,0] + dcm[1,1] - dcm[2,2]
		tmpk = 1 - dcm[0,0] - dcm[1,1] + dcm[2,2]

		if tmps > k:
			self.s = np.sqrt(tmps/4)
			self.v[0] = (dcm[1,2]-dcm[2,1])/(4*self.s)
			self.v[1] = (dcm[2,0]-dcm[0,2])/(4*self.s)
			self.v[2] = (dcm[0,1]-dcm[1,0])/(4*self.s)

		elif tmpi > k:
			self.v[0] = np.sqrt(tmpi/4)
			self.s = (dcm[1,2]-dcm[2,1])/(4*self.v[0])
			self.v[1] = (dcm[0,1]+dcm[1,0])/(4*self.v[0])
			self.v[2] = (dcm[2,0]+dcm[0,2])/(4*self.v[0])

		elif tmpj > k:
			self.v[1] = np.sqrt(tmpj/4)
			self.s = (dcm[2,0]-dcm[0,2])/(4*self.v[1])
			self.v[0] = (dcm[0,1]+dcm[1,0])/(4*self.v[1])
			self.v[2] = (dcm[1,2]+dcm[2,1])/(4*self.v[1])

		elif tmpk > k:
			self.v[2] = np.sqrt(tmpk/4)
			self.s = (dcm[0,1]-dcm[1,0])/(4*self.v[2])
			self.v[0] = (dcm[2,0]+dcm[0,2])/(4*self.v[2])
			self.v[1] = (dcm[1,2]+dcm[2,1])/(4*self.v[2])

		else:
			# Throw error
			print("ERROR Converting from dcm")
			return
		self.normalize()
		return

	def normalize(self):
		total = sqrt(self.s**2+self.v[0]**2+self.v[1]**2+self.v[2]**2)
		self.s = self.s/total
		self.v = self.v/total
		if self.s < 0:
			self.s = -self.s
			self.v = -self.v

	def toArray(self):
		return array([self.s,self.v[0],self.v[1],self.v[2]])
	
	def fromArray(self,arr):
		"""
			Assumes that array is set up like: [s,v1,v2,v3]
		"""
		self.s = float(arr[0])
		self.v = np.array(arr[1:4],dtype=float)
		self.normalize()
		return

	def __eq__(self,other):
		if abs(self.s) != abs(other.s):
			return False
		if not np.all(abs(self.v) == abs(other.v)):
			return False
		alt = Quaternion(s=-other.s,v=-other.v)
		if self.s == other.s and np.all(self.v == other.v):
			return True
		if self.s == alt.s and np.all(self.v == alt.v):
			return True
		return False


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


if __name__ == "__main__":
	quat = np.array([-0.541570454408883,0.454644303726942,-0.454644303726942,0.541570454408883])
	q1 = Quaternion()
	q2 = Quaternion()
	q1.fromArray(quat)
	q2.fromDCM(q1.toDCM())
	print("Q1 is: {}".format(q1))
	print("Q2 is: {}".format(q2))
