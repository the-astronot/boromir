#!/bin/bash
################################################################################
# Download the required DEM and albedo maps from the internet
#
# Author: Max Marshall -- 12/2024
################################################################################

# Download the files
download() {
	echo "Downloading $1..."
	wget -c -P "$2" --tries=0 "$1" --show-progress --random-wait -a kernel.log
	echo -e "Finished Downloading $1 to $2\n"
}

# Delete file if it exists
trydelete() {
	if [[ -f "$1" ]]; then
		rm "$1"
	fi
}

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
SPICE_DIR="$SCRIPT_DIR/../spicedata"
NAIF_LINK="https://naif.jpl.nasa.gov/pub/naif/generic_kernels"

# Download all requirements from file
trydelete "kernel.log"
while read -r line; do
	download "$NAIF_LINK/$line" "$SPICE_DIR"
done <"$SPICE_DIR/requirements.txt"
