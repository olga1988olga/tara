import os
import re
import sys
from functools import lru_cache
from pathlib import Path

from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, MarianMTModel, MarianTokenizer

MODEL_NAME = "Helsinki-NLP/opus-mt-de-en"

# Maps ISO 639-1 codes (both Whisper's detected source language and the
# user-selected target language) to NLLB's FLORES-200 codes, needed because
# NLLB (unlike opus-mt) is one model that translates between whichever
# source/target languages you tell it via these codes. Whisper doesn't
# detect dialects (Darija comes back as plain "ar", same as Standard
# Arabic) - not solved here, just worth knowing before the Darija phase.
LANGUAGE_TO_NLLB = {
    "en": "eng_Latn",
    "de": "deu_Latn",
    "fr": "fra_Latn",
    "es": "spa_Latn",
    "it": "ita_Latn",
    "pt": "por_Latn",
    "nl": "nld_Latn",
    "ar": "arb_Arab",
    "ru": "rus_Cyrl",
    "zh": "zho_Hans",
    "ja": "jpn_Jpan",
    "tr": "tur_Latn",
}


def _is_nllb(model_name: str) -> bool:
    return "nllb" in model_name.lower()


@lru_cache
def _load_model(model_name: str):
    if _is_nllb(model_name):
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    else:
        tokenizer = MarianTokenizer.from_pretrained(model_name)
        model = MarianMTModel.from_pretrained(model_name)
    return tokenizer, model


def list_cached_models() -> list[str]:
    # Scans the HF hub cache for already-downloaded translation models, so
    # the frontend can offer a dropdown that never triggers a surprise
    # multi-hundred-MB download for a mistyped/unfamiliar model name.
    cache_dir = Path(os.environ.get("HF_HOME", Path.home() / ".cache" / "huggingface")) / "hub"
    if not cache_dir.exists():
        return []
    models = []
    for entry in cache_dir.iterdir():
        if entry.is_dir() and entry.name.startswith("models--"):
            name = entry.name.removeprefix("models--").replace("--", "/", 1)
            if "opus-mt" in name or "nllb" in name.lower():
                models.append(name)
    return sorted(models)


def _split_sentences(text: str) -> list[str]:
    return [s.strip() for s in re.findall(r"[^.!?]+[.!?]?", text.strip()) if s.strip()]


def translate(
    text: str, model_name: str = MODEL_NAME, source_language: str = "en", target_language: str = "en"
) -> str:
    # opus-mt models are sentence-level translators - fed multiple sentences
    # at once, they tend to stop after the first rather than translating
    # everything, so translate one sentence at a time and join the results.
    # Note: opus-mt models are fixed-pair, so target_language only actually
    # takes effect when using an NLLB model.
    tokenizer, model = _load_model(model_name)
    is_nllb = _is_nllb(model_name)
    forced_bos_token_id = None

    if is_nllb:
        nllb_source = LANGUAGE_TO_NLLB.get(source_language)
        nllb_target = LANGUAGE_TO_NLLB.get(target_language)
        if nllb_source is None:
            raise ValueError(f"No NLLB language code mapped for detected language '{source_language}'")
        if nllb_target is None:
            raise ValueError(f"No NLLB language code mapped for target language '{target_language}'")
        tokenizer.src_lang = nllb_source
        forced_bos_token_id = tokenizer.convert_tokens_to_ids(nllb_target)

    translations = []
    for sentence in _split_sentences(text):
        inputs = tokenizer(sentence, return_tensors="pt", padding=True)
        generate_kwargs = {"forced_bos_token_id": forced_bos_token_id} if is_nllb else {}
        translated = model.generate(**inputs, **generate_kwargs)
        translations.append(tokenizer.decode(translated[0], skip_special_tokens=True))
    return " ".join(translations)


if __name__ == "__main__":
    text = sys.argv[1] if len(sys.argv) > 1 else None
    if not text:
        print("Usage: python translate.py <text>")
        sys.exit(1)
    print(translate(text))
