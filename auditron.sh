#!/bin/bash

# Run Docker container in the background
docker run -d -p 8383:8383 -v ${PWD}/data:/data my_custom_image &

# Execute Python script in parallel
python my_script.py
