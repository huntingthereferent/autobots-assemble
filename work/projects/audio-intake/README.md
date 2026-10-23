# Audio Intake — independent workstation production desk

The [Audio Intake page](../../../docs/live/audio-intake.html) accepts authorized local WAV/MP3 and MIDI files. It does not connect to accounts, transfer user audio to a server, access proprietary models or imply that a file's origin or rights are authenticated. Users remain responsible for choosing material they can lawfully use.

## Source-first browser operations

- Locally decode WAV/MP3 using browser-supported codecs; parse MIDI formats 0 and 1 with finite timing and event bounds.
- Up to 12 inputs per session, 50 MB each, audio up to 10 minutes, MIDI up to 5 MB, 64 tracks and 100,000 events.
- Measure waveform, RMS, peak, sample rate and duration; retain name, bytes and content SHA-256 when Web Crypto is available in a secure context. A hash is a content identity, not proof of ownership.
- Drag or enter an excerpt range, use a manually chosen/tapped BPM for a bar ruler, audition at an adjustable playback rate, loop and stop, play a sampled 13-note keyboard and export an unmodified-source-derived PCM16 WAV clip up to 45 seconds.
- Save named source-matched bookmarks with production notes; independently audition, export, revise or remove them. A portable session JSON keeps bookmarks, source fingerprints and creative directions but never audio bytes. Restored bookmarks require reimporting the matching source to play.
- Export a source manifest recording observed fields and any source-preserving transform. No transcription, stem separation, tempo/key detection or music generation is claimed.

## Manual production and A/B decisions

The direction desk allows editable style, mood, groove, texture, vocal intent, energy, density and a sequenced arrangement of up to 18 sections. Four starting points are editable suggestions, not detected musical structure. The planning ruler assumes 4/4 at the user-set BPM.

Users can export a plain-language production brief or its JSON, capture directions A and B, compare changes and restore either draft. Local decisions are not mathematical evidence about the imported audio.

## Native source worker

A separate explicitly invoked native workstation lane accepts finite PCM16 mono WAV input, up to the first 8192 frames, and performs limited playback-rate pitch motion (±12 semitones) and optional reversal. It copies and fingerprints its source, executes an isolated reviewed worker, independently replays resulting PCM samples and journals accepted movements. It is not a DAW or generative composition engine.

Relevant modules:

- `systems/workspace/audio_motion_worker_source/motion_worker.py`
- `systems/workspace/audio_motion_native.py`
- `systems/workspace/audio_motion_bridge.py`
- `systems/workspace/audio_sound_bank.py`
- `docs/live/audio-intake-core.js`

A local opt-in example:

```sh
python -m systems.workspace.audio_motion_bridge \
  --data-dir runtime/data --source-wav /path/to/short-source.wav \
  --version audio-v1 --root-note 60 --note 67 \
  --copy-source --execute --out /path/to/moved-source.wav
```

Browser source measurements and native journal verification are separate and must not be conflated.

## Verification

```sh
python -m unittest -v network.tests.test_audio_export_intake network.tests.test_audio_motion_workstation network.tests.test_audio_sound_bank
python -m unittest -v network.tests.test_audio_intake_browser network.tests.test_audio_intake_session
```

The browser tests require Playwright/Chromium; mathematical source tests use Node.js. The scheduled CI workflow is `.github/workflows/audio-intake-browser.yml`.

Copyright 2026 James Muneoka. All Rights Reserved.
