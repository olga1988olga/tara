import sys
from functools import lru_cache

import whisper


@lru_cache
def _load_model(model_size: str):
    return whisper.load_model(model_size)


def transcribe(audio_path: str, model_size: str = "base") -> tuple[str, str]:
    # No `language=` passed to .transcribe() - Whisper auto-detects the
    # spoken language from the audio itself, which we surface here instead
    # of discarding.
    model = _load_model(model_size)
    result = model.transcribe(audio_path)
    return result["text"], result["language"]

if __name__ == "__main__":
    audio_path = sys.argv[1] if len(sys.argv) > 1 else None
    if not audio_path:
        print("Usage: python transcribe.py <audio_file>")
        sys.exit(1)
    text, language = transcribe(audio_path)
    print(f"[{language}] {text}")
