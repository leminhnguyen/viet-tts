<!-- # VietTTS: An Open-Source Vietnamese Text to Speech -->
<p align="center">
  <img src="assets/viet-tts-medium.png" style="width: 22%">
  <h1 align="center"style="color: white; font-weight: bold; font-family:roboto"><span style="color: white; font-weight: bold; font-family:roboto">VietTTS</span>: An Open-Source Vietnamese Text to Speech</h1>
</p>
<p align="center">
  <a href="https://github.com/dangvansam/viet-tts"><img src="https://img.shields.io/github/stars/dangvansam/viet-tts?style=social"></a>
  <a href="https://huggingface.co/dangvansam/viet-tts"><img src="https://img.shields.io/badge/%F0%9F%A4%97HuggingFace-Model-yellow"></a>
  <a href="https://huggingface.co/dangvansam/viet-tts"><img src="https://img.shields.io/badge/%F0%9F%A4%97HuggingFace-Demo-green"></a>
    <a href="https://github.com/dangvansam/viet-tts"><img src="https://img.shields.io/badge/Python-3.10-green"></a>
    <!-- <a href="https://pypi.org/project/viet-tts" target="_blank"><img src="https://img.shields.io/pypi/v/viet-tts.svg" alt="PyPI Version"> -->
    <a href="LICENSE"><img src="https://img.shields.io/github/license/dangvansam/viet-asr"></a>
    </a>
    <br>
    <a href="README.md"><img src="https://img.shields.io/badge/README-English-blue"></a>
    <a href="README_VN.md"><img src="https://img.shields.io/badge/README-Tiếng Việt-red"></a>
</p>

**VietTTS** is an open-source toolkit providing the community with a powerful Vietnamese TTS model, capable of natural voice synthesis and robust voice cloning. Designed for effective experimentation, **VietTTS** supports research and application in Vietnamese voice technologies.

## ⭐ Key Features
- **TTS**: Text-to-Speech generation with any voice via prompt audio
- **VC**: Voice Conversion (TODO)

## 🛠️ Installation

VietTTS can be installed via either a Python installer or Docker.

### Python Installer
```bash
git clone https://github.com/dangvansam/viet-tts.git
cd viet-tts

# (Optional) Install Python environment with conda, you could also use virtualenv 
conda create --name viettts python=3.10
conda activate viettts

# Install
pip install -e . && pip cache purge
```

### Docker

