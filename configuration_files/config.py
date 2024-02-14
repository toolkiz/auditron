
import json
import os

modules = 8
sensors = 6

config_file_path = 'sensor_managements'
mapping_channel_name = 'likora_channels'
try:
    os.makedirs(config_file_path)
except:
    pass

likora_dict = {}
count = 1
for m in range(modules):
    for s in range(sensors):
        sensor_channel = f'M{m:02d}_S{s+1:02d}'
        likora_dict[sensor_channel] = count

        count +=1

# Serializing json
json_object = json.dumps(likora_dict, indent=4)
 
# Writing to sample.json
with open(f"{config_file_path}/{mapping_channel_name}.json", "w") as outfile:
    outfile.write(json_object)