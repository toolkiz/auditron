# get the libraries

import sys
import time
import pyaudio
import asyncio
import argparse

import numpy as np

from datetime import datetime
from scipy.fft import rfft, rfftfreq
from reduct import Client, BucketSettings, QuotaType

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

ap.add_argument("-en", "--entry_name", type=str, default='abstract',
                # required=True, 
                help="entry to read from")

args = vars(ap.parse_args())

class static_feature_extractor:
    def __init__(self):
        self.x = 0

    def calculate_amplitude(self, channel_data):
        return np.max(np.abs(channel_data))

    def calculate_fundamental_frequency(self, channel_data, sample_frequency):
        # Perform Fourier Transform
        N = len(channel_data)
        yf = rfft(channel_data)
        xf = rfftfreq(N, 1 / sample_frequency)

        # Find the peak frequency
        idx = np.argmax(np.abs(yf))
        return xf[idx]

    def calculate_energy(self, channel_data):
        return np.sum(channel_data.astype(float)**2) / len(channel_data)

chunk = 8192

async def main(ip_addr, bucket_name, entry_name):
    # create the pyaudio instance
    p = pyaudio.PyAudio()

    # choose the evident device by index
    index = -1
    for dev in range(p.get_device_count()):
        dev_info = p.get_device_info_by_index(dev)
        if 'Audient' in dev_info['name']:
            index = dev
            break

    if index >= 0:
        # get the audeient info
        info = p.get_device_info_by_index(index)

        # retrieve the constants
        async with Client(ip_addr) as client:

            bucket = await client.create_bucket(bucket_name,
                                                BucketSettings(quota_type=QuotaType.FIFO, quota_size=20_000_000_000_000), 
                                                exist_ok=True,)
        
            # streaming inputs
            stream = p.open(format=pyaudio.paInt16, channels=int(info['maxInputChannels']), rate=int(info['defaultSampleRate']), input=True, input_device_index=index, frames_per_buffer=4096)
            try:
                print(f"Recording started at {time.strftime('%Y-%m-%d %H:%M:%S')} ...")
                while True:
                    sys.stdout.write(f'\r{time.strftime("%Y-%m-%d %H:%M:%S")}')
                    ts = int(datetime.now().timestamp() * 1e6)
                    
                    data = stream.read(chunk, exception_on_overflow = False)

                    #signal compress
                    await bucket.write(entry_name, 
                                       data,
                                       timestamp=ts,
                                       content_length=len(data),
                                       labels={'sample_rate': int(info['defaultSampleRate']),
                                               'channels': int(info['maxInputChannels']),
                                               'chunk_size': chunk}
                                       )
                    
                    audio_data = np.frombuffer(data, dtype=np.int16)
                    audio_data = audio_data.reshape(-1, int(info['maxInputChannels']))

                    normalized_data = audio_data.astype(np.float32) / np.iinfo(np.int16).max  # Normalize entire array
                    feature_extractor = static_feature_extractor() # instantiating the feature extractor class --> more details in next version --> now a placeholder

                    # Calculate values for all channels using vectorized functions
                    blender_values = np.zeros((3, int(info['maxInputChannels'])))
                    blender_values[0, :] = np.apply_along_axis(feature_extractor.calculate_amplitude, 0, normalized_data)
                    blender_values[1, :] = np.apply_along_axis(feature_extractor.calculate_fundamental_frequency, 0, normalized_data, int(info['defaultSampleRate'])) / int(info['defaultSampleRate'])
                    blender_values[2, :] = np.apply_along_axis(feature_extractor.calculate_energy, 0, normalized_data)


                    blender_data = blender_values.flatten().tobytes()
                    await bucket.write(
                        f'{args["entry_name"]}_parameters',
                        blender_data,
                        timestamp=ts,
                        labels={'dtype': blender_values.dtype,
                                'channels': int(info['maxInputChannels']),
                                'parameters': 3}
                    )   

            except KeyboardInterrupt:
                print("Recording stopped by user")
                stream.stop_stream()
                stream.close()
                p.terminate()

            # put them in reduct database
            stream.stop_stream()
            stream.close()
            p.terminate()
    else:
        print('Device not found')

if __name__ == "__main__":
    asyncio.run(main(ip_addr=args['ip_address'], bucket_name=args['bucket_name'], entry_name=args['entry_name']))
