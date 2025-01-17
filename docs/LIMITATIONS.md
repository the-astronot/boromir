# BOROMIR LIMITATIONS

## BLENDER

The software is limited by using Blender as it's rendering engine. I learned too late into the process that Blender doesn't do well with "scientific" lighting, setting the Sun's power properly and rendering off of that. I have added an exposure offset to try and counteract this, but without proper examples to base the offset off of, it likely isn't very good. I have exposed this offset in the blender config so that you can try and do a better job with it if desired.

Blender also has precious few adjustments available to the camera. It cannot handle the Brown-Conrady distortion model natively, which limits the amount of simulation available there.

The Blender API is also Python based. Normally this would be fine, except that they do not include all of the functions required to efficiently create large meshes. This creates a slow down discussed in the next section as well as a lot of ram usage holding onto oversized data.

## RAM

Boromir creates new meshes for each image/set of images. This was done for 3 reasons:

1. This should minimize artifacts from different sections meeting and create nicer images
2. I had neither the storage space to hold multiple resolutions of different maps, nor a good way to swap them in and out in Blender
3. This allows layering multiple maps atop one another, as described in [MAPS](MAPS.md).

Unfortunately, in order to build larger, higher resolution images and maps, lots and lots of ram can be consumed. If you start running into issues, I'd recommend decreasing your number of subsamples or camera resolution.

## TIME

This is,in my opinion, Boromir's achilles heel. It can be **incredibly** slow, depending on the image size required and hardware that it is running on. That running time accumulates in 3 main locations:

1. Finding the mesh vertices, faces, and uv coords. This was originally the worst of the bunch, but I rewrote it in C++ to speed it up as best I could. Further improvements could likely be made in improving my code or porting the code to use multiple threads/GPU computing, since a proper GPU is essentially already required for the renderer.
2. ~~Converting from the vertices and faces into a mesh that Blender can read. Blender exposes part of its API to do this. It doesn't feel particularly efficient, but they don't readily offer a better way of accessing the lower levels of the code to try and improve it.~~
3. ~~Assigning the uv coords to the faces on the Blender mesh. This is my current opponent. It is currently accomplished by a double nested for loop in Python, which becomes **quite** slow when tens of millions of faces are used. I'd like to improve this, but it seems like it would take figuring out how to get C code to recognize the blender structure and perform a faster for loop there. Its a bit more than I am inclined to rush headlong into at the moment.~~

I managed to find a lower level solution to the latter two time sinks. I'm waiting to determine whether that has alleviated that slowdown sufficiently.

## IMAGE QUALITY

The images that Boromir can generate are limited by the resolution of the underlying elevation and albedo maps. If you bring the camera too low to the Moon over an area without high enough resolution map data, it will look crummy.
