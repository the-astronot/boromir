#ifndef LOLA_118_H
#define LOLA_118_H

// Standart Requirements
#include "common.h"
#include "math.h"
extern const double map_dims[][2];
extern FILE* files[];
//

// Is Point in Map?
int PointIn_LOLA_118(ldouble ra, ldouble decl) {
  // The LOLA 118 meter per pixel map has full moon coverage
  return TRUE;
}

// Convert to Map
void Convert_LOLA_118(ldouble* ra, ldouble* decl, double* radius, int idx) {
  ulong u,v,read_loc;
	float fu,fv;
  short read_radius;
  // u = ((U_PIXELS-1)/2)+(U_PIXELS/360.*rad2deg(ra))
	// v = ((V_PIXELS-1)/2)-(V_PIXELS/180.*rad2deg(decl))
	fu = round(((map_dims[idx][0]-1)/2.0)+((map_dims[idx][0]/(2*M_PI))*(*ra)));
	fv = round(((map_dims[idx][1]-1)/2.0)-((map_dims[idx][1]/M_PI)*(*decl)));
	u = (ulong) fu;
	v = (ulong) fv;
	// ra = 2*pi*((u+.5)/U_PIXELS) - pi
	// decl = -pi*((v+.5)/V_PIXELS) + pi/2
	*ra = 2.0*M_PI*((fu+0.5)/map_dims[idx][0]) - M_PI;
	*decl = -M_PI*((fv+0.5)/map_dims[idx][1]) + M_PI/2.0;
	//u = round(*color*mapsize[0]);
	//v = round(mapsize[1]*(1-*(color+1)));
	uv2vertid(u,v,(ulong)map_dims[idx][0],&read_loc);
	read_loc = sizeof(short)*read_loc;
	fseek(files[idx],read_loc,SEEK_SET);
	fread(&read_radius,sizeof(short),1,files[idx]);

	*radius = MOON_RADIUS+0.5*(double)read_radius;
}

#endif
