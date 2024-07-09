#include <iostream>
#include <fstream>
#include <string.h>
#include "linalg.h"
#include "common.h"
#include "maps.h"

using namespace linalg::aliases;

extern "C"{
int uv2_los(float u, float v, float NSubPixels, float2 fov, float2 camsize, float3 *los);

int vertIsNull(float* mesh);

int write_to_files(float* mesh, float* colors, ulong meshsize[2], const char* dirname);

int create_tris(float* mesh, float* colors, ulong* tris, ulong meshsize[2], ulong* count);

int get_intersection(float3 pos, float3 los, float radius, float3* intercept);

int findPoint(float3 intercept, float* color, float* point);

int findPoints(float position[3], 
							float dcm[9], 
							int camsize[2], 
							float offsetsize[2], 
							float* mesh,
							float* colors,
							ulong* tris,
							ulong* count,
							ulong meshsize[2],
							float N_SubPixels,
							float fov[2],
							const char* dirname);
}
