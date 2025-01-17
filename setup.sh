#!/bin/bash
################################################################################
# Performs setup of entire Repo                                                #
#                                                                              #
# Author: Max Marshall 06/2024                                                 #
################################################################################

# Create Virtual Environment
if [[ ! -e ".venv" ]]; then
  echo -e "Creating Virtual Environment"
  python3.11 -m venv .venv || (rm -r .venv && echo "Install required Python verion and try again" && exit)
  echo -e "Created Virtual Environment"
else
  echo -e "Virtual Environment Found, continuing..."
fi

# Source the Venv
echo "Upgrading Pip"
source ".venv/bin/activate"
pip3 install --upgrade pip

# Install Python Libraries
echo "Installing Python Libraries"
pip3 install -r "requirements.txt"
echo "Finishing Installing Libraries"

echo; echo; echo;

# Download NAIF Spice Kernels
echo "Begin Downloading Spice Kernels"
setup/kernel_downloader.sh || ( echo "Bad permissions" && exit )
echo "End Downloading Spice Kernels"

echo; echo; echo

# Download Required DEM/Albedo Files
echo "Begin Downloading DEM/Albedo Files"
setup/dem_downloader.sh || ( echo "Bad permissions" && exit )
echo "End Downloading DEM/Albedo Files"

echo; echo; echo

# Prep Blender installs
echo "Install Blender Python Libraries"
setup/setup_blender.sh || (echo "Bad permissions" && exit )

echo; echo; echo

# Build C++ Files
echo "Build C++ Script"
( cd src/cpp && ./buildmesh.sh ) || ( echo "Bad permissions/FileNotFound" && exit )

deactivate
