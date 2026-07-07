import sys

from transformers import MarianMTModel, MarianTokenizer

MODEL_NAME = "Helsinki-NLP/opus-mt-de-en"


def translate(text: str, model_name: str = MODEL_NAME) -> str:
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    model = MarianMTModel.from_pretrained(model_name)
    inputs = tokenizer(text, return_tensors="pt", padding=True)
    translated = model.generate(**inputs)
    return tokenizer.decode(translated[0], skip_special_tokens=True)


if __name__ == "__main__":
    text = sys.argv[1] if len(sys.argv) > 1 else None
    if not text:
        print("Usage: python translate.py <text>")
        sys.exit(1)
    print(translate(text))
