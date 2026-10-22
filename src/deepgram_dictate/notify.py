from __future__ import annotations

import subprocess

# Same hint on every notification, so new messages replace the previous one.
_REPLACE_HINT = "string:x-canonical-private-synchronous:deepgram-dictate"


def notify(title: str, body: str = "", urgency: str = "normal") -> None:
    cmd = ["notify-send", "-a", "Deepgram Dictate", "-u", urgency, "-h", _REPLACE_HINT]
    cmd.append(title)
    if body:
        cmd.append(body)
    subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
