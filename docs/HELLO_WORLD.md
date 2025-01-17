# HELLO WORLD

This file will outline a starter run to get you more familiar with BOROMIR.

NOTE: Before starting this run, read through [INPUTS](INPUTS.md) and make sure that you have the Blender configs configured properly for your system/use case.

In your terminal, enter the following command: `boromir --camera=hasselblad.json --logging=hello_world.log trajectory earth_rise.csv --job=hello_world`

## WHAT DOES IT DO?

Let's break it down, one piece at a time.

- boromir : Calls the program
- --camera=hasselblad.json : Selects hasselblad.json from configs/cameras/ as the camera to use
- --logging=hello_world.log : Creates file hello_world.log in logs/ as the log file
- trajectory : the first positional argument, specifies that we are performing a trajectory-based run
- earth_rise.csv : the second positional argument, specifies that the trajectory csv to run is configs/trajectories/earth_rise.csv
- --job=hello_world : Sets the name of the output dir for the images/metadata in outimages/ to be hello_world/ rather than earth_rise/, as the filename of the run is the default argument

When this program is run, you will see output begin appearing in the log file, temporary files appear in tmp/ and final outputs appear in outimages/hello_world/.
