import whisper
import sys

def transcribe(audio_path: str, model_size: str = "base") -> str:
    model = whisper.load_model(model_size)
    result = model.transcribe(audio_path)
    return result["text"]

if __name__ == "__main__":
    audio_path = sys.argv[1] if len(sys.argv) > 1 else None
    if not audio_path:
        print("Usage: python transcribe.py <audio_file>")
        sys.exit(1)
    print(transcribe(audio_path))
