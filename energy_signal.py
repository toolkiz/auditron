from datasets import load_dataset, Audio
from transformers import EncodecModel, AutoProcessor

import torchaudio

# Load and pre-process the audio waveform
wav, sr = torchaudio.load("data/BH/2022-11-12T11-45-18Z.wav")