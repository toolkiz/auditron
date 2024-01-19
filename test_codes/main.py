import pyaudio
import wave

p = pyaudio.PyAudio()
for i in range(p.get_device_count()):
    dev = p.get_device_info_by_index(i)
    print(f"Device {i}: {dev['name']}")
    if 'Audient' in dev['name']:
        break

# Set up
FORMAT = pyaudio.paInt16 # Audio format
CHANNELS = 1 # Number of audio channels
RATE = 44100 # Bit Rate
CHUNK = 1024 # Number of frames per buffer
RECORD_SECONDS = 5 # Record time
WAVE_OUTPUT_FILENAME = "output.wav"

audio = pyaudio.PyAudio()

# Start recording
stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK, input_device_index=i)
print("recording...")
frames = []

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)
print("finished recording")

# Stop recording
stream.stop_stream()
stream.close()
audio.terminate()

# Save the recorded data as a WAV file
waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
waveFile.setnchannels(CHANNELS)
waveFile.setsampwidth(audio.get_sample_size(FORMAT))
waveFile.setframerate(RATE)
waveFile.writeframes(b''.join(frames))
waveFile.close()
