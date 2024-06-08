#ifndef LOLA_118_H
#define LOLA_118_H

#include "common.h"

// Is Point in Map?
int PointIn_LOLA_118(float ra, float decl) {
  // The LOLA 118 meter per pixel map has full moon coverage
  return TRUE;
}

// Convert to Map
void Convert_LOLA_118(float* ra, float* decl, float* height, FILE* file) {
  //short read_height;
  //ulong u,v;
  *height = 118;
}

#endif