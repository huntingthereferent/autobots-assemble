# A/B Studio · first multitrack DAW construction

Current referent: build a DAW from the existing Meow Lab 2 / audio intake work by observing Suno Studio's published external workflow, not copying its implementation. [DAW interface](../../../docs/live/ab-studio.html) is linked from the existing Workstation. The original cat keyboard and native source handoff remain unchanged.

## Grounded external workflow

Suno Studio 2.0 (August 2026) documents MIDI editing and recording, audio recording, synthesizers, automation, effects, imported material, stem operations and WAV/MIDI export:
- https://help.suno.com/en/articles/13670529
- https://help.suno.com/en/articles/13670977
- https://help.suno.com/en/articles/13671041
- https://help.suno.com/en/articles/13670785
- https://help.suno.com/en/articles/13925249

This project uses independent musical math and Web Audio: seconds per quarter beat = 60 / BPM; equal-tempered frequency = 440 × 2^((MIDI note − 69) / 12); finite MIDI events; explicit note scheduling; playback-rate resampling; and PCM16 WAV encoding. No Suno model, account API, proprietary source, private endpoint, or sound library has been incorporated.

## Functional skeleton (distinct from repository witness/status projections)

| Local category | Implemented in this bounded build | Known wall |
|---|---|---|
| Project | Named JSON session with embedded source bytes; undo/redo history | No autosave or cloud |
| Timeline | Up to 64 beats; move, length edit, split, duplicate, snap, zoom | No cross-track drag or elastic time warp |
| Sources | WAV/MP3 or browser-decodable audio, imported MIDI, microphone permission | No stem separation or AI audio generation |
| Composition | 25-note piano roll, 13-key musical typing, five oscillator/noise instruments | No rich sample-library synthesis |
| Time | BPM 40–240, playback, looping, meter-derived ruler and bar transport | 6/8 modeled as three quarter-note durations per bar; no advanced rhythmic grouping |
| Processing | Track lowpass, drive, delay, gain, pan | No plugins, convolution, sidechain |
| Automation | Linearly interpolated track volume points | No editable graphical curve |
| Mixing | Solo, mute, master gain, live analyser, offline output | No true-peak or LUFS metering |
| A/B | Store/recall project A and B, summary delta, local event log | Comparison is not quality judgment or complete source-level diff |
| Export | PCM16 WAV mix, per-track WAV bounce, format-0 MIDI, project JSON | WAV ≤90 seconds, multiple downloads may be blocked |
| Evidence | Local filename/byte count, SHA-256 where possible, native code and browser tests | Identity hash does not authenticate ownership; no browser action is a native worker execution |

These are sibling functional relations answering one question: which DAW operations compose, move, inspect and deliver audio? They are separate from the repository's category projections for artifact, capability, witness, goal, or read-only view. This is not a definition or universal proof of A/B, also called the language referent.

## Bounds, input trust, and persistence

Browser sources: up to 16 assets, 25 MB per file, decoded duration ≤180 seconds. Project JSON exports cap at 52 MB, open at 55 MB. Imported MIDI parser uses the existing local audio-intake-core.js; initial import retains at most 2,048 note events. The browser performs no network fetch, Suno API access, remote audio upload or automatic localStorage persistence. Project audio data is retained in memory until explicit user export.

Imported audio clips represent duration in beats. If tempo changes, their sample playback rate changes and pitch can change. This is not pitch-preserving warp/time-stretch. A/B snapshots do not copy media bytes, but retain references to loaded assets. Saving the project explicitly embeds the authorized audio data for later reopen.

## Witness plan

Run: python -m unittest -v network.tests.test_ab_studio

Static tests verify linked page categories and JavaScript syntax. The Playwright tests launch Chromium and exercise live Web Audio transport, arrangement editing, A/B states, MIDI export, WAV import, local project persistence and OfflineAudioContext WAV bounce. GitHub workflow ab-studio-browser.yml runs these on pull requests affecting the feature. These tests are proposed until the job actually runs; passing tests would establish only this bounded browser implementation, not generative-model or full DAW parity.

## Next supported movement

Repair time-signature grid semantics; add direct note-duration/velocity editing, audio warp and cross-track operations, better automation curves and independent PCM duration/peak checks. Native workstation execution is a separate explicit handoff: never label browser playback as a source-copied worker run, independently replayed observation or native journal record. Keep ARC/WORLD/NIH lanes separate from this creative audio operation.

Copyright 2026 James Muneoka. All Rights Reserved. Repository license unchanged.
