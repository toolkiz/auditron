import wave
import glob
import os

base_path = '/media/ankit/doc_ankit/reductstore_data'
res_path = '/media/ankit/doc_ankit/reductstore_data/only_byte_data'

try:
    os.makedirs(res_path)
except:
    pass

all_files = glob.glob(f'{base_path}/*.wav')

# file = '/media/ankit/doc_ankit/reductstore_data/M00_S01_channel01_time000000600.wav'

def read_wav_to_bytes(filename):
    with wave.open(filename, 'rb') as wav_file:
        return wav_file.readframes(wav_file.getnframes())
    
def save_bytes_to_wav(bytes_data, channels, framerate, sample_width, output_filename):
    with wave.open(output_filename, 'wb') as wav_file:
        # Set the parameters for the output file (ensure these match the source file or desired output)
        wav_file.setnchannels(channels)  # Number of channels
        wav_file.setsampwidth(sample_width)  # Sample width in bytes
        wav_file.setframerate(framerate)  # Frame rate
        wav_file.writeframes(bytes_data)

def get_wav_info(filename):
    with wave.open(filename, 'rb') as wav_file:
        channels = wav_file.getnchannels()
        framerate = wav_file.getframerate()
        sample_width = wav_file.getsampwidth()
        return channels, framerate, sample_width


for count, file in enumerate(all_files):
    print('--------------------------------------------------------------------------------')

    file_name = os.path.basename(file)
    output_filename = f'{res_path}/{file_name}'

    print(f'{count}: {file_name} >>> starting conversion')

    wav_bytes = read_wav_to_bytes(file)

    print(f'changed to bytes')

    channels, framerate, sample_width = get_wav_info(file)
    
    print(f'extracted features, saving to new file')
    
    save_bytes_to_wav(wav_bytes, channels, framerate, sample_width, output_filename)

    print(f'byte file saved, continuing with next')

    print('--------------------------------------------------------------------------------')

print(f'All file processed')

test = 0