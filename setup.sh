#!/bin/bash
################################################################################
# Performs setup of entire Repo                                                #
#                                                                              #
# Author: Max Marshall 06/2024                                                 #
################################################################################

# Download NAIF Spice Kernels
echo "Begin Downloading Spice Kernels"
setup/kernel_downloader.sh || echo "Bad permissions" && exit
echo "End Downloading Spice Kernels"

# Download Required DEM/Albedo Files
echo "Begin Downloading DEM/Albedo Files"
setup/dem_downloader.sh || echo "Bad permissions" && exit
echo "End Downloading DEM/Albedo Files"

# Prep Blender installs
echo "Install Blender Python Libraries"
setup/setup_blender.sh

# Build C++ Files
echo "Build C++ Script"
src/cpp/buildmesh.sh || echo "Bad permissions" && exit

# Create Virtual Environment
if [[ ! -e ".venv" ]]; then
  echo -e "Creating Virtual Environment"
  python3.11 -m venv .venv
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

deactivate

