#!/bin/bash

# Run Docker container in the background
docker run -d -p 8383:8383 -v ${PWD}/data:/data my_custom_image &

# for development
docker run -d -p 8383:8383 -v /media/ankit/likora_office/likora_onsite:/data reduct/store:latest

# Execute Python script in parallel
python my_script.py
