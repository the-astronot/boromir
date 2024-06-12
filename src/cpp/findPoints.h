#include <iostream>
#include <fstream>
#include <string.h>
#include "linalg.h"
#include "common.h"
#include "maps.h"

using namespace linalg::aliases;

extern "C"{
int uv2_los(float u, float v, float2 fov, float2 camsize, float3 *los);

int vertIsNull(float* mesh);

int write_to_files(float* mesh, float* colors, ulong meshsize[2], const char* dirname);

int get_intersection(float3 pos, float3 los, float radius, float3* intercept);

int findPoint(float3 intercept, float* color, float* point);

int findPoints(float position[3], 
							float dcm[9], 
							int camsize[2], 
							double offsetsize[2], 
							float* mesh,
							float* colors,
							ulong meshsize[2],
							double N_SubPixels,
							float fov[2],
							const char* dirname);
}
