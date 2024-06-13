#ifndef LOLA_87S_5_H
#define LOLA_87S_5_H

// Standart Requirements
#include "common.h"
#include <math.h>
extern const double map_dims[][2];
extern FILE* files[];
//

// Is Point in Map?
int PointIn_LOLA_87S_5(double ra, double decl) {
  // LOLA 87S contains all points under slightly below 87S (don't ask)
  if (decl <= -1.519658) {
    return TRUE;
  }
  return FALSE;
}


#ifdef BILINEAR_INTERP
// Convert to Map
void Convert_LOLA_87S_5(double* ra, double* decl, double* radius, int idx) {
  /*
    Replicating the stereographic projection as laid out here:
    https://mathworld.wolfram.com/StereographicProjection.html
  */
 	const double MPP = 5.0;
  const double CENTER = 19999.5;
 	double phi,lambda,phi1,lambda0,k,du,dv,x,y;
  float weights[4];
  float heights[4];
	ulong u,v,read_loc,u_max,ui,vi;
	double height;
	phi1 = -M_PI/2.;
	lambda0 = 0.;
  // First, we need to get the uv coords
	phi = *decl;
	lambda = *ra;
	k = (2*MOON_POLAR_RADIUS)/(1+sin(phi1)*sin(phi)+cos(phi1)*cos(phi)*cos(lambda-lambda0));
	dv = -(k*(cos(phi1)*sin(phi)-sin(phi1)*cos(phi)*cos(lambda-lambda0))/MPP)+CENTER;
	du = (k*cos(phi)*sin(lambda-lambda0)/MPP)+CENTER;
  u = (ulong) floor(du);
  v = (ulong) floor(dv);
  // Get weights and heights
  x = du-floor(du);
  y = dv-floor(dv);
  weights[0] = (1-x)*(1-y); //W11
  weights[1] = (1-x)*(y); //W12
  weights[2] = (x)*(1-y); //W21
  weights[3] = (x)*(y); //W22
  u_max = (ulong) map_dims[idx][0];
  height = 0;
  for (int i=0; i<4; i++) {
    ui = u + i%2;
    vi = v + i/2;
    uv2vertid(ui,vi,u_max,&read_loc);
    read_loc = sizeof(float)*read_loc;
    fseek(files[idx],read_loc,SEEK_SET);
    fread((heights+i),sizeof(float),1,files[idx]);
    height += (double) weights[i]*heights[i];
    #ifdef DEBUG
      printf("Height at %lu,%lu is %f\n",ui,vi,heights[i]);
    #endif
  }
  #ifdef DEBUG
    printf("Height at %f,%f is %f\n",du,dv,height);
  #endif
  *radius = MOON_RADIUS+height;
}

#else
// Convert to Map
void Convert_LOLA_87S_5(double* ra, double* decl, double* radius, int idx) {
  /*
    Replicating the stereographic projection as laid out here:
    https://mathworld.wolfram.com/StereographicProjection.html
  */
 	const double MPP = 5.0;
  const double CENTER = 19999.5;
 	double phi,lambda,phi1,lambda0,k,rho,c,du,dv;
	ulong u,v, read_loc;
	float height;
	phi1 = -M_PI/2.;
	lambda0 = 0.;
  // First, we need to get the uv coords
	phi = *decl;
	lambda = *ra;
	k = (2*MOON_POLAR_RADIUS)/(1+sin(phi1)*sin(phi)+cos(phi1)*cos(phi)*cos(lambda-lambda0));
	dv = -round(k*(cos(phi1)*sin(phi)-sin(phi1)*cos(phi)*cos(lambda-lambda0))/MPP)+CENTER;
	du = round(k*cos(phi)*sin(lambda-lambda0)/MPP)+CENTER;
  u = (ulong) du;
  v = (ulong) dv;
  // Then, use the uv coords to get the radius
  uv2vertid(u,v,(ulong)map_dims[idx][0],&read_loc);
  read_loc = sizeof(float)*read_loc;
  fseek(files[idx],read_loc,SEEK_SET);
  fread(&height,sizeof(float),1,files[idx]);
  #ifdef DEBUG
    printf("Height at %lu,%lu is %f\n",u,v,height);
  #endif
  *radius = MOON_RADIUS+(double)height;
  // Now to go backwards and get the RA and Decl at uv
  du = (du-CENTER)*MPP;
  dv = (-dv+CENTER)*MPP;
  rho = sqrt(pow(du,2)+pow(dv,2));
  c = 2*atan2(rho,2*MOON_POLAR_RADIUS);
  *decl = asin(cos(c)*sin(phi1)+((dv*sin(c)*cos(phi1))/rho));
  *ra =  lambda0 + atan2(du*sin(c),rho*cos(phi1)*cos(c)-dv*sin(phi1)*sin(c));
  *decl = fmax(*decl,-M_PI/2.);
  *decl = fmin(*decl, M_PI/2.);
}

#endif

#endif
