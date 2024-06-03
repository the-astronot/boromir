from Structures import Quaternion
from numpy import array,eye

dcm0 = array([[0,-1,0],
							[0,0,1],
							[-1,0,0]])
print(dcm0)
offset = Quaternion()
offset.fromDCM(dcm0)
print(offset.toArray())
dcm1 = offset.toDCM()
print(dcm1)

sc = Quaternion(1,[0,0,0])
print(sc.toDCM())

full = sc.toDCM()@offset.toDCM()
print(full)
