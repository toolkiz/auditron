import pyaudio

class Config:
    def __init__(self):
        self.value_per_channel = 100
        self.target_frequency = 48000 
        self.FORMAT = pyaudio.paInt16