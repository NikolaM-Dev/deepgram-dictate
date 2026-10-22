from __future__ import annotations

import threading

from deepgram import DeepgramClient

from .config import Config

_client: DeepgramClient | None = None
_client_lock = threading.Lock()


def _get_client() -> DeepgramClient:
    global _client
    with _client_lock:
        if _client is None:
            # Reads DEEPGRAM_API_KEY from the environment.
            _client = DeepgramClient()
        return _client


def transcribe(wav: bytes, cfg: Config) -> str:
    """Send a WAV file to the pre-recorded endpoint and return plain text."""
    response = _get_client().listen.v1.media.transcribe_file(
        request=wav,
        model=cfg.model,
        language=cfg.language,
        # Included add-ons only: no keyterm, redact, summarize or topics.
        smart_format=cfg.smart_format,
    )
    try:
        alternative = response.results.channels[0].alternatives[0]
        return (alternative.transcript or "").strip()
    except (AttributeError, IndexError, TypeError):
        return ""
