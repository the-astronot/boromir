#!/bin/bash
################################################################################
# Download the required DEM and albedo maps from the internet
#
# Author: Max Marshall -- 06/2024
################################################################################

# Download the files
download() {
	echo "Downloading $1..."
	wget -c -P "$2" --tries=0 "$1" --show-progress --random-wait -olog
	echo -e "Finished Downloading $1 to $2\n"
}

# MAIN CODE

# File storage directory
IMGDIR="data/"

# Albedo Map File
ALBEDO_MAP="https://svs.gsfc.nasa.gov/vis/a000000/a004700/a004720/lroc_color_poles.tif"

# LOLA 118mpp DEM
LOLA_118="https://planetarymaps.usgs.gov/mosaic/Lunar_LRO_LOLA_Global_LDEM_118m_Mar2014.tif"

# 87S 5mpp DEM
LOLA_87S_5="https://pgda.gsfc.nasa.gov/data/LOLA_5mpp/87S/ldem_87s_5mpp.tif"

# Build Collection of Files to Download
## Feel free to add more maps here
MAPS=($ALBEDO_MAP $LOLA_118 $LOLA_87S_5)

for i in "${MAPS[@]}"; do
	download "$i" "$IMGDIR"
done

