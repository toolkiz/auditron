#!/bin/bash

# EXAMPLE USAGE
# python reader.py -b bucket_name -t0 '%Y-%m-%d %H:%M' - t1 '%Y-%m-%d %H:%M'

import pytz
import pickle
import asyncio
import argparse

import numpy as np

from datetime import datetime
from reduct import Client, BucketSettings, QuotaType

'''
-----------------------------------------
# constructing the argument parse and parse the arguments
-----------------------------------------
'''
ap = argparse.ArgumentParser()

ap.add_argument("-b", "--bucket_name", type=str, default='likoranpp_parameters',
                # required=True, 
                help="bucket to read from")

ap.add_argument("-t0", "--start_time", type=str, default='2024-02-14 14:47',#1707918379279762,
                # required=True, 
                help="start-time with UNIX microsecond format")

ap.add_argument("-t1", "--stop_time", type=str, default='2024-02-14 14:48',#1708218379279762,
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
        
        all_data_within_time = []

        datetime_obj0 = datetime.strptime(start_ts, '%Y-%m-%d %H:%M')
        # datetime_obj_utc0 = datetime_obj0.replace(tzinfo=pytz.utc)
        timestamp0 = datetime_obj0.timestamp()
        ts0 = int(timestamp0 * 1_000_000)

        datetime_obj1 = datetime.strptime(stop_ts, '%Y-%m-%d %H:%M')
        # datetime_obj_utc1 = datetime_obj1.replace(tzinfo=pytz.utc)
        timestamp1 = datetime_obj1.timestamp()
        ts1 = int(timestamp1 * 1_000_000)

        async for record in bucket.query(bucket_name, start=ts0, stop=ts1):
            print(f"Record timestamp: {record.timestamp}")
            print(f"Record size: {record.size}")
            
            async for data in record.read(record.size):
                
                # data processing 
                # ------------------
                blender_data = np.frombuffer(data, dtype=record.labels['dtype'])
                blender_data = blender_data.reshape(-1, int(record.labels['parameters']))

                all_data_within_time.append(blender_data)
                
        return np.array(all_data_within_time)

if __name__ == "__main__":
    array_object = asyncio.run(main(bucket_name=args['bucket_name'], start_ts=args['start_time'], stop_ts=args['stop_time']))

    pickle.dump(array_object, open('blender_array.aud', 'wb'))

    # print(array_object
