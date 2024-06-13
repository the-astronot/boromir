#include <iostream>
#include <fstream>
#include <string.h>
#include "linalg.h"
#include "common.h"
#include "maps.h"

using namespace linalg::aliases;

extern "C"{
int uv2_los(double u, double v, double NSubPixels, double2 fov,double2 camsize, double3 *los);

int vertIsNull(float* mesh);

int write_to_files(float* mesh, float* colors, ulong meshsize[2], const char* dirname);

int get_intersection(double3 pos, double3 los, float radius, double3* intercept);

int findPoint(double3 intercept, float* color, float* point);

int findPoints(double position[3], 
							double dcm[9], 
							int camsize[2], 
							double offsetsize[2], 
							float* mesh,
							float* colors,
							ulong meshsize[2],
							double N_SubPixels,
							double fov[2],
							const char* dirname);
}
