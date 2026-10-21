# Source-first construction note — Meow Machine

- **Referent:** a playable cat keyboard, not a depiction or decorative page.
- **Scope:** self-contained HTML/CSS/Web Audio with independent bounded score validation.
- **Entrypoint:** `docs/live/cat-keyboard.html` linked from `docs/live/work.html`.
- **Source data:** 13 chromatic note mappings, four deterministic voice profiles, finite 16-step grid.
- **Outputs:** synthesized live sound, local note-score playback, validated JSON interchange.
- **Boundaries:** no claims about native workstation worker execution; no remote services, private journals, microphone capture, or publication of user-made scores.
- **Native checks:** Python tests and Node syntax/pure-score validation; Chromium desktop and mobile interaction checks done locally before proposal. Browser sound perception is not independently verified in a listening test.
- **Next:** human playback/volume feedback and a final deployed GitHub Pages browser check after review/merge.