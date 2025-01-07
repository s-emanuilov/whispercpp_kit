# WhisperCPP Kit 🎙️

[![PyPI version](https://badge.fury.io/py/whispercpp-kit.svg)](https://badge.fury.io/py/whispercpp-kit)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 🚀 A Python wrapper around [whisper.cpp](https://github.com/ggerganov/whisper.cpp) with model management and helper features.

## ✨ Features

- 🔄 Automatic building and setup of whisper.cpp
- 🎯 Simple, intuitive Python API
- 🔧 Built-in model management
- 🚦 Clear error messages and dependency checks
- 🎵 Automatic audio format conversion
- 🧵 Multi-threading support
- 🐳 Docker support
- 🎯 Support for custom and fine-tuned models
- ⚡ Cached builds for faster subsequent inference

## 📋 System Requirements

Before installing `whispercpp_kit`, ensure you have these system-level dependencies:

### Required dependencies 🛠️

- `git`
- `cmake`
- `ffmpeg`
- `make`
- `g++`/`gcc` (C++ compiler)
- Build essentials

### Installation commands 📦

<details>
<summary>Ubuntu/Debian</summary>

```bash
sudo apt update
sudo apt install git cmake ffmpeg build-essential
```
</details>

<details>
<summary>MacOS</summary>

```bash
brew install git cmake ffmpeg gcc make
```
</details>

<details>
<summary>CentOS/RHEL</summary>

```bash
sudo yum update
sudo yum groupinstall "Development Tools"
sudo yum install git cmake ffmpeg gcc-c++ make
```
</details>

> ⚠️ Windows is currently not supported. Please use WSL (Windows Subsystem for Linux) with Ubuntu.

## 🚀 Quick start

### Installation

```bash
pip install whispercpp_kit
```

### Basic usage

```python
from whispercpp_kit import WhisperCPP

# Initialize with default model
whisper = WhisperCPP(model_name="tiny.en")

# First-time setup (automatically done on first transcribe)
whisper.setup()

# Transcribe audio
text = whisper.transcribe("audio.mp3")
print(text)
```

### Advanced configuration

```python
# Using standard models
whisper = WhisperCPP(
    model_name="tiny.en",
    num_threads=8,        # Control threads number
    verbose=True,         # Enable verbose output
    cache_dir="./cache"   # Custom cache directory
)

# Using custom or fine-tuned models
whisper = WhisperCPP(model_path="/path/to/your/fine-tuned-model.bin")

# The library caches the built whisper.cpp source code
# This means subsequent runs will be faster as compilation is skipped
```

## 🐳 Troubleshooting

### Rebuilding whisper.cpp

If you encounter issues with the whisper.cpp binary, you can force a rebuild:

```python
import shutil
from whispercpp_kit import WhisperCPP

whisper = WhisperCPP(model_name="tiny.en")
# Force rebuild of whisper.cpp
shutil.rmtree(whisper.base_path)
whisper.setup()
```

### Common Issues

1. **Binary Deprecation Warning**: If you see a warning about the 'main' binary being deprecated, rebuild whisper.cpp using the steps above. The latest version uses 'whisper-cli' instead.

2. **Transcription Failures**: Ensure you have all required dependencies installed and sufficient permissions to execute the binary.

3. **Audio Format Issues**: The library automatically converts audio files using ffmpeg. Make sure ffmpeg is properly installed if you encounter audio-related errors.

## 🐳 Docker support

<details>
<summary>Docker Instructions</summary>

```bash
git clone https://github.com/s-emanuilov/whispercpp_kit
cd whispercpp_kit/examples/docker

# Build the image
docker build -t whispercpp_kit .

# Run with default model (base.en)
docker run -v $(pwd):/app/audio whispercpp_kit your_audio.mp3

# Using specific model
docker run -v $(pwd):/app/audio whispercpp_kit your_audio.mp3 tiny.en
```

See [examples/docker/README.md](examples/docker/README.md) for more details.
</details>

## 📝 License

MIT License - feel free to use in your projects!

## 🤝 Contributing

Contributions are welcome! Feel free to submit issues and pull requests.

##
