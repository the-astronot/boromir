#!/bin/bash
source ../.venv/bin/activate
python3 blender_prep.py
python3 blender_test_redux.py
blender moon_test.blend -b -P autorender.py
deactivate
