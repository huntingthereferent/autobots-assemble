# Meow Lab 2 · Swallow Sounds cat keyboard

[Open the keyboard](../../../docs/live/cat-keyboard.html) · [Workstation](../../../docs/live/work.html)

This is a new 13-key cat instrument built *around source movement*. It is not the original purple Meow Machine page rebranded. It has a new dark research/audio look, an actual four-slot audio bank, waveform display, local sound imports, four mathematically synthesized cat sources, and playable sample repitching for the keyboard, recorder and 16-step sequencer. Everything in the public browser runs locally without account credentials or hidden network endpoints.

## Two distinct ways to swallow a sound

**Browser, immediately:** select a slot, choose an authorized local audio file, choose an offset and press Swallow Into Slot. The browser decodes the file, makes a bounded 2.6-second mono sample and maps it across the 13 keys. It displays the source filename and SHA-256 when available. This is a source observation, not a verified native worker. Press Export PCM16 WAV + Manifest to download an 8192-frame/16kHz mono source plus input receipt. If your browser blocks one of the two downloads, permit local downloads or try again.

**Actual native workstation:** run the exported WAV through the existing copy/admit/execute/host-replay/record pipeline, or batch-ingest four PCM16 WAV files named by slot. The standalone browser never executes private Python code and never falsely calls a DOM click a native PASS.

```sh
python -m systems.workspace.audio_sound_bank \
  --data-dir runtime/data \
  --source-dir /path/to/my/cat-wavs \
  --output-dir /path/to/my/verified-sounds \
  --version meow-sounds-v1 --semitones 5 \
  --copy-source --execute
```

The source directory must contain between one and four of `miso.wav`, `mochi.wav`, `nori.wav`, `bean.wav`. Native audio accepts ordinary non-symlink 16-bit mono WAV files with a sample rate from 8–96kHz and at least 128 frames; it moves at most 8192 source frames per file. **The bounded output can be imported back into Meow Lab 2**. Use a new version name when doing a new edition copy. The output includes native-reverified PCM WAVs, per-slot SHA-256 records, exact job IDs, and `sound-bank-manifest.json`. The native runner is invoked explicitly; it does not host a service.

## Verification

- `python -m unittest -v network.tests.test_audio_motion_workstation network.tests.test_audio_sound_bank network.tests.test_suno_export_intake network.tests.test_cat_keyboard_ui`
- `python -m unittest -v network.tests.test_meow_lab_browser` (with Playwright/Chromium installed).
- GitHub Actions `audio-motion-native` exercises actual local source editions and host replay; `meow-lab-v2-browser` exercises WAV import, waveform, keyboard, downloads and mobile layout.

This does not contain Suno software, generated Suno audio, model weights, or proprietary secrets. Generated browser cat sources are our own finite procedural sound buffers. Importing a Suno export does not imply rights to redistribute or commercialize it. Neither imported audio nor a local manifest alone is authenticated independent proof of source ownership.

Copyright 2026 James Muneoka. All Rights Reserved. See repository LICENSE.
