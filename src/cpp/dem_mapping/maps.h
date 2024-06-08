#ifndef BOROMIR_MAPS_H
#define BOROMIR_MAPS_H

#include "common.h"

typedef int(*check)(float,float);
typedef void(*convert)(float*,float*,float*,FILE*);

////////////////////////////////////////////////////////////////////////////////
// THIS IS THE BIT WHERE YOU ADD MORE MAPS
//// EACH SECTION HERE WILL HAVE TO BE MODIFIED
//// ORDER MATTERS, GO FROM HIGHEST RESOLUTION TO LOWEST
//// MAINTAIN ORDER THROUGHOUT SECTION
////////////////////////////////////////////////////////////////////////////////
// Include all map files
#include "lola_87s_5.h"
#include "lola_118.h"

#define NUM_MAPS 2 // Should be self-explanatory

// Check functions
check check_funcs[NUM_MAPS] = {PointIn_LOLA_87S_5,  // LOLA 87S
                              PointIn_LOLA_118      // LOLA 118
                              };

// Conversion functions
convert find_funcs[NUM_MAPS] = {Convert_LOLA_87S_5, // LOLA 87S
                                Convert_LOLA_118    // LOLA 118
                                };

// Map Names - These MUST be the Binary Versions!
const char* filenames[NUM_MAPS] = {
  "ldem_87s_5mpp.bin",                              // LOLA 87S
  "Lunar_LRO_LOLA_Global_LDEM_118m_Mar2014.bin"     // LOLA 118
  };

const ulong map_dims[NUM_MAPS][2] = {{40000,40000}, // LOLA 87S
                                    {92180,46080}   // LOLA 118
                                    };
// END MAP ADDITION SECTION
////////////////////////////////////////////////////////////////////////////////

// Map locations


// File Pointers
FILE* files[NUM_MAPS];

// Declarations
int get_point(float* ra, float* decl, float* height);
int load_maps();
int close_maps();

// Definitions
int get_point(float* ra, float* decl, float* height) {
  for (int i=0; i<NUM_MAPS; i++) {
    if ((check_funcs[i])(*ra,*decl) == TRUE) {
      (find_funcs[i])(ra,decl,height,files[i]);
      return 0;
    }
  }
  *ra = 0;
  *decl = 0;
  *height = 0;
  return 1;
}

int load_maps() {
  int status = 0;
  for (int i=0; i<NUM_MAPS; i++) {
    files[i] = fopen(filenames[i],"rb");
    if (files[i]==NULL) {
      printf("Could not find file: %s\n",filenames[i]);
      status = 1;
    }
  }
  return status;
}

int close_maps(){
  for (int i=0; i<NUM_MAPS; i++) {
    if (files[i]!=NULL){
      fclose(files[i]);
    }
  }
  return 0;
}

#endif