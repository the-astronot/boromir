# SETUP

Walking through the setup process.

## Hardware

The hardware requirements for running BOROMIR are... not exactly minor. I wouldn't recommend running it on a computer without a GPU (I've lost hours of my life running it on my GPU-less R620 development server) and a good chunk of ram. If you are stuck on older/less powerful hardware, I would start with smaller camera sizes and work your way up from there. If you have the time/inclination to note the time required to run the Hello World test script and feel like messaging me the time to complete and your hardware, I'd love to start a leaderboard of various hardware specs.

## Installation/Pre-requisites

BOROMIR relies on the following programs:

- [Blender 4.0](#installing-blender)
- Python>=3.10
- gcc
- make
- wget

NOTE: BOROMIR was built for and runs on Linux-based systems. All development and testing has been done on Ubuntu and/or Rocky. It should run on any other Debian-based OS, but has not been tested further.

### Installing Blender

Blender can be installed via their [website](https://blender.org). This project was built using Blender 4.0.2, and as such I cannot speak to how well alternate versions will work. For specific versions, see [this site](https://download.blender.org/release).

### Installing the Rest

The remaining utilities can be installed via the commandline. If you require tutorials for them, I would suggest looking into each of them separately.

### Cloning/Downloading

Finally, you'll need to clone/download this repo to your machine.

## Setup

NOTE: During setup, scripts download a whole bunch of maps. If you notice that any of the links are dead, please notify me and I'll get a replacement set up.

Once the above steps have been accomplished, perform the following:

1. Confirm that you can run blender from the commandline by running `blender --version`
2. Make sure that you have the privileges to execute the following files: `setup/dem_downloader.sh`, `setup/kernel_downloader.sh`, `setup/setup_blender.sh`, and `src/cpp/buildmesh.sh`
3. Cd to the parent directory for this repo
4. Run `setup.sh`. This will perform the following actions:
   1. Create a new virtual environment
   2. Install the required python libraries to the environment
   3. Download the requisite SPICE kernels
   4. Download and modify the assorted albedo and DEM maps. NOTE: This may take some time. Some of the maps can be pretty large and the servers are not the most responsive. Please be kind.
   5. Build the C++ script for the codebase
5. Inspect the documentation in docs/. There is information there about the maps, inputs, conventions, limitations, etc that may answer some of your questions
6. Try running the Hello World script as detailed in [HELLO WORLD](HELLO_WORLD.md)
