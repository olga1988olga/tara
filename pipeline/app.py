import sys

from asr.transcribe import transcribe
from translation.translate import translate
from tts.synthesize import load_voice, synthesize


def run(input_audio: str, output_audio: str) -> None:
    transcript = transcribe(input_audio)
    print(f"Transcript: {transcript}")

    translation = translate(transcript)
    print(f"Translation: {translation}")

    voice = load_voice()
    synthesize(translation, output_audio, voice)
    print(f"Saved to {output_audio}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python -m pipeline.app <input_audio> <output_audio>")
        sys.exit(1)
    run(sys.argv[1], sys.argv[2])
