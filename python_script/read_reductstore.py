import wave
import asyncio

import numpy as np

from time import time_ns
from scipy.signal import resample
from scipy.fft import rfft, rfftfreq
from reduct import Client, BucketSettings, QuotaType

target_rate = 8e3
bucket_name = 'M00_S01'

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


async def main():
    # Create a ReductStore client
    async with Client("http://0.0.0.0:8383") as client:

        # creating the bucket
        bucket = await client.create_bucket(
            "likora",
            BucketSettings(quota_type=QuotaType.NONE),
            exist_ok=True,
        )

        # More complex case. Iterate over all records in the entry and read them in chunks
        async for record in bucket.query(bucket_name):
            print(f"Record timestamp: {record.timestamp}")
            print(f"Record size: {record.size}")
            CHUNK = int(record.labels['channels']) * int(record.labels['sample_rate'])
            async for data in record.read(CHUNK):
                
                # data processing 
                # ------------------

                # getting the audio data from the byte format

                # --------------------------------------------------------------------------
                audio_data = np.frombuffer(data, dtype=np.int16)

                dividend = len(audio_data) % int(record.labels['channels'])
                if dividend > 0:
                    audio_data = audio_data[:-dividend]
                audio_data = audio_data.reshape(-1, int(record.labels['channels']))
                # --------------------------------------------------------------------------

                # # getting the signal processed for blender                
                # blender_values = np.zeros((3, int(record.labels['channels'])))

                # for i in range(int(record.labels['channels'])):
                #     control_data = audio_data[:, i].astype(np.float32)
                #     max_int16 = np.iinfo(np.int16).max
                #     control_data /= max_int16  # Normalize to -1.0 to 1.0

                #     # getting 1 value per channel
                #     blender_values[0,i] = calculate_amplitude(control_data) / np.iinfo(np.int16).max #calculating the amplitude values
                #     blender_values[1,i] = calculate_fundamental_frequency(control_data, target_rate) / target_rate #calculating the fundamental frequencies
                #     blender_values[2,i] = calculate_energy(control_data) #calculating the total energy
                
                max_int16 = np.iinfo(np.int16).max
                normalized_data = audio_data.astype(np.float32) / max_int16  # Normalize entire array

                # Calculate values for all channels using vectorized functions
                blender_values = np.zeros((3, int(record.labels['channels'])))
                blender_values[0, :] = np.apply_along_axis(calculate_amplitude, 0, normalized_data)
                blender_values[1, :] = np.apply_along_axis(calculate_fundamental_frequency, 0, normalized_data, target_rate) / target_rate
                blender_values[2, :] = np.apply_along_axis(calculate_energy, 0, normalized_data)

                
                blender_data = blender_values.flatten().tobytes()
                await bucket.write(
                    f'{bucket_name}_parameters',
                    blender_data,
                    # timestamp=ts,
                    # content_length=len(blender_values.flatten()),
                    labels={'dtype': blender_values.dtype,
                            'channels': int(record.labels['channels']),
                            'parameters': 3}
                )
                

if __name__ == "__main__":
    asyncio.run(main())
