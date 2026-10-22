from __future__ import annotations

import logging
import threading
import time

from . import sounds
from .audio import Recorder, silent_wav
from .config import Config
from .notify import notify
from .output import deliver
from .transcribe import transcribe

log = logging.getLogger(__name__)

# A kept-alive socket dies server-side after a minute or two of idle, so warm
# again only when the previous request is older than this.
WARM_INTERVAL = 30.0


class Dictate:
    """F7 toggles recording. A fast second press cancels and discards the audio."""

    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self.recorder = Recorder(cfg.samplerate)
        self._lock = threading.Lock()
        self._recording = False
        self._started_at = 0.0
        self._last_api_use = 0.0

    def _warm_in_background(self) -> None:
        """Pay the handshake while the user is still speaking."""
        if time.monotonic() - self._last_api_use < WARM_INTERVAL:
            return
        # Mark it now so a second fast press does not spawn a second warm-up.
        self._last_api_use = time.monotonic()
        threading.Thread(target=self._ping, daemon=True).start()

    def _ping(self) -> None:
        """Send a short silent clip so the next real request reuses the socket."""
        try:
            transcribe(silent_wav(0.5, self.cfg.samplerate), self.cfg)
        except Exception as exc:  # noqa: BLE001 - the real request reports failures
            log.debug("key-down warm-up failed: %s", exc)

    def toggle(self) -> None:
        with self._lock:
            if self._recording:
                elapsed = time.monotonic() - self._started_at
                self._stop(elapsed)
            else:
                self._start()

    def _start(self) -> None:
        try:
            self.recorder.start()
        except Exception as exc:  # noqa: BLE001 - surface mic problems to the user
            log.exception("microphone failed")
            notify("Microphone error", str(exc), "critical")
            return
        self._recording = True
        self._started_at = time.monotonic()
        sounds.play("start", self.cfg.sounds)
        self._warm_in_background()
        log.info("recording")

    def _stop(self, elapsed: float) -> None:
        self._recording = False
        if elapsed < max(self.cfg.cancel_window, self.cfg.min_seconds):
            self.recorder.discard()
            sounds.play("cancel", self.cfg.sounds)
            log.info("quick cancel after %.2fs", elapsed)
            return

        wav = self.recorder.stop()
        sounds.play("stop", self.cfg.sounds)
        log.info("stopped after %.2fs, %d bytes", elapsed, len(wav))
        threading.Thread(target=self._transcribe, args=(wav,), daemon=True).start()

    def _transcribe(self, wav: bytes) -> None:
        started = time.monotonic()
        self._last_api_use = started
        try:
            text = transcribe(wav, self.cfg)
        except Exception as exc:  # noqa: BLE001 - network/auth errors
            log.exception("transcription failed")
            notify("Transcription failed", str(exc)[:200], "critical")
            return

        took = time.monotonic() - started
        if not text:
            log.info("no speech detected (%.2fs)", took)
            notify("No speech detected", "Nothing was transcribed")
            return

        deliver(text, self.cfg)
        log.info("transcribed in %.2fs", took)
