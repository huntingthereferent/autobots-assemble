# Suno export intake — an independent A/B workstation audio lane

This lane is an *intake of user-provided musical material*, **not a copy of Suno**. Suno is a third-party proprietary music service. No Suno code, trained weights, private endpoints, media libraries, credentials, generated sounds, or protected assets are incorporated into the repository.

## Official input contract checked October 20, 2026

- Suno Help Center documents WAV/MP3 downloads, downloadable stems, and MIDI exports for eligible Suno Studio projects. Feature access and export quotas vary by subscription, and may change.
- Source pages: <https://help.suno.com/en/articles/13926081>, <https://help.suno.com/en/articles/13925249>, <https://help.suno.com/en/articles/13925185>, <https://help.suno.com/en/articles/13670529>.
- Terms and restrictions: <https://suno.com/terms>. Users must be entitled to use any files they select. Importing a file does not grant ownership or commercial rights. Suno's terms restrict copying/service-content use and some competing uses.
- No Suno developer API, authorization, or account access is asserted by this implementation. This is not an official Suno integration.

## Native construction

- [Workstation intake](../../../docs/live/suno-intake.html) — operates on local files; no upload, account, backend storage, sync, or network request.
- [Math/source module](../../../docs/live/audio-intake-core.js) — calculate RMS/peak waveform envelopes, perform bounded PCM16 WAV slicing, pitch by playback-rate ratio, parse standard MIDI format 0/1 with tick-to-ms tempo mapping.
- File source: name, byte size, SHA-256 where WebCrypto is available in a secure context, and decoded measurements. Hashes establish *content identity*, not authorship or rights.
- WAV and MP3 files are decoded by the local browser; compressed format support depends on that browser. Input bounds: 12 files/session, 50MB/file, 10-minute audio maximum, 5MB MIDI maximum, 64 MIDI tracks, 100,000 events.
- A user-selected range can be heard, pitch-resampled, exported as a maximum 45-second WAV, or documented as a JSON manifest that explicitly identifies manual settings and claims. JSON does not contain the music.
- Input MIDI is parsed for notes and tempo events, and MIDI note observations can be exported as JSON. This is not audio-to-MIDI or stem separation.

## Browser direction desk (October 22, 2026)

The Audio Intake page now has a separate **manual creative-direction desk**, alongside the existing source-measurement controls.

- Four editable production starting points (Drive, Float, Cut, Lift); style, mood, groove, texture, vocal direction, energy, and density are user choices.
- An ordered arrangement builder supports repeat sections, bar-length changes, section movement, and up to 18 sections.
- The bar ruler uses a **manual or tapped BPM** and an explicitly assumed 4/4 meter. Four- and eight-bar buttons convert that *planning choice* into a seconds-based local WAV slice, capped by the existing 45-second export limit and available source length. It is not automatic BPM analysis.
- The waveform can be dragged to choose source times, in addition to the accessible numeric controls.
- The live brief can be copied as text or saved as `ab-audio-direction/v1` JSON. Its source file name, SHA-256 (where available), and selected time range are identity/observation references, not proof of rights or automatic musical inference.
- The independent `ab-audio-intake/v1` source manifest is preserved; creative instructions remain distinctly labeled. No network calls, account authorization, third-party APIs, persistent browser storage, generative service, or automatic exports are added. Links to Suno and Meow Lab 2 are navigation, not integrations.

## Native workstation movement (source-owned)

The browser page is only the **intake and preview**. The actual workstation motion path is now:

```text
WAV from an authorized source
  -> PCM16 mono frames (max 8192) with full-file source hash
  -> ProcessWorkstation.copy_source() [private, source-fingerprinted edition]
  -> AudioMotionBridge.admit() [existing RuntimeJournal, READY handoff]
  -> explicitly invoked copied worker in isolated Python process
  -> independent host-owned sample-by-sample native replay
  -> verified COMPLETE -> WorkspaceStore.record_movement()
  -> reverified WAV output + source/result hashes
```

Code: `systems/workspace/audio_motion_worker_source/motion_worker.py`, `audio_motion_native.py`, and `audio_motion_bridge.py`. The worker implements finite playback-rate pitch movement (±12 semitones) with optional time reversal. The host independently computes and compares every resulting PCM sample; recording a movement requires fresh re-verification. An edited source edition or fabricated output blocks verification. A restart can reload the exact runtime journal and evidence. All file processing is local and explicitly invoked, **not** a browser-side simulated worker or a copy of Suno's model.

Run from the repository root, with a local 16-bit **mono uncompressed WAV** (8–96kHz):

```sh
python -m systems.workspace.audio_motion_bridge \
  --data-dir runtime/data --source-wav /path/to/short-meow.wav \
  --version audio-v1 --root-note 60 --note 67 \
  --copy-source --execute --out /path/to/moved-meow.wav
python -m unittest -v network.tests.test_audio_motion_workstation
```

The example is an opt-in action. `--copy-source` and `--execute` are required; it never reads the user’s Suno account, launches autonomous tasks, or moves unrelated research lanes. Audio beyond the first 8192 frames stays out of this bounded pass and is not falsely counted as processed. Browser WAV/MP3 playback and MIDI inspection remain separate capabilities; the native source worker currently accepts only finite PCM16 mono WAV. It is one operation toward a musical workstation, **not** a full replacement for generative composition.

## Next interface (not yet implemented)

Add explicit sample-import support to the existing **Meow Machine** cat keyboard, keyed to exported PCM16 clips and their associated source manifests. Do not couple this lane to ARC, WORLD, NIH or workstation execution evidence. The cat keyboard is in PR #325 as of construction; this lane can be reviewed independently.

## Tests

Run `python -m unittest -v network.tests.test_suno_export_intake` and the existing workstation tests. Native Node regression covers MIDI timing, waveform measurements, PCM16 lengths and invalid data rejection. Browser interactions should be exercised with user-selected test fixture WAV/MIDI before release. Preserve failed or unsupported cases as boundaries rather than asserting Suno generation has been reconstructed.