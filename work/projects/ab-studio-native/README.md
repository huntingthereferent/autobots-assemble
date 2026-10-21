# Studio swallow — native workstation component before DAW UI

## What "swallow" means here

Recover Suno Studio's publicly documented functional relations, implement independently source-owned math and software for those relations, and compare outputs with a native independent witness. No Suno model, third-party source code, private API, service assets, account access, or generated songs are incorporated.

Sources reviewed: Suno Studio 2.0 public release documentation and clip, MIDI, automation, recording, effects and export guides (August–September 2026):
- https://help.suno.com/en/articles/13670529
- https://help.suno.com/en/articles/13670977
- https://help.suno.com/en/articles/13670785
- https://help.suno.com/en/articles/13674305
- https://help.suno.com/en/articles/13671041
- https://help.suno.com/en/articles/13925249

This is a native **workstation component**, not a new standalone website. ProcessWorkstation source editions are mutable through explicit copying/branching, and worker jobs are executable via HandoffRuntime. The separately named read-only viewer is only a projection of this real system.

## Actual code and chain

- Worker source: systems/workspace/studio_worker_source/studio_worker.py
- Independent host contract, WAV intake, PCM replay and output: systems/workspace/studio_native.py
- Native source edition, handoff, execution, witness and movement: systems/workspace/studio_bridge.py
- Native tests: network/tests/test_studio_workstation.py

Flow:

    local, authorized mono WAV + arrangement manifest
      -> finite validated PCM16 arrays and content SHA-256
      -> ProcessWorkstation.copy_source() -> private source edition/fingerprint
      -> HandoffRuntime.submit() -> recorded READY with exact edition
      -> explicit execute() -> actual copied Python worker in child process
      -> host-owned FRAME-CENTRIC replay independent of worker-source traversal
      -> verified COMPLETE, exact PCM and source fingerprint
      -> WorkspaceStore recorded movement / preserved native job ID
      -> stereo WAV export only after fresh re-verification

The private edition, runtime and workspace journals reside under --data-dir, not a public web page. GitHub Actions can execute the source copies on its runner; that does not start code on the user's offline Windows PC.

## Functional category skeleton (one local sibling axis)

Each child answers: What independent operation does a DAW need?

| Functional relation | Native component v1 | Remaining wall |
|---|---|---|
| Session/project | Finite manifest, source inventory, BPM and 960 ticks/quarter | Long-duration sessions and GUI state |
| Timeline | Tick-to-frame placement of audio and MIDI clips | Live transport, waveform editor, markers |
| Sound sources | Selected user-provided PCM16 mono WAV input | Mic recording and true stem separation |
| Notes/instruments | Bounded MIDI events and sine synthesis | Wavetable synth, MIDI controller |
| Clip movement | Offset, duration, rational playback-rate resampling | Reverse, pitch-preserving time stretch, warp |
| Effects | No effect plugins in v1 | Compression, gate, EQ, delay, reverb, convolution |
| Automation | Linear gain envelopes from sorted time points | Pan and plugin envelopes |
| Mixing | Gain, stereo linear pan, mute, solo, PCM clipping | Subgroups, buses, sidechain, loudness |
| Alternative takes | Independently selected clips and source editions | GUI take comping |
| Generative sound | Not implemented | Independently sourced, permitted model/algorithm |
| A/B observation | Source hashes, independent host output replay | Perceptual comparison and full project differ |
| Output | Verified stereo PCM16 WAV | Long-song bounce, per-track stem bundling |
| Provenance | Explicit source choice and job fingerprints | Authorship or media ownership authentication |

Do not mix these functional categories with completion state, witness depth, artifact type or goal lane. The language referent (historically A/B) is not a DAW component or an algorithm; these finite operations are scoped mathematical representations only.

## Finite render and time contract

- 8–48 kHz source PCM, 40–240 BPM, 960 ticks per quarter beat.
- Maximum 12,000 stereo frames of output. This is a deliberately small **real** native render that can be independently replayed in bounded time; it is not a full-length DAW.
- Maximum 4 sources with up to 8,192 mono PCM16 samples each, 8 tracks, 16 clips per track, 64 notes per MIDI clip and 32 automation points per track.
- Audio samples are moved at rational playback rates from 1/4 to 4; signed nearest-integer interpolation is recorded. This changes pitch. No transparent time-warp claim.
- MIDI is a single finite sine oscillator per note with equal temperament; no Suno model or voice is involved.
- Stereo PCM16 output identity is SHA-256 over interleaved signed little-endian samples. Source identity is SHA-256 over source PCM samples, not proof of ownership.

The ordinary local manifest uses schema ab-studio-wav-intake/v1 and exact keys: schema, sample_rate, bpm, duration_ticks, sources, tracks. Each source has an id and path to selected mono PCM16 WAV with matching sample rate. Each track has id, gain (0–1500), pan (-1000–1000), mute, solo, automation (tick/gain), clips. Audio clip: kind, id, source, start, length, offset, rate_num, rate_den. MIDI clip: kind, id, start, length, notes, each note pitch, start, length, velocity. Timing is integer ticks.

Run from the repository root:

    python -m systems.workspace.studio_bridge --manifest /path/to/studio-session.json --data-dir runtime/data --version studio-first-001 --copy-source --execute --out /path/to/mix.wav

Existing edition names cannot be overwritten. Copy and execute require two explicit flags.

Test with:

    python -m unittest -v network.tests.test_studio_workstation

Tests include the actual copied worker in a child Python process, host-owned replay, explicit READY/execute, export/readback of WAV, journal restart, digest falsification, worker source mutation and malformed inputs.

## Next movement

Only after the native component is verified: extend processing and state relationships, then have the earlier DAW UI candidate export a valid native input and invoke this explicit workstation component. Browser events alone do not certify native execution. Keep the browser candidate as a separate draft.

Copyright 2026 James Muneoka. All Rights Reserved. Repository license unchanged.
