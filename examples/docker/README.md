# WhisperCPP Kit Docker Example

This example demonstrates how to use WhisperCPP Kit in a Docker container for easy audio transcription.

## Quick Start

1. Build the Docker image:
```bash
docker build -t whispercpp-kit .
```

2. Run transcription:
```bash
# Using default model (base.en)
docker run -v $(pwd):/app whispercpp-kit your_audio.mp3

# Using specific model
docker run -v $(pwd):/app whispercpp-kit your_audio.mp3 tiny.en
```

## Notes

- Place your audio files in the same directory as where you run the docker command
- The first run will download the selected model, which might take some time
- Supported audio formats: MP3, WAV, and other formats supported by FFmpeg 