#!/bin/bash

# This file will make the pyslurm.py script executable by adding the PySlurm base directory
# to your PATH

# Add to PATH
DIR="$(pwd)/pyslurm"
echo PATH="$DIR:$PATH" >> ~/.bashrc
source "$HOME/.bashrc"

# Add executable permissions
chmod +x "$DIR/pyslurm.py"
