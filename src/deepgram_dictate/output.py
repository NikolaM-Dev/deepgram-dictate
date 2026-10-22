from __future__ import annotations

import logging
import subprocess
import time

from .config import Config

log = logging.getLogger(__name__)


def deliver(text: str, cfg: Config) -> None:
    """Copy the text, then paste it into the focused window."""
    log.info("transcript: %s", text)
    _set_clipboard(text)

    if cfg.paste == "none":
        return

    # Give the clipboard owner a moment to take the selection.
    time.sleep(0.15)

    if cfg.paste == "type":
        _run(["xdotool", "type", "--clearmodifiers", "--delay", "2", "--", text])
        return

    _run(["xdotool", "key", "--clearmodifiers", cfg.paste])


def _set_clipboard(text: str) -> None:
    try:
        # xclip forks a daemon to own the selection, so detach its stdio.
        subprocess.run(
            ["xclip", "-selection", "clipboard", "-i"],
            input=text.encode(),
            check=False,
            timeout=2,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        log.warning("clipboard failed: %s", exc)


def _run(cmd: list[str]) -> None:
    try:
        subprocess.run(
            cmd,
            check=False,
            timeout=10,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        log.warning("paste failed: %s", exc)
