from __future__ import annotations

import io
import wave

import numpy as np
import sounddevice as sd


def silent_wav(seconds: float, samplerate: int = 16000) -> bytes:
    """Small silent WAV used to warm up the client and check the API key."""
    samples = np.zeros(int(seconds * samplerate), dtype=np.int16)
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(samplerate)
        wav.writeframes(samples.tobytes())
    return buffer.getvalue()


class Recorder:
    """Records the default input into memory and returns WAV bytes."""

    def __init__(self, samplerate: int = 16000, channels: int = 1) -> None:
        self.samplerate = samplerate
        self.channels = channels
        self._chunks: list[np.ndarray] = []
        self._stream: sd.InputStream | None = None

    def start(self) -> None:
        self._chunks = []
        self._stream = sd.InputStream(
            samplerate=self.samplerate,
            channels=self.channels,
            dtype="int16",
            blocksize=0,
            callback=self._on_audio,
        )
        self._stream.start()

    def _on_audio(self, indata, frames, time, status) -> None:
        self._chunks.append(indata.copy())

    def stop(self) -> bytes:
        self._close()
        if self._chunks:
            samples = np.concatenate(self._chunks)
        else:
            samples = np.zeros((0, self.channels), dtype=np.int16)
        self._chunks = []

        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wav:
            wav.setnchannels(self.channels)
            wav.setsampwidth(2)
            wav.setframerate(self.samplerate)
            wav.writeframes(samples.tobytes())
        return buffer.getvalue()

    def discard(self) -> None:
        self._close()
        self._chunks = []

    def _close(self) -> None:
        stream, self._stream = self._stream, None
        if stream is None:
            return
        stream.stop()
        stream.close()
