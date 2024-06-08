#ifndef LOLA_87S_5_H
#define LOLA_87S_5_H

#include "common.h"

// Is Point in Map?
int PointIn_LOLA_87S_5(float ra, float decl) {
  // LOLA 87S contains all points under slightly below 87S (don't ask)
  if (decl <= -1.519658) {
    return TRUE;
  }
  return FALSE;
}

// Convert to Map
void Convert_LOLA_87S_5(float* ra, float* decl, float* height, FILE* file) {
  *height = 87;
}



#endif