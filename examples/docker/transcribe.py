import sys
import os
from whispercpp_kit import WhisperCPP

def main():
    if len(sys.argv) < 2:
        print("Usage: python transcribe.py <audio_file> [model_name]")
        print("Example: python transcribe.py audio.mp3 base.en")
        sys.exit(1)

    audio_file = sys.argv[1]
    model_name = sys.argv[2] if len(sys.argv) > 2 else "base.en"

    # Look for the audio file in both the current directory and the /app/audio directory
    possible_paths = [
        audio_file,  # Try direct path first
        os.path.join('/app/audio', audio_file)  # Try in audio subdirectory
    ]

    audio_path = next((path for path in possible_paths if os.path.exists(path)), None)
    
    if not audio_path:
        print(f"Error: Audio file not found in any of these locations: {possible_paths}")
        sys.exit(1)

    try:
        whisper = WhisperCPP(model_name=model_name)
        result = whisper.transcribe(audio_path)
        print(result)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()