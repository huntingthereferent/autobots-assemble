# Meow Machine — workstation side project

A self-contained, offline instrument that lives at [`docs/live/cat-keyboard.html`](../../../docs/live/cat-keyboard.html) and is linked from the public workstation. Its synthesized cat voices are original Web Audio tone designs, not sampled recordings or realistic animal vocalizations. No build system, remote assets, telemetry, account, or private journal access is required.

- 13 chromatic keys (C through C), physical A W S E D F T G Y H U J K shortcuts, multi-touch, drag-to-play, and accessible clickable buttons
- Miso, Mochi, Nori, Bean voice synthesis; independent timbres across musical octaves; echo, purr, octave selection, and volume
- Performance recorder with replay, two-minute / 2,000-event limit, validated `meow-machine/score-v1` JSON export and import
- 16-step, five-note loop editor with tempo, three pattern presets, and per-step playback
- Responsive design, reduced-motion support, no user data sent to any server

This is an independent creative project, **not** an ARC, WORLD, NIH or A/B research result. Workstation navigation is only a link; playing notes does not create workflow or research execution evidence.

## Verification

```sh
python -m unittest -v network.tests.test_cat_keyboard_ui
```

Browser checks should additionally exercise keyboard, multi-touch, recording and replay, presets, and mobile sizing. Sound requires a browser that supports Web Audio and a user gesture to unlock the audio context. JSON saves scores rather than recording audio.

Copyright (c) 2026 James Muneoka. All rights reserved. See the repository `LICENSE`; this addition includes no third-party code or audio assets.