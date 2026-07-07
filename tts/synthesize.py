import sys
import wave
from huggingface_hub import hf_hub_download
from piper import PiperVoice


def load_voice(lang: str = "en") -> PiperVoice:
    model_file = hf_hub_download(
        repo_id="rhasspy/piper-voices",
        filename="en/en_US/lessac/medium/en_US-lessac-medium.onnx",
    )
    config_file = hf_hub_download(
        repo_id="rhasspy/piper-voices",
        filename="en/en_US/lessac/medium/en_US-lessac-medium.onnx.json",
    )
    return PiperVoice.load(model_file, config_file)


def synthesize(text: str, output_path: str, voice: PiperVoice) -> None:
    with wave.open(output_path, "wb") as wav_file:
        voice.synthesize_wav(text, wav_file)


if __name__ == "__main__":
    text = sys.argv[1] if len(sys.argv) > 1 else "Hello, I am TARA."
    output = sys.argv[2] if len(sys.argv) > 2 else "output.wav"
    voice = load_voice()
    synthesize(text, output, voice)
    print(f"Saved to {output}")
