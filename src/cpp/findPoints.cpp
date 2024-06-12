#include "findPoints.h"

extern "C" {
int findPoints(float position[3], 
							float dcm[9], 
							int camsize[2], 
							double offsetsize[2], 
							float* mesh,
							float* colors,
							ulong meshsize[2],
							double N_SubPixels,
							float fov[2],
							const char* dirname) 
							{
	
	float2 lin_camsize = {(float)camsize[0],(float)camsize[1]};
	float2 lin_fov = {fov[0],fov[1]};
	float3 lin_position = {position[0],position[1],position[2]};
	float3x3 mat_dcm = {{dcm[0],dcm[1],dcm[2]},{dcm[3],dcm[4],dcm[5]},{dcm[6],dcm[7],dcm[8]}};
	float3 los;
	int status;
	float3 intercept;
	float3 new_los;
	double c_u,c_v;
	ulong idx;
	float RADIUS = 1737400;

	load_maps();

	for (ulong u=0; u<meshsize[0]; u++) {
		for (ulong v=0; v<meshsize[1]; v++) {
			c_u = ((double)u-offsetsize[0])/N_SubPixels;
			c_v = ((double)v-offsetsize[1])/N_SubPixels;
			uv2_los(c_u,c_v,lin_fov,lin_camsize,&los);
			//std::cout << "LOS: (" << los[0] << ", " << los[1] << ", " << los[2] << ")" <<std::endl;
			new_los = mul(transpose(mat_dcm),los);
			//std::cout << "NEW_LOS: (" << new_los[0] << ", " << new_los[1] << ", " << new_los[2] << ")" <<std::endl;
			status = get_intersection(lin_position,new_los,RADIUS,&intercept);
			uv2vertid(u,v,meshsize[0],&idx);
			if (status == 0) {
				//std::cout << "INTERCEPTION: (" << intercept[0] << ", " << intercept[1] << ", " << intercept[2] << ")" << std::endl;
			} else {
				//std::cout << "NO INTERCEPT" << std::endl;
				for (ulong i=0; i<3; i++) {
					*(mesh+(3*idx)+i) = 0;
				}
				continue;
			}
			//findPoint(file,intercept,mapsize,colors+((v+u*meshsize[1])*2),mesh+((v+u*meshsize[1])*3));
			findPoint(intercept,colors+idx*2,mesh+(idx*3));
			//std::cout << "Actual Intercept: (" << *(mesh+((v*meshsize[0]+u)*3)) << ", " << *(mesh+((v*meshsize[0]+u)*3)+1) << ", " << *(mesh+((v*meshsize[0]+u)*3)+2) << ")" << std::endl;
		}
	}

	close_maps();

	std::cout << "Writing to Files" << std::endl;

	write_to_files(mesh,colors,meshsize,dirname);

	return 0;
}

int uv2_los(float u, float v, float2 fov, float2 camsize, float3* los) {
	float angles_per_pixel_u = fov[0]/camsize[0];
	float angles_per_pixel_v = fov[1]/camsize[1];

	(*los)[0] = (u-(camsize[0]/2.0)+.5)*angles_per_pixel_u;
	(*los)[1] = -(v-(camsize[1]/2.0)+.5)*angles_per_pixel_v;
	(*los)[2] = 1.0;

	float norm = sqrt(sum(pow(*los,2)));

	*los /= norm;

	return 0;
}

int vertIsNull(float* mesh) {
	float thresh = 1;
	return (fabs(*(mesh))+fabs(*(mesh+1))+fabs(*(mesh+2)))<thresh;
}

int write_to_files(float* mesh, float* colors, ulong meshsize[2], const char* dirname) {
	std::FILE *vertptr, *colorptr, *faceptr;
	char vertfile[1024],colorfile[1024],facefile[1024];
	ulong idx,count;
	ulong idxs[3];
	strcpy(vertfile,dirname);
	strcat(vertfile,"verts.bin");
	strcpy(colorfile,dirname);
	strcat(colorfile,"colors.bin");
	strcpy(facefile,dirname);
	strcat(facefile,"faces.bin");

	vertptr = std::fopen(vertfile,"wb+");
	colorptr = std::fopen(colorfile,"wb+");
	faceptr = std::fopen(facefile,"wb+");

	count = 0;

	for (ulong u=0; u<meshsize[0]; u++) {
		for (ulong v=0; v<meshsize[1]; v++) {
			uv2vertid(v,u,meshsize[1],&idx);
			// Add Vertex
			//std::cout << "Point: " << idx << " ==> ";
			for (ulong i=0; i<3; i++) {
				std::fwrite(mesh+(idx*3)+i,sizeof(float),1,vertptr);
				//std::cout << *(mesh+(idx*3)+i) << ",";
			}
			//std::cout << std::endl;
			// Add Colors
			for (ulong i=0; i<2; i++) {
				std::fwrite(colors+(idx*2)+i,sizeof(float),1,colorptr);
			}
			// Add Vertices
			if ((u > 0) && (v > 0)) {
				//if sum(np.abs(mesh[u-1,v]*mesh[u-1,v-1]*mesh[u,v])) > 0:
				uv2vertid(u-1,v,meshsize[0],idxs);
				uv2vertid(u-1,v-1,meshsize[0],idxs+1);
				uv2vertid(u,v,meshsize[0],idxs+2);
				if (!(vertIsNull(mesh+(3*idxs[0]))||vertIsNull(mesh+(3*idxs[1]))||vertIsNull(mesh+(3*idxs[2])))) {
					for (ulong i=0; i<3; i++) {
						std::fwrite((idxs+i),sizeof(ulong),1,faceptr);
					}
					//std::cout << "Added Face: (" << *(idxs) << "," << *(idxs+1) << "," << *(idxs+2) << ")" << std::endl;
					count++;
				}
				//if sum(np.abs(mesh[u-1,v-1]*mesh[u,v-1]*mesh[u,v])) > 0:
				uv2vertid(u-1,v-1,meshsize[0],idxs);
				uv2vertid(u,v-1,meshsize[0],idxs+1);
				uv2vertid(u,v,meshsize[0],idxs+2);
				if (!(vertIsNull(mesh+(3*idxs[0]))||vertIsNull(mesh+(3*idxs[1]))||vertIsNull(mesh+(3*idxs[2])))) {
					for (ulong i=0; i<3; i++) {
						//*(idxs+i) = *(idxs+i)+1;
						std::fwrite((idxs+i),sizeof(ulong),1,faceptr);
					}
					//std::cout << "Added Face: (" << *(idxs) << "," << *(idxs+1) << "," << *(idxs+2) << ")" << std::endl;
					count++;
				}
			}
		}
	}

	std::cout << "Face Count: " << count << std::endl; 

	std::fclose(vertptr);
	std::fclose(colorptr);
	std::fclose(faceptr);

	return 0;
}

int get_intersection(float3 pos, float3 los, float radius, float3* intercept) {
	float nabla,d,d1,d2;
	float edge_thresh = 10000;

	nabla = pow(dot(los,pos),2)-(sum(pow(pos,2))-pow(radius,2));

	d1 = -dot(los,pos)-sqrt(fabs(nabla));
	d2 = -dot(los,pos)+sqrt(fabs(nabla));

	if (nabla < edge_thresh) {
		// Peeking around Moon, take further point
		if (fabs(d1) > fabs(d2)) {
			d = d1;
		} else {
			d = d2;
		}
	} else if (nabla < 0) {
		// Ain't no Moon there, chief
		return 1;
	} else {
		// Visible point on Moon is closer point
		if (fabs(d1) < fabs(d2)) {
			d = d1;
		} else {
			d = d2;
		}
	}
	*intercept = (pos + (los*d));

	return 0;
}

int findPoint(float3 intercept, float* color, float* point) {
	// Get Moon UV
	float r;
	double ra,decl;
	double radius;

	r = sqrt(sum(pow(intercept,2)));
	decl = asin(fmax(-1.0,fmin(intercept[2]/r,1.0)));
	if (fabs(cos(decl)) < 1e-20) {
		ra = 0;
	} else {
		ra = atan2(intercept[1]/(r*cos(decl)),intercept[0]/(r*cos(decl)));
	}

	// Trying out the new system
	get_point(&ra,&decl,&radius);

	#ifdef DEBUG
		std::cout << "RA: " << ra << ", Decl: " << decl << ", Radius: " << radius << std::endl;
	#endif

	*color = (float)(ra/(2*M_PI)+0.5);
	*(color+1) = (float)(0.5+(decl/(M_PI)));

	*point = (float) radius*cos(decl)*cos(ra);
	*(point+1) = (float) radius*cos(decl)*sin(ra);
	*(point+2) = (float) radius*sin(decl);
	return 0;
}


}

