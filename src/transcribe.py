from __future__ import annotations

from typing import Optional

from faster_whisper import WhisperModel

_model: Optional[WhisperModel] = None


def load_model(size: str = "small", compute_type: str = "int8") -> None:
    global _model
    _model = WhisperModel(size, device="cpu", compute_type=compute_type)


def transcribe_file(path: str, language: str = "ja") -> str:
    if _model is None:
        # Lazy-load with defaults if not loaded explicitly
        load_model()
    assert _model is not None

    segments, info = _model.transcribe(
        path,
        language=language,
        vad_filter=True,
    )
    text = "".join(seg.text for seg in segments).strip()
    return text
