#ifndef BOROMIR_COMMON_H
#define BOROMIR_COMMON_H
#include <stdio.h>
#include "math.h"

#define TRUE 1
#define FALSE 0
#define ullong unsigned long long
#define ulong unsigned long
#define MOON_RADIUS 1737400 //meters
#define MOON_POLAR_RADIUS 1736000 //meters

int uv2vertid(ulong u, ulong v, ulong u_pixels, ulong* id) {
	*id = v*u_pixels+u;
	return 0; 
}

#endif