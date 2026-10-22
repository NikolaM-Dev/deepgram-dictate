from __future__ import annotations

import logging
import os
import sys

from pynput import keyboard

from .app import Dictate
from .config import Config, parse_args
from .notify import notify

log = logging.getLogger(__name__)


def main(argv: list[str] | None = None) -> None:
    cfg = parse_args(argv)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stderr,
    )

    if not os.environ.get("DEEPGRAM_API_KEY"):
        log.error(
            "DEEPGRAM_API_KEY is not set. The systemd wrapper sources "
            "%s/config/secrets.zsh; check that file is unlocked.",
            os.environ.get("ZDOTDIR", "~/.config/zsh"),
        )
        notify("No Deepgram API key", "DEEPGRAM_API_KEY is missing", "critical")
        raise SystemExit(78)

    dictate = Dictate(cfg)
    listener = keyboard.GlobalHotKeys({"<f7>": dictate.toggle})
    listener.start()
    log.info(
        "ready: F7 start/stop, press F7 again within %.1fs to cancel "
        "(model=%s, paste=%s, sounds=%s)",
        cfg.cancel_window,
        cfg.model,
        cfg.paste,
        cfg.sounds,
    )

    try:
        listener.join()
    except KeyboardInterrupt:
        log.info("shutting down")
    finally:
        listener.stop()


if __name__ == "__main__":
    main()
