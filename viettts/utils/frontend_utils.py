import re
import torch
import numpy as np
import torch.utils.data
from vinorm import TTSnorm
from librosa.filters import mel as librosa_mel_fn
from scipy.io.wavfile import read

MAX_WAV_VALUE = 32768.0


def remove_urls_and_links(text):
    url_pattern = r"http[s]?:\/\/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+|www\.[a-zA-Z0-9.\/]+"
    markdown_image_pattern = r"!\[.*?\]\(http[s]?:\/\/.*?\)"
    text = re.sub(markdown_image_pattern, '', text, 0, re.MULTILINE)
    text = re.sub(url_pattern, '', text, 0, re.MULTILINE)
    return text


def remove_emojis(text):
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"  # other miscellaneous symbols
        "\U000024C2-\U0001F251" 
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U0001F004-\U0001F0CF"  # Mahjong and Playing Cards
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub(r'', text)


def remove_punc(text):
    text = (text
        .replace('<input>', '')
        .replace("..", ".")
        .replace("!.", "!")
        .replace('!', ".")
        .replace("?.", "?")
        .replace("?", ".")
        .replace(" .", ".")
        .replace(" ,", ",")
        .replace('"', "")
        .replace("'", "")
        .replace("AI", "Ây Ai")
        .replace("A.I", "Ây Ai")
        .replace("$", "")
        .replace("(", "")
        .replace(")", "")
        .replace("**", "")
        .replace(" = ", " bằng ")
        .replace("#", "")
        .replace('\\', '')
        .replace('```', '')
        .replace('- ', '')
        .replace('+ ', '')
        .replace(":", "")
        .replace(",,", ",")
        .replace(", ,", ",")
        .replace(",.", ".")
        .replace(".,", ".")
        .replace("..", ".")
        .replace(". .", ".")
    )
    text = re.sub(r'\n+', ' ', text)
    text = ' '.join([t for t in text.split() if t.strip()])
    text = text.strip()
    return text


def normalize_text(text: str) -> str:
    text = text.strip()
    text = remove_urls_and_links(text)
    text = remove_emojis(text)
    text = remove_punc(text)
    text = TTSnorm(text, lower=False)
    return text


def split_text(text: str, tokenize, token_max_n=80, token_min_n=60, merge_len=20, comma_split=False):
    def calc_utt_length(_text: str):
        return len(tokenize(_text))

    def should_merge(_text: str):
        return len(tokenize(_text)) < merge_len

    pounc = ['.', '?', '!', ';', ':']
    if comma_split:
        pounc.extend(['，', ','])

    if text[-1] not in pounc:
        text += "."

    st = 0
    utts = []
    for i, c in enumerate(text):
        if c in pounc:
            if len(text[st: i]) > 0:
                utts.append(text[st: i] + c)
            if i + 1 < len(text) and text[i + 1] in ['"', '”']:
                tmp = utts.pop(-1)
                utts.append(tmp + text[i + 1])
                st = i + 2
            else:
                st = i + 1

    final_utts = []
    cur_utt = ""
    for utt in utts:
        if calc_utt_length(cur_utt + utt) > token_max_n and calc_utt_length(cur_utt) > token_min_n:
            final_utts.append(cur_utt)
            cur_utt = ""
        cur_utt = cur_utt + utt
    if len(cur_utt) > 0:
        if should_merge(cur_utt) and len(final_utts) != 0:
            final_utts[-1] = final_utts[-1] + cur_utt
        else:
            final_utts.append(cur_utt)

    final_utts = [utt.strip() for utt in final_utts]
    return final_utts


def dynamic_range_compression(x, C=1, clip_val=1e-5):
    return np.log(np.clip(x, a_min=clip_val, a_max=None) * C)


def dynamic_range_decompression(x, C=1):
    return np.exp(x) / C


def dynamic_range_compression_torch(x, C=1, clip_val=1e-5):
    return torch.log(torch.clamp(x, min=clip_val) * C)


def dynamic_range_decompression_torch(x, C=1):
    return torch.exp(x) / C


def spectral_normalize_torch(magnitudes):
    output = dynamic_range_compression_torch(magnitudes)
    return output


def spectral_de_normalize_torch(magnitudes):
    output = dynamic_range_decompression_torch(magnitudes)
    return output


mel_basis = {}
hann_window = {}


def mel_spectrogram(y, n_fft, num_mels, sampling_rate, hop_size, win_size, fmin, fmax, center=False):
    if torch.min(y) < -1.0:
        print("min value is ", torch.min(y))
    if torch.max(y) > 1.0:
        print("max value is ", torch.max(y))

    global mel_basis, hann_window  # pylint: disable=global-statement
    if f"{str(fmax)}_{str(y.device)}" not in mel_basis:
        mel = librosa_mel_fn(sr=sampling_rate, n_fft=n_fft, n_mels=num_mels, fmin=fmin, fmax=fmax)
        mel_basis[str(fmax) + "_" + str(y.device)] = torch.from_numpy(mel).float().to(y.device)
        hann_window[str(y.device)] = torch.hann_window(win_size).to(y.device)

    y = torch.nn.functional.pad(
        y.unsqueeze(1), (int((n_fft - hop_size) / 2), int((n_fft - hop_size) / 2)), mode="reflect"
    )
    y = y.squeeze(1)

    spec = torch.view_as_real(
        torch.stft(
            y,
            n_fft,
            hop_length=hop_size,
            win_length=win_size,
            window=hann_window[str(y.device)],
            center=center,
            pad_mode="reflect",
            normalized=False,
            onesided=True,
            return_complex=True,
        )
    )

    spec = torch.sqrt(spec.pow(2).sum(-1) + (1e-9))

    spec = torch.matmul(mel_basis[str(fmax) + "_" + str(y.device)], spec)
    spec = spectral_normalize_torch(spec)

    return spec


# def tokenize(data, get_tokenizer, allowed_special):
#     """ Decode text to chars or BPE
#         Inplace operation

#         Args:
#             data: Iterable[{key, wav, txt, sample_rate}]

#         Returns:
#             Iterable[{key, wav, txt, tokens, label, sample_rate}]
#     """
#     tokenizer = get_tokenizer()
#     for sample in data:
#         assert 'text' in sample
#         sample['text_token'] = tokenizer.encode(sample['text'], allowed_special=allowed_special)
#         sample['tts_text_token'] = tokenizer.encode(sample['tts_text'], allowed_special=allowed_special)
