from reduct import Client, BucketSettings, QuotaType
from time import time_ns
import wave

import asyncio

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

        # More complex case. Iterate over all records in the entry and read them in chunks
        async for record in bucket.query("M00_S01"):
            print(f"Record timestamp: {record.timestamp}")
            print(f"Record size: {record.size}")
            async for chunk in record.read(CHUNK):
                print(chunk)

if __name__ == "__main__":
    asyncio.run(main())
