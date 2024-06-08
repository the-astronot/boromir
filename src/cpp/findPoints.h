#include <iostream>
#include <fstream>
#include <string.h>
#include "linalg.h"
#include "common.h"

using namespace linalg::aliases;

extern "C"{
int uv2_los(float u, float v, float2 fov, float2 camsize, float3 *los);

int uv2vertid(ulong u, ulong v, ulong u_pixels, ulong* id);

int vertIsNull(float* mesh);

int write_to_files(float* mesh, float* colors, ulong meshsize[2], const char* dirname);

int get_intersection(float3 pos, float3 los, float radius, float3* intercept);

int findPoint(std::FILE* fp, float3 intercept, float2 mapsize, float* color, float* point);

int findPoints(float position[3], 
							float dcm[9], 
							int camsize[2], 
							float offsetsize[2], 
							float* mesh,
							float* colors,
							ulong meshsize[2],
							float N_SubPixels,
							int i_mapsize[2],
							float fov[2],
							const char* filename,
							const char* dirname);
}
