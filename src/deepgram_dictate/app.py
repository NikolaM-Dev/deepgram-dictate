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


class Dictate:
    """F7 toggles recording. A fast second press cancels and discards the audio."""

    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self.recorder = Recorder(cfg.samplerate)
        self._lock = threading.Lock()
        self._recording = False
        self._started_at = 0.0
        threading.Thread(target=self._warm_up, daemon=True).start()

    def _warm_up(self) -> None:
        """Open the TLS connection and check the key before the first dictation."""
        started = time.monotonic()
        try:
            transcribe(silent_wav(1.0, self.cfg.samplerate), self.cfg)
        except Exception as exc:  # noqa: BLE001 - auth or network problem at startup
            log.exception("warm-up failed")
            notify("Deepgram not ready", str(exc)[:200], "critical")
            return
        log.info("deepgram ready in %.2fs", time.monotonic() - started)

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
