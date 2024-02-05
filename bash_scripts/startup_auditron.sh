#!/bin/bash
# Run Docker container in the background
docker run -d -p 8383:8383 -v ${PWD}/data:/data my_custom_image

# Execute the recording script
python record.py  & # change the placeholder

python downsample.py & # for Maciej quantification 

python feature_extraction.py & # for getting the moving window features of the vibration data

python push_2_nas.py & # for linking the local data to datalake server
