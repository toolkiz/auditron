# get the libraries
import os
import pyaudio
import time
import argparse
from scipy.io.wavfile import write
import numpy as np
import sys

'''
-----------------------------------------
# constructing the argument parse and parse the arguments
-----------------------------------------
'''
ap = argparse.ArgumentParser()

ap.add_argument("-d", "--data_path", type=str, 
                default='/media/ankit/doc_ankit/reductstore_data', 
                help="base folder")

ap.add_argument("-s", "--sensor_name", type=str, 
                required=True, 
                help="name of the sensor")

ap.add_argument("-t", "--time_of_recording", type=int, 
                required=True, 
                help="Recording time")

ap.add_argument("-c", "--channel", type=int, 
                required=True, 
                help="Recording channel")

args = vars(ap.parse_args())

try:
    os.makedirs(args['data_path'])
except:
    pass


# create the pyaudio instance
p = pyaudio.PyAudio()

# choose the evident device by index
index = -1
for dev in range(p.get_device_count()):
    dev_info = p.get_device_info_by_index(dev)
    # print(dev_info)
    if 'Audient' in dev_info['name']:
        index = dev
        break

if index >= 0:

    # get the audient info
    info = p.get_device_info_by_index(index)

    # retrieve the constants
    CHANNELS = info['maxInputChannels']
    RATE = info['defaultSampleRate']
    CHUNK = 24000
    RECORD_SECONDS = int(args['time_of_recording'])
    FORMAT = pyaudio.paInt16
    WAVE_OUTPUT_FILENAME = f"{args['data_path']}/{args['sensor_name']}_channel{args['channel']:02d}_time{args['time_of_recording']:09d}.wav"
    
    # streaming inputs
    stream = p.open(format=pyaudio.paInt16, channels=CHANNELS, rate=int(RATE), input=True, input_device_index=index)
    # stream = p.open(format=pyaudio.paInt16, channels=int(info['maxInputChannels']), rate=int(info['defaultSampleRate']), input=True, input_device_index=index, frames_per_buffer=8192)

    start_time = time.time()
    frames = []
    try:
        print(f"Recording started at {time.strftime("%Y-%m-%d %H:%M:%S")} ...\n")
        while time.time() - start_time < RECORD_SECONDS:
            sys.stdout.write(f'\r{time.strftime("%Y-%m-%d %H:%M:%S")}')
            # sys.stdout.write(f'\r[INFO]recording for >> {int(time.time() - start_time):04d} seconds')
            data = stream.read(CHUNK)       
            # data = stream.read(int(info['defaultSampleRate'])//2)     
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

debug_res = 0

