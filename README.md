# BOROMIR

## Description

The Blender-based Open-source Repository for Opnav Moon Image Rendering (BOROMIR) is a utility for generating simulated images of the Moon from lunar orbit.

## Abstract

BOROMIR utilizes digital elevation maps (DEMs) and albedo maps of the Moon to generate meshes and create simulated images from a camera state and time (Sun position).

## Installation

### Pre-requisites

BOROMIR relies on the following programs:

- [Blender](#installing-blender)
- Python>=3.10
- gcc
- make

NOTE: BOROMIR was built for and runs on Linux-based systems. All development and testing has been done on Ubuntu and/or Rocky. It should run on any other Debian-based OS, but has not been tested further.

#### Installing Blender

Blender can be installed via {FILL_IN}.

#### Installing the Rest

The remaining utilities can be installed via the commandline.

### Cloning/Downloading



### Setup


## Usage

BOROMIR is run from the commandline. The main bash file can be found in the bin/ directory and added to your $PATH. Running as below will show the help page.

``` bash
boromir -h
```

At present, BOROMIR has two options for generating states/images, RANDOM and TRAJECTORY. RANDOM takes a config file as argument for specifying the parameters for the random generated states. TRAJECTORY instead takes a config file as argument for specifying the exact states which will be used. In essence, if you just need images under certain conditions (like for generating datasets), RANDOM is the way to go. Alternatively if you have done the work to compute the state for a certain image, then use TRAJECTORY.

Examples of each are shown below.

``` bash
boromir random rand_file.json --num_images=100
```

``` bash
boromir traj traj_file.json
```

## License

This project is licensed under the MIT License, in order to make it as accessible as possible.

Borrowing from the (claimed) words of Freddie Mercury, "do whatever you want with \[it\], ... just don't make it boring."

## Authors and Acknowledgements

This project was authored by [Max Marshall](www.github.com/the-astronot) towards the fulfillment of a Masters of Engineering (M. Eng) degree at Rensselaer Polytechnic Institute (RPI) during the year of 2024.

Special thanks to:

- My advisor: Kurt Anderson, PhD for setting me on my path and being in my corner
- My friend: Sophia Catalan for her help with brainstorming and testing
- My adopted mentor: James McCabe, PhD for believing in this project
- NASA Goddard Spaceflight Center: for your maps that make this all possible
- NASA Johnson Space Center: for inspiring this project
- My parents: for ... **everything**
