#include "findPoints.h"

extern "C" {
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
	float2 mapsize = {(float)i_mapsize[0],(float)i_mapsize[1]};
	float c_u,c_v;
	ulong idx;
	float RADIUS = 1737400;

	std::FILE* file = std::fopen(filename,"rb");
	if (file != NULL) {
		std::cout << "File opened" << std::endl;
	}

	for (ulong u=0; u<meshsize[0]; u++) {
		for (ulong v=0; v<meshsize[1]; v++) {
			c_u = ((float)u-offsetsize[0])/N_SubPixels;
			c_v = ((float)v-offsetsize[1])/N_SubPixels;
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
			findPoint(file,intercept,mapsize,colors+idx*2,mesh+(idx*3));
			//std::cout << "Actual Intercept: (" << *(mesh+((v*meshsize[0]+u)*3)) << ", " << *(mesh+((v*meshsize[0]+u)*3)+1) << ", " << *(mesh+((v*meshsize[0]+u)*3)+2) << ")" << std::endl;
		}
	}

	std::fclose(file);

	std::cout << "Writing to Files" << std::endl;

	write_to_files(mesh,colors,meshsize,dirname);

	return 0;
}

int uv2_los(float u, float v, float2 fov, float2 camsize, float3* los) {
	float angles_per_pixel_u = fov[0]/camsize[0];
	float angles_per_pixel_v = fov[1]/camsize[1];

	(*los)[0] = -(u-(camsize[0]/2.0)+.5)*angles_per_pixel_u;
	(*los)[1] = -(v-(camsize[1]/2.0)+.5)*angles_per_pixel_v;
	(*los)[2] = 1.0;

	float norm = sqrt(sum(pow(*los,2)));

	*los /= norm;

	return 0;
}

int uv2vertid(ulong u, ulong v, ulong u_pixels, ulong* id) {
	*id = v*u_pixels+u;
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

int findPoint(std::FILE* fp, float3 intercept, float2 mapsize, float* color, float* point) {
	// Get Moon UV
	float r,decl,ra,radius;
	ulong u,v;
	ulong read_loc,idx;
	short read_radius;

	r = sqrt(sum(pow(intercept,2)));
	decl = asin(fmax(-1,fmin(intercept[2]/r,1)));
	if (fabs(cos(decl)) < 1e-10) {
		ra = 0;
	} else {
		// ra = arctan2(ijk[1]/(r*cos(decl)),ijk[0]/(r*cos(decl)))
		ra = atan2(intercept[1]/(r*cos(decl)),intercept[0]/(r*cos(decl)));
	}
	// u = ((U_PIXELS-1)/2)+(U_PIXELS/360.*rad2deg(ra))
	// v = ((V_PIXELS-1)/2)-(V_PIXELS/180.*rad2deg(decl))
	u = (ulong) round(((mapsize[0]-1)/2.0)+((mapsize[0]/(2*M_PI))*ra));
	v = (ulong) round((mapsize[1]-1)/2.0)-((mapsize[1]/M_PI)*decl);
	// ra = 2*pi*((u+.5)/U_PIXELS) - pi
	// decl = -pi*((v+.5)/V_PIXELS) + pi/2
	ra = 2.0*M_PI*(((float)u+0.5)/mapsize[0]) - M_PI;
	decl = -M_PI*(((float)v+0.5)/mapsize[1]) + M_PI/2.0;
	*color = (((mapsize[0]-1)/2.0)+((mapsize[0]/(2*M_PI))*ra))/mapsize[0];
	*(color+1) = 1.0-((((mapsize[1]-1)/2.0)-((mapsize[1]/M_PI)*decl))/mapsize[1]);
	//u = round(*color*mapsize[0]);
	//v = round(mapsize[1]*(1-*(color+1)));
	uv2vertid(u,v,(ulong)mapsize[0],&idx);
	read_loc = sizeof(short)*idx;
	std::fseek(fp,read_loc,SEEK_SET);
	std::fread(&read_radius,sizeof(short),1,fp);

	radius = 1737400+0.5*(float)read_radius;

	*point = radius*cos(decl)*cos(ra);
	*(point+1) = radius*cos(decl)*sin(ra);
	*(point+2) = radius*sin(decl);
	// colors[u,v,:] = array([cu/U_PIXELS,1-(cv/V_PIXELS)])
	//std::cout << "Point: U=" << u << ", V=" << v << std::endl;

	//std::cout << "Point: RA=" << ra*180/M_PI << ", DECL=" << decl*180/M_PI << std::endl;
	
	//std::cout << "Point: (" << *point << ", " << *(point+1) << ", " << *(point+2) << ")" << std::endl;
	return 0;
}


}

