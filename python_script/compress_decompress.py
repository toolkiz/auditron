import os
import time
import wave

# Function to get duration of WAV file in seconds, considering the number of channels
def get_wav_duration(wav_file_path):
    with wave.open(wav_file_path, 'r') as wav_file:
        frames = wav_file.getnframes()
        rate = wav_file.getframerate()
        channels = wav_file.getnchannels()
        duration = frames / float(rate * channels)
        return duration
    
# Function to convert WAV to AAC using ffmpeg, and measure the time taken
def convert_wav_to_aac_and_measure_time(input_file, output_file):
    start_time = time.time()
    command = f'ffmpeg -y -f wav -i "{input_file}" -f adts "{output_file}"'
    os.system(command)
    end_time = time.time()
    conversion_time = end_time - start_time
    print(f"Conversion completed in: {conversion_time:.2f} seconds")
    return conversion_time

# Main function to execute the process
# input_folder_path = "/content"
wav_file_name = "sample_output.wav"
# input_wav_file = os.path.join(input_folder_path, wav_file_name)
output_aac_file = wav_file_name.rsplit(".", 1)[0] + ".aac"

# Get duration of WAV file, considering the number of channels
wav_duration = get_wav_duration(wav_file_name)
print(f"Duration of WAV file: {wav_duration:.2f} seconds")
      
# Convert the WAV file to AAC and measure conversion time
conversion_time = convert_wav_to_aac_and_measure_time(wav_file_name, output_aac_file)

# Calculate and print the scale ratio
scale_ratio = wav_duration / conversion_time
print(f"Scale ratio (seconds of recording to seconds it takes to compress): {scale_ratio:.2f}")