#!/bin/bash

#Access variables
echo "First argument: $1"
config_file_path="$1"

# 1. Install Docker
sudo ./bash_scripts/install_docker.sh

# 2. Install PyAudio dependencies
sudo ./bash_scripts/install_pyaudio_dependencies.sh

# 3. Install Conda if not already installed
if ! command -v conda &> /dev/null
then
    sudo ./bash_scripts/install_conda.sh
else
    echo "Conda is already installed."
fi

# 4. Create Conda environment from environment.yml
conda env create -f environment.yml

# Extract the environment name from environment.yml
env_name=$(grep 'name:' environment.yml | cut -d ' ' -f 2)

# Current Conda environment
current_env=$(conda info --json | grep '"active_prefix":' | cut -d '"' -f 4 | xargs basename)

# Activate only if not already active
if [ "$current_env" != "$env_name" ]; then
    echo "Activating $env_name..."
    conda activate "$env_name"
else
    echo "$env_name is already active."
fi

# Check if OpenVPN is installed
if ! command -v openvpn &> /dev/null; then
    echo "OpenVPN not found. Installing..."
    ./bash_scripts/install_openvpn.sh $config_file_path
else
    echo "OpenVPN is already installed."
fi
