import pytest
from pytest import importorskip

################################################################################
# Setup module for get/set
import sys
this = sys.modules[__name__]

def getvar(var):
	return getattr(this,var)

def setvar(name,value):
	setattr(this,name,value)
################################################################################

# Setup import variable addresses
modules = {
	"cv":"cv2",
	"mpl":"matplotlib",
	"np":"numpy",
	"tqdm":"tqdm",
	"bpy":"bpy",
	"pd":"pandas",
	"ski":"skimage",
	"sp":"spiceypy"
}


def try_imports():
	## Test importing each of the required modules
	for key in modules:
		setvar(key,importorskip(modules[key]))
	return True


if __name__ == "__main__":
	print(try_imports())
	for key in modules:
		try:
			print(getvar(key).__version__)
		except AttributeError:
			print(key)

