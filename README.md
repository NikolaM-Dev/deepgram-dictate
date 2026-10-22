# deepgram-dictate

Push-to-talk dictation for X11. Press **F7**, speak, press **F7** again. The
transcript is pasted into the focused window.

Uses the Deepgram **pre-recorded** API with Nova-3, then copies the text and
pastes it. Recording stays in memory, so no files are written.

## Keys

| Key | Action |
| --- | --- |
| `F7` | Start recording |
| `F7` | Stop, transcribe, paste |
| `F7` twice fast (< 0.5s) | Cancel and throw the audio away |

## Run

```bash
uv run deepgram-dictate
```

Requires `DEEPGRAM_API_KEY` in the environment.

```bash
uv run deepgram-dictate --paste none          # print only, no pasting
uv run deepgram-dictate --sounds pop          # other feedback theme
uv run deepgram-dictate --language multi      # code-switching (Nova-3)
uv run deepgram-dictate --paste ctrl+shift+v  # terminals (e.g. kitty)
```

| Flag | Env var | Default |
| --- | --- | --- |
| `--model` | `DICTATE_MODEL` | `nova-3` |
| `--language` | `DICTATE_LANGUAGE` | `en` |
| `--paste` | `DICTATE_PASTE` | `ctrl+v` (`ctrl+v`, `ctrl+shift+v`, `type`, `none`) |
| `--sounds` | `DICTATE_SOUNDS` | `marimba` (`marimba`, `pop`, `none`) |
| `--cancel-window` | `DICTATE_CANCEL_WINDOW` | `0.5` |
| `--samplerate` | `DICTATE_SAMPLERATE` | `16000` |

## Autostart

`graphical-session.target` is dead under dwm, so the unit hooks `default.target`:

```bash
mkdir -p ~/.config/systemd/user
cp systemd/deepgram-dictate.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now deepgram-dictate
journalctl --user -fu deepgram-dictate
```

A user unit does not inherit your shell, so `DEEPGRAM_API_KEY` would be missing
there. `ExecStart` is `bin/deepgram-dictate-service`, which sources
`~/.config/zsh/config/secrets.zsh` and then starts the app. No second copy of the
secret to keep in sync. If the key is missing the app exits with code 78 and the
unit does not restart, so it shows as failed instead of looping.

If you prefer systemd to own the variable, replace the `ExecStart` with the
`.venv/bin/deepgram-dictate` binary and add
`EnvironmentFile=%h/.config/deepgram-dictate.env`.

## Notes

- **Handy also owns F7.** In `~/.local/share/com.pais.handy/settings_store.json`
  the `transcribe` binding is `f7`. Change it or quit Handy, otherwise both apps
  record at the same time.
- Only included Speech-to-Text features are requested (`smart_format`, which
  covers punctuation and paragraphs). Paid add-ons (keyterm, redact, summarize,
  topics) are off.
- Notifications are error-only: microphone failure, missing key, Deepgram or
  network failure, and no speech detected. Start, stop, paste and cancel are
  sound-only feedback. Cancel uses the other theme's stop sound, so it is easy to
  tell apart.
- Startup sends 1 second of silence to warm the TLS connection and check the
  key. Delete `_warm_up` in `app.py` if you do not want that.
- The hotkey listens through XRecord, so F7 still reaches the focused app. F7 is
  not bound in most apps, so this is rarely a problem.
- Sounds are copied from [Handy](https://github.com/cjpais/Handy) (MIT).
- System dependencies: `pipewire` (`paplay`), `libnotify`, `xdotool`, `xclip`,
  `portaudio`.

## License

MIT. See [LICENSE](LICENSE).
