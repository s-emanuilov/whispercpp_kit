# WhisperCPP Kit

A wrapper arround [whisper.cpp](https://github.com/ggerganov/whisper.cpp) with additional helper features like model management capabilities.

While `whispercpp_kit` will automatically build and set up whisper.cpp for you, it requires certain system-level dependencies (git, cmake, ffmpeg) to be pre-installed on your system. 
If any dependency is missing, the library will provide a clear error message indicating what needs to be installed.


## System requirements

Before installing `whispercpp_kit`, ensure you have the following dependencies installed:

- `git`
- `cmake`
- `ffmpeg`

### Installing dependencies

Ubuntu/Debian:
```bash
sudo apt update
sudo apt install git cmake ffmpeg
```

MacOS:
```bash
brew install git cmake ffmpeg
```

## Installation

```bash
pip install whispercpp_kit
```

## Quickstart

```python
from whispercpp_kit import WhisperCPP

whisper = WhisperCPP(model_name="tiny.en")
# whisper = Whisper(model_path="/custom/pathggml-large-v3-turbo-q5_0.bin")

output = whisper.transcribe("input.mp3")
print(output)
```

