#!/bin/bash

# Define Miniconda installer URL
MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"

# Define installer path
INSTALLER_PATH="$HOME/miniconda.sh"

# Download Miniconda installer
curl -o "$INSTALLER_PATH" "$MINICONDA_URL"

# Make installer executable
chmod +x "$INSTALLER_PATH"

# Run installer
bash "$INSTALLER_PATH" -b

# Optionally, initialize Miniconda
"$HOME/miniconda3/bin/conda" init

# Clean up installer
rm "$INSTALLER_PATH"

echo "Miniconda installation complete."
