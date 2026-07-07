import sys

# Windows' default console encoding (cp1252) can't represent Cyrillic/CJK/
# Arabic - without this, printing a non-Latin translation crashes the
# request instead of just logging it.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from asr.transcribe import transcribe
from translation.translate import MODEL_NAME as DEFAULT_TRANSLATION_MODEL
from translation.translate import translate
from tts.synthesize import load_voice, synthesize


def run(
    input_audio: str,
    output_audio: str,
    translation_model: str = DEFAULT_TRANSLATION_MODEL,
    target_language: str = "en",
) -> tuple[str, str, str]:
    transcript, language = transcribe(input_audio)
    print(f"Transcript [{language}]: {transcript}")

    translation = translate(
        transcript, model_name=translation_model, source_language=language, target_language=target_language
    )
    print(f"Translation [{target_language}]: {translation}")

    voice = load_voice(target_language)
    synthesize(translation, output_audio, voice)
    print(f"Saved to {output_audio}")

    return transcript, translation, language


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python -m pipeline.app <input_audio> <output_audio> [translation_model] [target_language]")
        sys.exit(1)
    kwargs = {}
    if len(sys.argv) > 3:
        kwargs["translation_model"] = sys.argv[3]
    if len(sys.argv) > 4:
        kwargs["target_language"] = sys.argv[4]
    run(sys.argv[1], sys.argv[2], **kwargs)
