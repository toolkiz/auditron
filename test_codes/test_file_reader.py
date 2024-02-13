import wave
CURRENT_FILE    = '/media/ankit/doc_ankit/reductstore_data/M00_S01_channel01_time000000600.wav'
CHUNK           = 24000

async def file_reader():
    """Read the current example in chunks of 50 bytes"""
    with wave.open(CURRENT_FILE, "rb") as wav_file:
        file = wav_file.readframes(wav_file.getnframes())

        for i in range(0, len(file), CHUNK):
            data = file[i:i+CHUNK]
            yield data


test = 0