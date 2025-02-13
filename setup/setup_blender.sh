#!/bin/bash
################################################################################
# Install the requirements to the Blender Python env
################################################################################

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
INSTALL_FILE="$SCRIPT_DIR/lib_install.py"

blender -b -P "$INSTALL_FILE"
