import os
import torch
import torchaudio
import whisper
import onnxruntime
import numpy as np
import torchaudio.compliance.kaldi as kaldi
from typing import Callable, List, Union
from functools import partial
from loguru import logger

from viettts.utils.frontend_utils import split_text, normalize_text, mel_spectrogram
from viettts.tokenizer.tokenizer import get_tokenizer

class TTSFrontEnd:
    def __init__(
        self,
        speech_embedding_model: str,
        speech_tokenizer_model: str,
    ):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.tokenizer = get_tokenizer()
        option = onnxruntime.SessionOptions()
        option.graph_optimization_level = onnxruntime.GraphOptimizationLevel.ORT_ENABLE_ALL
        option.intra_op_num_threads = 1
        self.speech_embedding_session = onnxruntime.InferenceSession(
            speech_embedding_model,
            sess_options=option,
            providers=["CPUExecutionProvider"]
        )
        self.speech_tokenizer_session = onnxruntime.InferenceSession(
            speech_tokenizer_model,
            sess_options=option,
            providers=["CUDAExecutionProvider" if torch.cuda.is_available() else "CPUExecutionProvider"]
        )
        self.spk2info = {}

    def _extract_text_token(self, text: str):
        text_token = self.tokenizer.encode(text, allowed_special='all')
        text_token = torch.tensor([text_token], dtype=torch.int32).to(self.device)
        text_token_len = torch.tensor([text_token.shape[1]], dtype=torch.int32).to(self.device)
        return text_token, text_token_len

    def _extract_speech_token(self, speech: torch.Tensor):
        if speech.shape[1] / 16000 > 30:
            speech = speech[:, :int(16000 * 30)]
        feat = whisper.log_mel_spectrogram(speech, n_mels=128)
        speech_token = self.speech_tokenizer_session.run(
            None,
            {self.speech_tokenizer_session.get_inputs()[0].name: feat.detach().cpu().numpy(),
            self.speech_tokenizer_session.get_inputs()[1].name: np.array([feat.shape[2]], dtype=np.int32)}
        )[0].flatten().tolist()
        speech_token = torch.tensor([speech_token], dtype=torch.int32).to(self.device)
        speech_token_len = torch.tensor([speech_token.shape[1]], dtype=torch.int32).to(self.device)
        return speech_token, speech_token_len

    def _extract_spk_embedding(self, speech: torch.Tensor):
        feat = kaldi.fbank(
            waveform=speech,
            num_mel_bins=80,
            dither=0,
            sample_frequency=16000
        )
        feat = feat - feat.mean(dim=0, keepdim=True)
        embedding = self.speech_embedding_session.run(
            None,
            {self.speech_embedding_session.get_inputs()[0].name: feat.unsqueeze(dim=0).cpu().numpy()}
        )[0].flatten().tolist()
        embedding = torch.tensor([embedding]).to(self.device)
        return embedding

    def _extract_speech_feat(self, speech: torch.Tensor):
        speech_feat = mel_spectrogram(
            y=speech,
            n_fft=1024,
            num_mels=80,
            sampling_rate=22050,
            hop_size=256,
            win_size=1024,
            fmin=0,
            fmax=8000,
            center=False
        ).squeeze(dim=0).transpose(0, 1).to(self.device)
        speech_feat = speech_feat.unsqueeze(dim=0)
        speech_feat_len = torch.tensor([speech_feat.shape[1]], dtype=torch.int32).to(self.device)
        return speech_feat, speech_feat_len

    def preprocess_text(self, text, split=True) -> Union[str, List[str]]:
        text = normalize_text(text)
        if split:
            text = list(split_text(
                text=text,
                tokenize=partial(self.tokenizer.encode, allowed_special='all'),
                token_max_n=30,
                token_min_n=10,
                merge_len=5,
                comma_split=False
            ))
        return text

    def frontend_tts(
        self,
        text: str,
        prompt_speech_16k: Union[np.ndarray, torch.Tensor]
    ) -> dict:
        if isinstance(prompt_speech_16k, np.ndarray):
            prompt_speech_16k = torch.from_numpy(prompt_speech_16k)

        text_token, text_token_len = self._extract_text_token(text)
        speech_token, speech_token_len = self._extract_speech_token(prompt_speech_16k)
        prompt_speech_22050 = torchaudio.transforms.Resample(orig_freq=16000, new_freq=22050)(prompt_speech_16k)
        speech_feat, speech_feat_len = self._extract_speech_feat(prompt_speech_22050)
        embedding = self._extract_spk_embedding(prompt_speech_16k)

        model_input = {
            'text': text_token,
            'text_len': text_token_len,
            'flow_prompt_speech_token': speech_token, 'flow_prompt_speech_token_len': speech_token_len,
            'prompt_speech_feat': speech_feat,
            'prompt_speech_feat_len': speech_feat_len,
            'llm_embedding': embedding,
            'flow_embedding': embedding
        }
        return model_input


    def frontend_vc(
        self,
        source_speech_16k: Union[np.ndarray, torch.Tensor],
        prompt_speech_16k: Union[np.ndarray, torch.Tensor]
    ) -> dict:
        if isinstance(source_speech_16k, np.ndarray):
            source_speech_16k = torch.from_numpy(source_speech_16k)
        if isinstance(prompt_speech_16k, np.ndarray):
            prompt_speech_16k = torch.from_numpy(prompt_speech_16k)

        prompt_speech_token, prompt_speech_token_len = self._extract_speech_token(prompt_speech_16k)
        prompt_speech_22050 = torchaudio.transforms.Resample(orig_freq=16000, new_freq=22050)(prompt_speech_16k)
        prompt_speech_feat, prompt_speech_feat_len = self._extract_speech_feat(prompt_speech_22050)
        embedding = self._extract_spk_embedding(prompt_speech_16k)
        source_speech_token, source_speech_token_len = self._extract_speech_token(source_speech_16k)
        model_input = {
            'source_speech_token': source_speech_token,
            'source_speech_token_len': source_speech_token_len,
            'flow_prompt_speech_token': prompt_speech_token,
            'flow_prompt_speech_token_len': prompt_speech_token_len,
            'prompt_speech_feat': prompt_speech_feat,
            'prompt_speech_feat_len': prompt_speech_feat_len,
            'flow_embedding': embedding
        }
        return model_input
