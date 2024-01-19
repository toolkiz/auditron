from scipy.io import wavfile

# Read the WAV file
sample_rate, data = wavfile.read('output_test.wav')

# data is a NumPy array containing the audio samples
# sample_rate is the sampling rate of the audio

print(sample_rate)
print(data.shape)
