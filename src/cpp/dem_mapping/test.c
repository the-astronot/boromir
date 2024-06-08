#include "stdio.h"
#include "maps.h"

int main(int argc, char** argv);

int main(int argc, char** argv) {
  float ra,decl,height;
  int status;
  ra = 0;
  decl = -3.1410/2.0;
  height = 100;
  load_maps();
  status = get_point(&ra,&decl,&height);
  printf("Status is: %d\n",status);
  close_maps();
  printf("Height is: %f\n",height);
  return 0;
}
