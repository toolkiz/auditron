#!/bin/bash

# EXAMPLE USAGE
# python reader.py -a http://0.0.0.0:8383 -bn bucket_name -en entry_name -t0 %Y-%m-%d %H:%M - t1 %Y-%m-%d %H:%M

import pickle
import asyncio
import argparse

import numpy as np

from reduct import Client
from datetime import datetime

'''
-----------------------------------------
# constructing the argument parse and parse the arguments
-----------------------------------------
'''
ap = argparse.ArgumentParser()

ap.add_argument("-a", "--ip_address", type=str, default="http://0.0.0.0:8383",
                # required=True, 
                help="bucket to read from")

ap.add_argument("-bn", "--bucket_name", type=str, default='likora',
                # required=True, 
                help="bucket to read from")

ap.add_argument("-en", "--entry_name", type=str, default='octopus_parameters',
                # required=True, 
                help="entry to read from")

ap.add_argument("-t0", "--start_time", type=str, default='2024-02-14 14:47',#1707918379279762,
                # required=True, 
                help="start-time with UNIX microsecond format")

ap.add_argument("-t1", "--stop_time", type=str, default='2024-02-14 14:48',#1708218379279762,
                # required=True, 
                help="bucket to read from")

args = vars(ap.parse_args())

def unix_microsecond_format(timestamp):
    '''
    Convert a timestamp string to Unix time in microseconds.

    This function takes a timestamp string formatted as '%Y-%m-%d %H:%M' and 
    converts it to the number of microseconds since the Unix epoch (Jan 1, 1970).

    Parameters:
    timestamp (str): A timestamp string in the format of '%Y-%m-%d %H:%M'.
    
    Returns:
    int: The Unix time representation of the input timestamp in microseconds.
    '''

    datetime_obj = datetime.strptime(timestamp, '%Y-%m-%d %H:%M')
    timestamp = datetime_obj.timestamp()
    microseconds = int(timestamp * 1_000_000)

    return microseconds

async def main(bucket_name, entry_name, start_ts, stop_ts):
    '''
    Asynchronously queries a ReductStore bucket and retrieves entries within a specified time range.

    This function creates a ReductStore client, queries the specified bucket for entries with the given name that fall within the start and stop timestamps, and processes the cumulative data into a feature data array.

    Parameters:
    bucket_name (str): The name of the ReductStore bucket to query.
    entry_name (str): The name of the entry to query within the bucket.
    start_ts (str): The start timestamp in '%Y-%m-%d %H:%M' format.
    stop_ts (str): The stop timestamp in '%Y-%m-%d %H:%M' format.

    Returns:
    np.ndarray: A numpy array containing the processed feature data from the queried records.
    '''

    # Create a ReductStore client
    async with Client(args["ip_address"]) as client:

        # get the bucket
        bucket = await client.get_bucket(bucket_name)

        # creating the time in milisecond
        ts0 = unix_microsecond_format(start_ts)
        ts1 = unix_microsecond_format(stop_ts)

        cumulative_data = []

        async for record in bucket.query(entry_name, start=ts0, stop=ts1, ttl=1000):

            data = await record.read_all()
            cumulative_data.append(data)
        
        if len(cumulative_data) > 0:
            feature_data = b''.join(cumulative_data)
            feature_data = np.frombuffer(feature_data, dtype=record.labels['dtype'])

            batch = len(cumulative_data)

            dividend = len(feature_data) % (int(record.labels['parameters']) * int(record.labels['channels']) * batch)
            if dividend > 0:
                feature_data = feature_data[:-dividend]
            feature_data = feature_data.reshape(batch, int(record.labels['channels']), int(record.labels['parameters']))
                    
            return feature_data
        else:
            return np.array(cumulative_data)

if __name__ == "__main__":
    array_object = asyncio.run(main(bucket_name=args['bucket_name'], entry_name=args['entry_name'], start_ts=args['start_time'], stop_ts=args['stop_time']))
    pickle.dump(array_object, open('blender_array.aud', 'wb'))