1. Install [Docker](https://docs.docker.com/get-docker/), [NVIDIA Driver](https://www.nvidia.com/download/index.aspx), [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html), and [CUDA](https://developer.nvidia.com/cuda-downloads).

2. Run the following commands:
```bash
git clone https://github.com/dangvansam/viet-tts.git
cd viet-tts

# Build docker images
docker compose build

# Run with docker-compose - will create server at: http://localhost:8298
docker compose up -d

# Run with docker run - will create server at: http://localhost:8298
docker run -itd --gpu=alls -p 8298:8298 -v ./pretrained-models:/app/pretrained-models -n viet-tts-service viet-tts:latest viettts server --host 0.0.0.0 --port 8298

# Show available voices
docker exec viet-tts-service viettts show-voices
```

## 🚀 Usage

### Built-in Voices 🤠
You can use available voices bellow to synthesize speech.
<details>
  <summary>Expand</summary>

| ID  | Voice                  | Gender | Play Audio                                        |
|-----|-----------------------|--------|--------------------------------------------------|
| 1   | nsnd-le-chuc          | 👨     | <audio controls src="samples/nsnd-le-chuc.mp3"></audio>  |
| 2   | speechify_10          | 👩     | <audio controls src="samples/speechify_10.wav"></audio>  |
| 3   | atuan                 | 👨     | <audio controls src="samples/atuan.wav"></audio>         |
| 4   | speechify_11          | 👩     | <audio controls src="samples/speechify_11.wav"></audio>  |
| 5   | cdteam                | 👨     | <audio controls src="samples/cdteam.wav"></audio>       |
| 6   | speechify_12          | 👩     | <audio controls src="samples/speechify_12.wav"></audio>  |
| 7   | cross_lingual_prompt  | 👩     | <audio controls src="samples/cross_lingual_prompt.wav"></audio>  |
| 8   | speechify_2           | 👩     | <audio controls src="samples/speechify_2.wav"></audio>   |
| 9   | diep-chi              | 👨     | <audio controls src="samples/diep-chi.wav"></audio>      |
| 10  | speechify_3           | 👩     | <audio controls src="samples/speechify_3.wav"></audio>   |
| 11  | doremon               | 👨     | <audio controls src="samples/doremon.mp3"></audio>       |
| 12  | speechify_4           | 👩     | <audio controls src="samples/speechify_4.wav"></audio>   |
| 13  | jack-sparrow          | 👨     | <audio controls src="samples/jack-sparrow.mp3"></audio>  |
| 14  | speechify_5           | 👩     | <audio controls src="samples/speechify_5.wav"></audio>   |
| 15  | nguyen-ngoc-ngan      | 👩     | <audio controls src="samples/nguyen-ngoc-ngan.wav"></audio>  |
| 16  | speechify_6           | 👩     | <audio controls src="samples/speechify_6.wav"></audio>   |
| 17  | nu-nhe-nhang          | 👩     | <audio controls src="samples/nu-nhe-nhang.wav"></audio>  |
| 18  | speechify_7           | 👩     | <audio controls src="samples/speechify_7.wav"></audio>   |
| 19  | quynh                 | 👩     | <audio controls src="samples/quynh.wav"></audio>         |
| 20  | speechify_8           | 👩     | <audio controls src="samples/speechify_8.wav"></audio>   |
| 21  | speechify_9           | 👩     | <audio controls src="samples/speechify_9.wav"></audio>   |
| 22  | son-tung-mtp    | 👨     | <audio controls src="samples/son-tung-mtp.wav"></audio>  |
| 23  | zero_shot_prompt      | 👩     | <audio controls src="samples/zero_shot_prompt.wav"></audio>  |
| 24  | speechify_1           | 👩     | <audio controls src="samples/speechify_1.wav"></audio>   |

  <div>
  </div>
</details>

### Command Line Interface (CLI)
The VietTTS Command Line Interface (CLI) allows you to quickly generate speech directly from the terminal. Here's how to use it:
```bash
# Usage
viettts --help

# Start API Server
viettts server --host 0.0.0.0 --port 8298

# Synthesis speech from text
viettts synthesis --text "Xin chào" --voice 0 --output test.wav

# List all built-in voices
viettts show-voices
```

### API Client
#### Python (OpenAI Client)
You need to set environment variables for the OpenAI Client:
```bash
# Set base_url and API key as environment variables
export OPENAI_BASE_URL=http://localhost:8298
export OPENAI_API_KEY=viet-tts # not use in current version
```
To create speech from input text:
```python
from pathlib import Path
from openai import OpenAI

client = OpenAI()

output_file_path = Path(__file__).parent / "speech.wav"

with client.audio.speech.with_streaming_response.create(
  model='tts-1',
  voice='cdteam',
  input='Xin chào Việt Nam.',
  speed=1.0,
  response_format='wav'
) as response:
  response.stream_to_file('a.wav')
```

#### CURL
```bash
curl http://localhost:8298/v1/audio/speech \
  -H "Authorization: Bearer viet-tts" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1",
    "input": "Xin chào Việt Nam.",
    "voice": "son-tung-mtp"
  }' \
  --output speech.wav
```

#### Node
```js
import fs from "fs";
import path from "path";
import OpenAI from "openai";

const openai = new OpenAI();

const speechFile = path.resolve("./speech.wav");

async function main() {
  const mp3 = await openai.audio.speech.create({
    model: "tts-1",
    voice: "1",
    input: "Xin chào Việt Nam.",
  });
  console.log(speechFile);
  const buffer = Buffer.from(await mp3.arrayBuffer());
  await fs.promises.writeFile(speechFile, buffer);
}
main();
```

## 🙏 Acknowledgement
- 💡 Borrowed code from [Cosyvoice](https://github.com/FunAudioLLM/CosyVoice)
- 🎙️ VAD model from [silero-vad](https://github.com/snakers4/silero-vad)
- 📝 Text normalization with [Vinorm](https://github.com/v-nhandt21/Vinorm)

## 📜 License
The **VietTTS** source code is released under the **Apache 2.0 License**. Pre-trained models and audio samples are licensed under the **CC BY-NC License**, based on an in-the-wild dataset. We apologize for any inconvenience this may cause.

## ⚠️ Disclaimer
The content provided above is for academic purposes only and is intended to demonstrate technical capabilities. Some examples are sourced from the internet. If any content infringes on your rights, please contact us to request its removal.

## 💬 Contact 
- Facebook: https://fb.com/sam.rngd
- GitHub: https://github.com/dangvansam
- Email: dangvansam98@gmail.com