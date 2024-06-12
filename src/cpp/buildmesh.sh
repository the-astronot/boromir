#!/bin/bash
g++ -c -o findPoints.o findPoints.cpp -fPIC -Wall -lm -I./mapping -I./ -D BILINEAR_INTERP #-D DEBUG
g++ -shared -o libPoints.so findPoints.o
