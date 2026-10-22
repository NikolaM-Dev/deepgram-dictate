from __future__ import annotations

import subprocess
from pathlib import Path

_ASSETS = Path(__file__).resolve().parent / "assets"

# Sounds are copied from Handy (MIT) so feedback matches what Nikola already knows.
_FILES = {
    ("pop", "start"): "pop_start.wav",
    ("pop", "stop"): "pop_stop.wav",
    ("pop", "cancel"): "marimba_stop.wav",
    ("marimba", "start"): "marimba_start.wav",
    ("marimba", "stop"): "marimba_stop.wav",
    ("marimba", "cancel"): "pop_stop.wav",
}


def play(event: str, theme: str) -> None:
    """Play 'start', 'stop' or 'cancel' without blocking the caller."""
    if theme == "none":
        return
    name = _FILES.get((theme, event))
    if name is None:
        return
    path = _ASSETS / name
    if not path.exists():
        return
    subprocess.Popen(
        ["paplay", str(path)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
