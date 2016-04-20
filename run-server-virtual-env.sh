#!/bin/bash

# This script is used to run dwwikiserver.py
# using virtual python environment.

# directory for virtual python environment
virtual_env_dir=~/src/pyvirt1/dwwikienv

# enable virtual environment
source $virtual_env_dir/bin/activate

# run the server
python dwwikiserver.py

