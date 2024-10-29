import os
import torchaudio
import soundfile
import numpy as np
from glob import glob
from huggingface_hub import snapshot_download

from viettts.utils.vad import get_speech


def load_wav(filepath: str, target_sr: int):
    speech, sample_rate = torchaudio.load(filepath)
    speech = speech.mean(dim=0, keepdim=True)
    if sample_rate != target_sr:
        assert sample_rate > target_sr, 'wav sample rate {} must be greater than {}'.format(sample_rate, target_sr)
        speech = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=target_sr)(speech)
    return speech


def save_wav(wav: np.ndarray, sr: int, filepath: str):
    soundfile.write(filepath, wav, sr)


def load_prompt_speech_from_file(filepath: str, min_duration: float=3, max_duration: float=5, return_numpy: bool=False):
    wav = load_wav(filepath, 16000)

    if wav.abs().max() > 0.9:
        wav = wav / wav.abs().max() * 0.9

    wav = get_speech(
        audio_input=wav.squeeze(0),
        min_duration=min_duration,
        max_duration=max_duration,
        return_numpy=return_numpy
    )
    return wav


def load_voices(voice_dir: str):
    files = glob(os.path.join(voice_dir, '*.wav')) + glob(os.path.join(voice_dir, '*.mp3'))
    voice_name_map = {
        os.path.basename(f).split('.')[0]: f
        for f in files
    }
    return voice_name_map


def download_model(save_dir: str):
    snapshot_download(repo_id="dangvansam/viet-tts", local_dir=save_dir)