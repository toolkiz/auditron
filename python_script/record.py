# get the libraries

import sys
import time
import asyncio
import pyaudio

from reduct import Client, BucketSettings, QuotaType

CHUNK = 24000
FORMAT = pyaudio.paInt16
RATE = CHUNK

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
        CHANNELS = info['maxInputChannels']
        async with Client("http://localhost:8383") as client:

            bucket = await client.create_bucket("metricspace",
                                                BucketSettings(quota_type=QuotaType.FIFO, quota_size=1_000_000_000), 
                                                exist_ok=True,)
        
            # streaming inputs
            stream = p.open(format=FORMAT, channels=CHANNELS, rate=int(RATE), input=True, input_device_index=index)
            frames = []
            try:
                print("Recording...")
                while True:
                    sys.stdout.write(f'\r{time.strftime("%Y-%m-%d %H:%M:%S")}')
                    data = stream.read(CHUNK)
                    await bucket.write(f"raw_data", data)
                    frames.append(data)
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
