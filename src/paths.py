# Setting up all the requisite paths
# Library imports
from os.path import basename,dirname,abspath,join

# Local imports


# Important Paths
BASE_DIR = dirname(dirname(abspath(__file__)))
CONFIG_DIR = join(BASE_DIR,"configs")
CAMERA_DIR = join(CONFIG_DIR,"cameras")
BLENDER_CONF_DIR = join(CONFIG_DIR,"blender")
TRAJECTORY_DIR = join(CONFIG_DIR,"trajectories")
RANDOM_POSE_DIR = join(CONFIG_DIR,"random_poses")
IMG_DIR = join(BASE_DIR,"outimages")
LOG_DIR = join(BASE_DIR,"logs")
SRC_DIR = join(BASE_DIR,"src")
CPP_DIR = join(SRC_DIR,"cpp")
TMP_DIR = join(BASE_DIR,"tmp")
MAP_DIR = join(BASE_DIR,"maps")
PYTHON_VENV = join(BASE_DIR,".venv","bin","python3")
