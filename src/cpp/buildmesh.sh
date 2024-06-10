#!/bin/bash
g++ -c -o findPoints.o findPoints.cpp -fPIC -Wall -lm -I./mapping -I./ #-D DEBUG
g++ -shared -o libPoints.so findPoints.o
