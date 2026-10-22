# Pony Trail — horse riding browser game

[Play source](../../../docs/live/pony-trail.html) · [Workstation](../../../docs/live/work.html)

## Purpose
An original, kid-friendly horseback jumping game made for the Workstation. It is a **standalone browser play activity**, not an A/B experiment, research result, native task, or worker.

## The trail is the feature
Switch the trail **during a ride** without interrupting controls, score or progress. Each choice changes the whole scene, not merely the color of the sky:

| Trail | Visual character | Passing details |
| --- | --- | --- |
| Wildflower Meadow | bright sky, orchard foliage, grassy ridges, flowering verges | birds, butterflies and windblown petals |
| Golden Hour Ridge | low sun, amber haze, warm trees and grasses | warm leaves drifting past |
| Moonlit Woods | stars, crescent moon, cool pines and dark trail | softly glowing fireflies |

The old single-layer scenery has been replaced with **speed-linked parallax**: clouds and distant hills move slowly; tree rows move at different speeds; the trail edge, flowers and stones move fastest. The motion is tied to the same travel speed used by the obstacle system, including the Left/Right pace controls. Trail changes crossfade rather than resetting the ride. Drawing and animation are authored in HTML Canvas and JavaScript, with no imported sprites.

## What else is playable
- Three selectable ponies: Cocoa, Blossom, Moonbeam, with distinct coats and saddle accents.
- Automatic scrolling ride, fences and puddles to jump, carrots and golden horseshoes to gather.
- Three hearts, distance, best record saved **only locally in the browser**, start/pause/restart and optional synthesized audio.
- Space or Up to jump, Left/Right to change pace, P to pause, R to restart; the Jump button works by touch.
- A compact retro-storybook interface with clear trail selector and scene name.

## Visual provenance and design boundaries
Reference material was reviewed for **visual structure and depth**, not copied into this project:

1. [The Mane Quest — horse-game roundup (June 2024)](https://www.themanequest.com/blog/2024/6/7/game-announcement-roundup-here-are-6-new-and-upcoming-horse-games-to-have-a-look-at): horse-game readability, framing and the appeal of illustrated 2D worlds.
2. [Kingdom: Classic, Steam community screenshots](https://steamcommunity.com/app/368230/screenshots/): depth from overlapping silhouettes, simple environment bands and a small rider against a larger landscape.
3. [Pixelnest Studio — Parallax scrolling (2013)](https://pixelnest.io/tutorials/2d-game-unity/parallax-scrolling/): technique reference for differential motion across scene layers.

These are **references only**, not asset sources, collaborator credits or claims of affiliation. No screenshots, copyrighted characters, image files or third-party scripts are shipped or loaded. All game illustration remains original procedural Canvas geometry.

## Run and review
Open `docs/live/pony-trail.html` in a browser, including offline from a saved HTML file. It is linked from the Workstation header. Manually check all three trails at rest and while running, pace change, foreground flybys, jumping, pause, restart, sound and mobile controls. Source-level regression checks live in `network/tests/test_pony_trail_ui.py`; those checks do **not** substitute for interactive browser playtesting.

## Boundary and safety
Pony Trail does not run workstation Python, write a native journal, access research records or claim research/Actions results. Local best distance is a game preference, not research evidence. Graphics are stylized drawings, not real riding instructions. No account, analytics, chat, network request or upload is made by the game.

Copyright 2026 James Muneoka. All Rights Reserved. See repository LICENSE.
