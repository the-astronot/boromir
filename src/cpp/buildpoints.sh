#!/bin/bash
g++ -c -o findPoints.o findPoints.cpp -fPIC -Wall
g++ -shared -o libPoints.so findPoints.o
