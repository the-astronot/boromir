# INPUTS

Explaining the different input files, and their data. These are all found in configs/.

## BLENDER

This config contains all of the requisite data for configuring Blender

- device: One of \["CPU","GPU"\], whether you are rendering on a CPU or GPU
- threads_mode: One of \["AUTO","FIXED"\], whether the number of threads used should be automatic or fixed
- threads: If "threads_mode" is "FIXED", this sets the number of threads to be used
- samples: The number of samples to be used in rendering. More samples -> Better looking image -> More render time
- bounces: The maximum number of reflections light should make
- denoise: Whether or not to have Blender denoise the image. Should usually be true, but is not supported on legacy cpus like mine
- moon: Settings regarding the Moon object, all the BSDF values are via trial and error (I'm neither a geologist nor an artist)
  - albedo_map: The filename of the albedo map file in maps/
  - roughness: The roughness of the BSDF shader
  - metallic: The metallic quality of the BSDF shader
  - ior: The IOR of the BSDF shader
  - bright: The value of the applied brightness shader
  - contrast: The value of the applied contrast shader
- earth: Settings regarding the Earth object, see above disclaimer
  - albedo_map: The filename of the albedo map file in maps/
  - roughness: The roughness of the BSDF shader
  - metallic: The metallic quality of the BSDF shader
  - ior: The IOR of the BSDF shader
  - bright: The value of the applied brightness shader
  - contrast: The value of the applied contrast shader
- sun: Settings regarding the sun object
  - energy: The energy of the sunlight, in W/m^2
  - color: The color of the sun, in RGB, from 0 to 1 for each band
  - angle: The angular diameter of the Sun, in radians
- exposure_offset: Integer offset to try and correct for Blender's funky math
- re_render: DEPRECATED Whether or not to regenerate an already rendered image
- color_mode: One of \["RGB","BW"\], What colorspace is used for the image
- color_depth: The bit depth of the pixels in the image
- file_ext: File extension to use for the image. I recommend leaving it as PNG.

## CAMERA

This config specifies camera parameters. These are more likely to vary than the Blender config, which will likely remain the same once you find settings you are comfortable with.

- FOV_x: The Field of View of the camera in the horizontal direction
- FOV_y : The Field of View of the camera in the vertical direction
- iso: The ISO of the camera, part of the exposure triangle
- F_Stop: The aperature of the lens, part of the exposure triangle
- Exposure_Time: The length of the exposure, part of the exposure triangle
- NumBlades: DEPRECATED The number of blades on the lens (Blender's lenses are a bit of a mess)
- Nrows: Number of pixels per row of sensor
- Ncols: Number of pixels per col of sensor
- Subsamples: Target number of vertices on the mesh per pixel of the camera
- OffsetPix: The number of extra pixels to add to the camera for mesh generation (Keeps from seeing artifacts at the edges of the mesh)

## RANDOM POSES

W.I.P.

## TRAJECTORIES

Unlike the other configs, the trajectory file is a csv with the following columns:

NOTE: Boromir treats lines beginning with "#" as comments, and ignores them

NOTE: SEE [CONVENTIIONS](CONVENTIONS.md) for frame conventions explained

- ImgName: What to call the image
- CAM_PosX: Camera position on the X-axis, in meters
- CAM_PosY: Camera position on the Y-axis, in meters
- CAM_PosZ: Camera position on the Z-axis, in meters
- CAM_QUATS: The S value of the Camera quaternion
- CAM_QUATV1: The first value of the V component of the Camera quaternion
- CAM_QUATV2: The second value of the V component of the Camera quaternion
- CAM_QUATV3: The third value of the V component of the Camera quaternion
- Time: (OPTIONAL) The UTC time of the image, if recreating a real image. Not required if you are specifying the remainder of the data. If not setting, simply do not include a time value, e.g. ",,"
- SUN_LosX: (OPTIONAL) The Line of Sight from the Sun to the Moon in the X direction, not required if time was set
- SUN_LosY: (OPTIONAL) The Line of Sight from the Sun to the Moon in the Y direction, not required if time was set
- SUN_LosZ: (OPTIONAL) The Line of Sight from the Sun to the Moon in the Z direction, not required if time was set
- EARTH_PosX: (OPTIONAL) The Earth position on the X-axis, in meters, not required if time set or Earth not required
- EARTH_PosY: (OPTIONAL) The Earth position on the Y-axis, in meters, not required if time set or Earth not required
- EARTH_PosZ: (OPTIONAL) The Earth position on the Z-axis, in meters, not required if time set or Earth not required
- EARTH_QuatS: (OPTIONAL) The S value of the Earth quaternion, not required if time set or Earth not required
- EARTH_QuatV1: (OPTIONAL) The first value of the V component of the Earth quaternion, not required if time set or Earth not required
- EARTH_QuatV2: (OPTIONAL) The second value of the V component of the Earth quaternion, not required if time set or Earth not required
- EARTH_QuatV3: (OPTIONAL) The third value of the V component of the Earth quaternion, not required if time set or Earth not required
