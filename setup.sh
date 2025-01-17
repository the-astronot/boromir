#!/bin/bash
################################################################################
# Performs setup of entire Repo                                                #
#                                                                              #
# Author: Max Marshall 06/2024                                                 #
################################################################################

# Download NAIF Spice Kernels
setup/kernel_downloader.sh

# Download Required DEM/Albedo Files
setup/dem_downloader.sh

# Prep Blender installs
setup/setup_blender.sh

# Build C++ Files
src/cpp/buildmesh.sh

# Create Virtual Environment
if [[ ! -e ".venv" ]]; then
  echo -e "Creating Virtual Environment"
  python3.11 -m venv .venv
  echo -e "Created Virtual Environment"
else
  echo -e "Virtual Environment Found, continuing..."
fi

# Source the Venv
source ".venv/bin/activate"
pip3 install --upgrade pip

# Install Python Libraries
echo "Installing Python Libraries"
pip3 install -r "requirements.txt"
echo "Finishing Installing Libraries"

deactivate

