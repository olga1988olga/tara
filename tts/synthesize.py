import sys
import wave
from functools import lru_cache

from huggingface_hub import hf_hub_download
from piper import PiperVoice

# One medium-quality Piper voice per supported target language, verified
# against rhasspy/piper's own VOICES.md rather than guessed.
VOICE_PATHS = {
    "en": "en/en_US/lessac/medium/en_US-lessac-medium.onnx",
    "de": "de/de_DE/thorsten/medium/de_DE-thorsten-medium.onnx",
    "fr": "fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx",
    "ru": "ru/ru_RU/irina/medium/ru_RU-irina-medium.onnx",
    "it": "it/it_IT/paola/medium/it_IT-paola-medium.onnx",
}


@lru_cache
def load_voice(lang: str = "en") -> PiperVoice:
    model_path = VOICE_PATHS[lang]
    model_file = hf_hub_download(repo_id="rhasspy/piper-voices", filename=model_path)
    config_file = hf_hub_download(repo_id="rhasspy/piper-voices", filename=f"{model_path}.json")
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
