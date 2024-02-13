from reduct import Client, BucketSettings, QuotaType
from time import time_ns
import wave
import os

import asyncio

CURRENT_FILE = '/media/ankit/doc_ankit/reductstore_data/M00_S01_channel01_time000000600.wav'
bucket_name = os.path.basename(CURRENT_FILE)[:7]

async def main():
    # Create a ReductStore client
    async with Client("http://0.0.0.0:8383") as client:

        # creating the bucket
        bucket = await client.create_bucket(
            "likora",
            BucketSettings(quota_type=QuotaType.NONE),
            exist_ok=True,
        )

        with wave.open(CURRENT_FILE, "rb") as wav_file:
            file = wav_file.readframes(wav_file.getnframes())
            channels = wav_file.getnchannels()
            framerate = wav_file.getframerate()

            CHUNK = framerate * channels

            for i in range(0, len(file), CHUNK):
                data = file[i:i+CHUNK]
                # ts = i / CHUNK * 1e6

                await bucket.write(
                    bucket_name,
                    data,
                    # timestamp=ts,
                    content_length=len(data),
                    labels={'sample_rate': framerate,
                            'channels': channels,
                            'chunk_size': CHUNK}
                )

if __name__ == "__main__":
    asyncio.run(main())
