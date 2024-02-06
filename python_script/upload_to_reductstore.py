from reduct import Client, BucketSettings, QuotaType
from time import time_ns
import wave

import asyncio

CURRENT_FILE = '/media/ankit/doc_ankit/reductstore_data/M00_S01_channel01_time000000600.wav'
CHUNK = 24000

async def main():
    # Create a ReductStore client
    async with Client("http://0.0.0.0:8383") as client:

        # creating the bucket
        bucket = await client.create_bucket(
            "likora",
            BucketSettings(quota_type=QuotaType.NONE),
            exist_ok=True,
        )

        # More complex case. Upload a file in chunks with a custom timestamp unix timestamp in microseconds
        """Read the current example in chunks of 50 bytes"""
        with wave.open(CURRENT_FILE, "rb") as wav_file:
            file = wav_file.readframes(wav_file.getnframes())

            for i in range(0, len(file), CHUNK):
                data = file[i:i+CHUNK]
                # yield data

                await bucket.write(
                    "M00_S04",
                    data,
                )

if __name__ == "__main__":
    asyncio.run(main())
