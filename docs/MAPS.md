# MAPS

Boromir relies on a number of maps in order to generate its images. These break down into 2 groups:

## Albedo Maps

These maps are pretty straightforward. They are simple cylindrical projection maps of the moon/earth that act as color maps on their surfaces.

## Digital Elevation Maps (DEM)s

These get a little more interesting. Boromir was designed to allow multiple maps to be used at the same time. This allows both an equatorial map and polar map to be used at once, rather than having to choose between them. Maps are given preference over each other, and that preference is used to determine which data to use at each point. This can also in theory be used to add in smaller areas of higher resolution data, such as landing sites, to allow for better images closer to the surface there. In order to add a new map, the process is as follows:

### Find a relevant DEM

I got access to the included maps through [NASA's GSFC](https://pgda.gsfc.nasa.gov) and similar sites. Further DEM development/refinement seems to be an area of active study, so map updates down the line will likely occur. Internet searches for something along the lines of "Moon DEM", "Moon elevation map", or similar will lead you down a rabbit hole with a bunch of different DEMs to choose from. Important to note are the estimated error and resolution of the data, as well as any noted incomplete segments.

### Download the DEM into maps/

Hoping this one is pretty self-explanatory.

### Run tiff2bin.py on the downloaded image

This converts the DEM from a TIFF file (assumed) to a binary file that is easier to work with. This essentially allows Boromir to scan around in the file, rather than try and open the whole thing, which can be exceptionally large. Looking in tiff2bin.py should show the current maps being processed to give you an idea of what it should look like. "float" or "short" should be selected based on what information your DEM actually uses. Make note of your choice, it'll become important momentarily.

### Go to src/cpp/mapping and create a *.h file for your map

Look at lola_118.h and lola_87s_5.h as examples. In this file, you will need to create 2 functions:

1. IsPointInMap?
2. MapRa/Decl

#### IsPointInMap?

This function is pretty straightforward. All you have to do is come up with a function that returns TRUE if the given Ra/Decl is in the map you're adding, and FALSE otherwise. I recommend erring on the side of caution. There is a map for the full Moon in place, I'd think it better to underestimate the size of the added map so as to avoid issues.

#### Map Ra/Decl

This is the key function. This function needs to accept a Ra/Decl, and return a Ra/Decl and Radius from your map. In short, this is mapping your elevation map. In the simplest case, Ra/Decl can remain the same, and the radius can be calculated from the elevation map and returned. For your convenience, I have included src/cpp/common.h with some useful constants and a function to convert the u and v coordinates on your map into the vertex id, which can be used to retrieve the elevation from the binary file.

NOTE: This is likely going to be tough. I'd recommend trying a simple projection first, as in lola_118.h, before approaching a stereographic projection like in lola_87s_5.h.

### Append the *.h file to maps.h

ALMOST THERE! Now all you need to do is set the required values in maps.h.

NOTE: The only section you should need to edit is the bit within the brackets

1. Include your new map file
2. Increment the number of maps used
3. Decide what priority your new map should have (look at the other maps)
4. Enter your new maps check and mapping functions into the check, mapping, filename, and dimension arrays. It is critical that you put them at the same index in each. Highest priority maps are at index 0.

Now you'll just need to run build_mesh.sh from src/cpp and you're good to go!

If you are feeling generous and your map looks good, please consider putting in a commit with a link to your map and your shiny new mapping file and I'll try and add it in.
