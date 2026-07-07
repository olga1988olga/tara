import os
import tempfile
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import quote

from fastapi import FastAPI, Form, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from starlette.background import BackgroundTask

from asr.transcribe import _load_model as _load_whisper
from pipeline.app import run
from translation.translate import MODEL_NAME as TRANSLATION_MODEL
from translation.translate import _load_model as _load_translation
from translation.translate import list_cached_models
from tts.synthesize import VOICE_PATHS, load_voice

STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Warm all three model caches before accepting requests, so the first
    # real request is as fast as the second.
    _load_whisper("base")
    _load_translation(TRANSLATION_MODEL)
    load_voice()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def index() -> HTMLResponse:
    return HTMLResponse((STATIC_DIR / "index.html").read_text())


@app.get("/models")
def models() -> list[str]:
    return list_cached_models()


@app.get("/target-languages")
def target_languages() -> list[str]:
    return list(VOICE_PATHS.keys())


@app.post("/translate-audio")
async def translate_audio(
    file: UploadFile, model: str = Form(TRANSLATION_MODEL), target_language: str = Form("en")
) -> FileResponse:
    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as input_file:
        input_file.write(await file.read())
        input_path = input_file.name

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as output_file:
        output_path = output_file.name

    try:
        transcript, translation, language = run(
            input_path, output_path, translation_model=model, target_language=target_language
        )
    finally:
        os.remove(input_path)

    return FileResponse(
        output_path,
        media_type="audio/wav",
        headers={
            "X-Transcript": quote(transcript),
            "X-Translation": quote(translation),
            "X-Detected-Language": language,
        },
        background=BackgroundTask(os.remove, output_path),
    )
