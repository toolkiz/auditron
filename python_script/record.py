# get the libraries

import sys
import time
import asyncio
import pyaudio

import numpy as np

from datetime import datetime
from reduct import Client, BucketSettings, QuotaType

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
                    data = stream.read(int(info['defaultSampleRate']))
                    await bucket.write(f"test_2", 
                                       data,
                                       timestamp=int(datetime.now().timestamp() * 1e6),
                                       content_length=len(data),
                                       labels={'sample_rate': int(info['defaultSampleRate']),
                                               'channels': int(info['maxInputChannels']),
                                               'chunk_size': int(info['defaultSampleRate'])}
                                       )
                    
                    audio_data = np.frombuffer(data, dtype=np.int16)
                    audio_data = audio_data.reshape(-1, int(info['maxInputChannels']))

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
