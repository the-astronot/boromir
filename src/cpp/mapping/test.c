#include "stdio.h"
#include "maps.h"

int main(int argc, char** argv);

int main(int argc, char** argv) {
  double ra,decl,height;
  ra = -0.891307;
  decl = -M_PI/2.0 + 0.01;
  height = 100;
  load_maps();
  printf("RA is %f, Decl is %f\n",ra,decl);
  get_point(&ra,&decl,&height);
  close_maps();
  printf("RA is %f, Decl is %f\n",ra,decl);
  printf("Height is: %f\n",height);
  return 0;
}
