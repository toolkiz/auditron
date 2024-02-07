# create the audio control table
import numpy as np

from scipy.io import wavfile
from scipy.signal import resample, welch
from scipy.fft import rfft, rfftfreq

def calculate_amplitude(channel_data):
    return np.max(np.abs(channel_data))

def calculate_fundamental_frequency(channel_data, rate):
    # Perform Fourier Transform
    N = len(channel_data)
    yf = rfft(channel_data)
    xf = rfftfreq(N, 1 / rate)

    # Find the peak frequency
    idx = np.argmax(np.abs(yf))
    return xf[idx]

def calculate_energy(channel_data):
    return np.sum(channel_data.astype(float)**2) / len(channel_data)

# Load the audio file
file_path = 'sound_test/output_test.wav'
original_rate, data = wavfile.read('sound_test/output_test.wav')  # Load with original sample rate

print(data.shape, original_rate)

# resample to 48KHz
duration = data.shape[0] / original_rate
target_rate = 48000  # New sample rate: 48kHz
target_samples = int(duration * target_rate)

print(target_samples)

num_channels = data.shape[1]  # Number of channels
resampled_data = np.zeros((target_samples, num_channels))

for i in range(num_channels):
    resampled_data[:, i] = resample(data[:, i], target_samples)

    control_data = resampled_data[:, i].astype(np.float32)
    max_int16 = np.iinfo(np.int16).max
    control_data /= max_int16  # Normalize to -1.0 to 1.0

    # getting 1 value per channel
    amplitude = calculate_amplitude(control_data) / np.iinfo(np.int16).max
    frequency = calculate_fundamental_frequency(control_data, target_rate) / target_rate
    energy = calculate_energy(control_data)

    print(f"Channel {i+1}:")
    print(f"  Amplitude: {amplitude}")
    print(f"  Fundamental Frequency: {frequency} Hz")
    print(f"  Energy: {energy}")

wavfile.write('sound_test/resampled_output_test.wav', target_rate, resampled_data.astype(data.dtype))
print(resampled_data.shape)