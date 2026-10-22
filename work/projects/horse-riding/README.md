# Pony Trail — horse riding game

[Play source](../../../docs/live/pony-trail.html) · [Workstation](../../../docs/live/work.html)

## Purpose
A small original, kid-friendly horse riding and jumping game requested for the workstation. It is a **standalone browser play activity**, not an A/B experiment, research result, native task, or worker.

## What is implemented
- Three selectable ponies: Cocoa, Blossom and Moonbeam; three scenic trails: meadow, sunset and moonlight.
- Automatic scrolling ride with jumping fences and puddles, collecting carrots and jumping for golden horseshoes.
- Three hearts, a distance tracker, a record stored *only in the local browser*, start/pause/restart and sound toggle.
- Space or Up to jump; Left / Right to change the pace; P to pause; R to restart. The Jump button supports mouse or touch.
- Fully original Canvas drawings and synthesized sounds. No external assets, analytics, chat, network requests, accounts or uploads.

## Run it
Open `docs/live/pony-trail.html` in a browser. It also appears in `docs/live/work.html` navigation after the branch is merged and the Pages site updates. You can save that single HTML file to play offline.

## Boundary and safety
The game does not run workstation Python, write to the native journal, access research records, or claim GitHub Actions successes. Browser best distance is a convenience preference, not a measured research datum. Graphics are stylized drawings, not real riding instructions. No connections are opened by the game.

## Review
Check that Start, Jump, Pause, restart and all selectors work. A basic source-level regression test is in `network/tests/test_pony_trail_ui.py`; interactive behavior still requires browser testing. The project is isolated from research code.

Copyright 2026 James Muneoka. All Rights Reserved. See repository LICENSE.
