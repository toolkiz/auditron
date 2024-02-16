#!/bin/bash

# EXAMPLE USAGE
# python reader.py -b bucket_name -t0 1707394990549623 - t1 1707395000581107


import asyncio
import argparse
import pickle
import numpy as np
import soundfile as sf
from reduct import Client, BucketSettings, QuotaType

'''
-----------------------------------------
# constructing the argument parse and parse the arguments
-----------------------------------------
'''
ap = argparse.ArgumentParser()

ap.add_argument("-b", "--bucket_name", type=str, default='likoranpp',
                # required=True, 
                help="bucket to read from")

ap.add_argument("-t0", "--start_time", type=int, default=1707921557112009,
                # required=True, 
                help="start-time with UNIX microsecond format")

ap.add_argument("-t1", "--stop_time", type=int, default=1707921657112009,
                # required=True, 
                help="bucket to read from")

ap.add_argument("-w", "--save_as_wave", type=bool, default=True,
                # required=True, 
                help="bucket to read from")

args = vars(ap.parse_args())

async def main(bucket_name, start_ts, stop_ts):
    # Create a ReductStore client
    async with Client("http://0.0.0.0:8383") as client:

        # creating the bucket
        bucket = await client.create_bucket(
            "likora",
            BucketSettings(quota_type=QuotaType.NONE),
            exist_ok=True,
        )
        
        arr = np.array([], dtype=np.int16)
        async for record in bucket.query(bucket_name, start=start_ts, stop=stop_ts):
            print(f"Record timestamp: {record.timestamp}")
            print(f"Record size: {record.size}")
            async for data in record.read(record.size):
                
                # data processing 
                # ------------------
                audio_data = np.frombuffer(data, dtype=np.int16)
                if arr.size == 0:
                    arr = audio_data.copy()
                else:
                    arr = np.append(arr, audio_data)

                # all_data_within_time.append(blender_data)
                
        return arr, int(record.labels['sample_rate']), int(record.labels['channels'])

if __name__ == "__main__":
    data, fs, channels = asyncio.run(main(bucket_name=args['bucket_name'], start_ts=args['start_time'], stop_ts=args['stop_time']))
    dividend = len(data) % channels 
    if dividend > 0:
        data = data[:-dividend] 
    data = data.reshape(-1, channels)
    sf.write('sample_output.wav', data, fs)

    # pickle.dump(array_object, open('blender_array.aud', 'wb'))
