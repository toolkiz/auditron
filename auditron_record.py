# get the libraries
import pyaudio
import time
from scipy.io.wavfile import write
import numpy as np
import asyncio
import zlib

from pathlib import Path
from time import time_ns
from reduct import Client, BucketSettings, QuotaType

CHUNK = 24000
RECORD_SECONDS = 10
FORMAT = pyaudio.paInt16

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
        RATE = info['defaultSampleRate']
        WAVE_OUTPUT_FILENAME = "output_test_0.wav"

        async with Client("http://localhost:8383") as client:

            bucket = await client.create_bucket("metricspace",
                                                BucketSettings(quota_type=QuotaType.FIFO, quota_size=1_000_000_000), 
                                                exist_ok=True,)
        
            # streaming inputs
            stream = p.open(format=FORMAT, channels=CHANNELS, rate=int(RATE), input=True, input_device_index=index)
            start_time = time.time()
            frames = []
            try:
                print("Recording...")
                while time.time() - start_time < RECORD_SECONDS:
                    data = stream.read(CHUNK)
                    await bucket.write(f"auditron_zipped", data)
                    frames.append(data)
            except KeyboardInterrupt:
                print("Recording stopped by user")

            # put them in reduct database
            stream.stop_stream()
            stream.close()
            p.terminate()

            # Save the recorded audio as a WAV file
            data = b''.join(frames)
            audio_data = np.frombuffer(data, dtype=np.int16)

            dividend = len(audio_data) % CHANNELS
            if dividend > 0:
                audio_data = audio_data[:-dividend]
            audio_data = audio_data.reshape(-1, CHANNELS)

            write(WAVE_OUTPUT_FILENAME, int(RATE), audio_data)

            print(f"Audio saved as {WAVE_OUTPUT_FILENAME}")
    else:
        print('Device not found')

if __name__ == "__main__":

    asyncio.run(main())

