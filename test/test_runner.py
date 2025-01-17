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


def test_main():
	# Try all the imports
	assert try_imports()
	print("All libraries located")

	print()
	print("Library versions:")
	# Print the versions of all of the modules
	for key in modules:
		try:
			print("{} = {}".format(key,getvar(key).__version__))
		except AttributeError:
			print("{} = unknown".format(key))


if __name__ == "__main__":
	test_main()
