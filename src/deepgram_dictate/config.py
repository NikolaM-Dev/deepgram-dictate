from __future__ import annotations

import argparse
import os
from dataclasses import dataclass


def _env(name: str, default: str) -> str:
    return os.environ.get(name, default)


@dataclass(frozen=True, slots=True)
class Config:
    model: str = "nova-3"
    language: str = "en"
    smart_format: bool = True
    paste: str = "ctrl+v"
    sounds: str = "marimba"
    cancel_window: float = 0.5
    min_seconds: float = 0.35
    samplerate: int = 16000


def parse_args(argv: list[str] | None = None) -> Config:
    parser = argparse.ArgumentParser(
        prog="deepgram-dictate",
        description="Push-to-talk dictation with the Deepgram pre-recorded API.",
    )
    parser.add_argument(
        "--model", default=_env("DICTATE_MODEL", "nova-3"), help="Deepgram model"
    )
    parser.add_argument(
        "--language",
        default=_env("DICTATE_LANGUAGE", "en"),
        help="BCP-47 language code, or 'multi' for code-switching (Nova-3)",
    )
    parser.add_argument(
        "--paste",
        default=_env("DICTATE_PASTE", "ctrl+v"),
        choices=["ctrl+v", "ctrl+shift+v", "type", "none"],
        help="How to deliver the transcript into the focused window",
    )
    parser.add_argument(
        "--sounds",
        default=_env("DICTATE_SOUNDS", "marimba"),
        choices=["pop", "marimba", "none"],
        help="Feedback sound theme",
    )
    parser.add_argument(
        "--cancel-window",
        type=float,
        default=float(_env("DICTATE_CANCEL_WINDOW", "0.5")),
        help="Press F7 again within this many seconds to cancel",
    )
    parser.add_argument(
        "--samplerate",
        type=int,
        default=int(_env("DICTATE_SAMPLERATE", "16000")),
        help="Microphone sample rate",
    )
    args = parser.parse_args(argv)

    return Config(
        model=args.model,
        language=args.language,
        paste=args.paste,
        sounds=args.sounds,
        cancel_window=args.cancel_window,
        samplerate=args.samplerate,
    )
