# get the libraries

import sys
import time
import asyncio
import pyaudio

import numpy as np

from datetime import datetime
from scipy.fft import rfft, rfftfreq
from reduct import Client, BucketSettings, QuotaType

def calculate_amplitude(channel_data):
    return np.max(np.abs(channel_data))

def calculate_fundamental_frequency(channel_data, rate):
    # Perform Fourier Transform
    N = len(channel_data)
    yf = rfft(channel_data)
    xf = rfftfreq(N, 1 / rate)

    # Find the peak frequency
    idx = np.argmax(np.abs(yf))
    return xf[idx]

def calculate_energy(channel_data):
    return np.sum(channel_data.astype(float)**2) / len(channel_data)

bucket_name = 'test_3'

async def main():
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
        async with Client("http://localhost:8383") as client:

            bucket = await client.create_bucket("metricspace",
                                                BucketSettings(quota_type=QuotaType.FIFO, quota_size=1_000_000_000_000), 
                                                exist_ok=True,)
        
            # streaming inputs
            stream = p.open(format=pyaudio.paInt16, channels=int(info['maxInputChannels']), rate=int(info['defaultSampleRate']), input=True, input_device_index=index, frames_per_buffer=4096)
            try:
                print("Recording...")
                while True:
                    sys.stdout.write(f'\r{time.strftime("%Y-%m-%d %H:%M:%S")}')
                    ts = int(datetime.now().timestamp() * 1e6)
                    data = stream.read(int(info['defaultSampleRate']))
                    await bucket.write(f"{bucket_name}", 
                                       data,
                                       timestamp=ts,
                                       content_length=len(data),
                                       labels={'sample_rate': int(info['defaultSampleRate']),
                                               'channels': int(info['maxInputChannels']),
                                               'chunk_size': int(info['defaultSampleRate'])}
                                       )
                    
                    audio_data = np.frombuffer(data, dtype=np.int16)
                    audio_data = audio_data.reshape(-1, int(info['maxInputChannels']))

                    normalized_data = audio_data.astype(np.float32) / np.iinfo(np.int16).max  # Normalize entire array

                    # Calculate values for all channels using vectorized functions
                    blender_values = np.zeros((3, int(info['maxInputChannels'])))
                    blender_values[0, :] = np.apply_along_axis(calculate_amplitude, 0, normalized_data)
                    blender_values[1, :] = np.apply_along_axis(calculate_fundamental_frequency, 0, normalized_data, int(info['defaultSampleRate'])) / int(info['defaultSampleRate'])
                    blender_values[2, :] = np.apply_along_axis(calculate_energy, 0, normalized_data)

                    blender_data = blender_values.flatten().tobytes()
                    await bucket.write(
                        f'{bucket_name}_parameters',
                        blender_data,
                        timestamp=ts,
                        # content_length=len(blender_values.flatten()),
                        labels={'dtype': blender_values.dtype,
                                'channels': int(info['maxInputChannels']),
                                'parameters': 3}
                    )   

            except KeyboardInterrupt:
                print("Recording stopped by user")

            # put them in reduct database
            stream.stop_stream()
            stream.close()
            p.terminate()
    else:
        print('Device not found')

if __name__ == "__main__":

    asyncio.run(main())
