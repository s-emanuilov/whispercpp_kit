import sys
from whispercpp_kit import WhisperCPP

def main():
    if len(sys.argv) < 2:
        print("Usage: python transcribe.py <audio_file> [model_name]")
        print("Example: python transcribe.py audio.mp3 base.en")
        sys.exit(1)

    audio_file = sys.argv[1]
    model_name = sys.argv[2] if len(sys.argv) > 2 else "base.en"

    try:
        whisper = WhisperCPP(model_name=model_name)
        result = whisper.transcribe(audio_file)
        print(result)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()