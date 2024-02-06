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
            "likora_data",
            BucketSettings(quota_type=QuotaType.FIFO, quota_size=1_000_000_000),
            exist_ok=True,
        )

        # More complex case. Upload a file in chunks with a custom timestamp unix timestamp in microseconds
        async def file_reader():
            """Read the current example in chunks of 50 bytes"""
            with wave.open(CURRENT_FILE, "rb") as wav_file:
                file = wav_file.readframes(wav_file.getnframes())

                for i in range(0, len(file), CHUNK):
                    data = file[i:i+CHUNK]
                    yield data

        ts = int(time_ns() / 10000)
        await bucket.write(
            "M00_S01",
            file_reader(),
            timestamp=ts,
            content_length=wave.open(CURRENT_FILE, 'rb').getnframes(),
        )

if __name__ == "__main__":
    asyncio.run(main())


# ask how to load wav data 