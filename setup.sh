#!/bin/bash

# This script links pyslurm.py to an alias in ~/bin, and makes it executable
EXE=$(pwd)/pyslurm/pyslurm.py
ln -s $EXE $HOME/bin/pyslurm.py

chmod +x $EXE

