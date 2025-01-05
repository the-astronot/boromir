#!/bin/bash
################################################################################
# Download the required DEM and albedo maps from the internet
#
# Author: Max Marshall -- 06/2024
################################################################################

# Download the files
download() {
	echo "Downloading $1..."
	wget -c -P "$2" --tries=0 "$1" --show-progress --random-wait -a "dem.log"
	echo -e "Finished Downloading $1 to $2\n"
}

# Delete file if it exists
trydelete() {
	if [[ -f "$1" ]]; then
		rm "$1"
	fi
}

# Move file if it exists
trymove() {
	if [[ -f "$1" ]]; then
		mv "$1" "$2"
	fi
}

################################################################################
# MAIN CODE

# File storage directory
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
MAPDIR="$SCRIPT_DIR/../maps/"

# Star Map File
STAR_MAP="https://github.com/nasa/NASA-3D-Resources/blob/master/Images%20and%20Textures/Hipparcos%20Star%20Map/hipp8.tif?raw=true"

# Albedo Map File
ALBEDO_MAP="https://svs.gsfc.nasa.gov/vis/a000000/a004700/a004720/lroc_color_poles.tif"

# LOLA 118mpp DEM
LOLA_118="https://planetarymaps.usgs.gov/mosaic/Lunar_LRO_LOLA_Global_LDEM_118m_Mar2014.tif"

# 87S 5mpp DEM
LOLA_87S_5="https://pgda.gsfc.nasa.gov/data/LOLA_5mpp/87S/ldem_87s_5mpp.tif"

# Get the higher resolution Albedo Map
WAC_MOS_1="https://pds.lroc.asu.edu/data/LRO-L-LROC-5-RDR-V1.0/LROLRC_2001/DATA/MDR/WAC_HAPKE/WAC_HAPKE_3BAND_E350N2250.TIF"
WAC_MOS_2="https://pds.lroc.asu.edu/data/LRO-L-LROC-5-RDR-V1.0/LROLRC_2001/DATA/MDR/WAC_HAPKE/WAC_HAPKE_3BAND_E350N3150.TIF"
WAC_MOS_3="https://pds.lroc.asu.edu/data/LRO-L-LROC-5-RDR-V1.0/LROLRC_2001/DATA/MDR/WAC_HAPKE/WAC_HAPKE_3BAND_E350N0450.TIF"
WAC_MOS_4="https://pds.lroc.asu.edu/data/LRO-L-LROC-5-RDR-V1.0/LROLRC_2001/DATA/MDR/WAC_HAPKE/WAC_HAPKE_3BAND_E350N1350.TIF"
WAC_MOS_5="https://pds.lroc.asu.edu/data/LRO-L-LROC-5-RDR-V1.0/LROLRC_2001/DATA/MDR/WAC_HAPKE/WAC_HAPKE_3BAND_E350S2250.TIF"
WAC_MOS_6="https://pds.lroc.asu.edu/data/LRO-L-LROC-5-RDR-V1.0/LROLRC_2001/DATA/MDR/WAC_HAPKE/WAC_HAPKE_3BAND_E350S3150.TIF"
WAC_MOS_7="https://pds.lroc.asu.edu/data/LRO-L-LROC-5-RDR-V1.0/LROLRC_2001/DATA/MDR/WAC_HAPKE/WAC_HAPKE_3BAND_E350S0450.TIF"
WAC_MOS_8="https://pds.lroc.asu.edu/data/LRO-L-LROC-5-RDR-V1.0/LROLRC_2001/DATA/MDR/WAC_HAPKE/WAC_HAPKE_3BAND_E350S1350.TIF"

# Number of DEM files
NUM_BIN_FILES=2

# Build Collection of Files to Download
## Feel free to add more maps here
MAPS=($STAR_MAP $ALBEDO_MAP $LOLA_118 $LOLA_87S_5 $WAC_MOS_1 $WAC_MOS_2 $WAC_MOS_3 $WAC_MOS_4 $WAC_MOS_5 $WAC_MOS_6 $WAC_MOS_7 $WAC_MOS_8)

# Download all maps
trydelete "dem.log"
for i in "${MAPS[@]}"; do
	download "$i" "$MAPDIR"
done

# Rename the tif file
trymove "$MAPDIR/hipp8.tif?raw=true" "$MAPDIR/hipp8.tif"

BIN_FILES_COUNT=$(find "$MAPDIR" -name "*.bin" | wc -l)
if [[ "$BIN_FILES_COUNT" -lt "$NUM_BIN_FILES" ]]; then
	cd "$MAPDIR" && python3 tiff2bin.py
fi

################################################################################
