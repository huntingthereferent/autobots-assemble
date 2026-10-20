# A/B-owned renderer — Godot-informed, NOT Godot-hosted

**This is A/B's own renderer** — an original source adapter and Canvas2D scene
painter, not a Godot project, exported Godot game, embedded engine, or
transplanted `RenderingServer`. It extends the repo's existing
[source-generated SVG motion](../motion/README.md) with direct, interactive
viewing of a selected **native finite source**.

[Open the renderer on the live Pages surface](../../docs/live/ab-renderer.html)
(if the repository's Pages site is enabled).

## Actual Godot source reviewed

Source inspected at [Godot `469659e0617345149cd1eaec2e643d61d130aa6a`](https://github.com/godotengine/godot/tree/469659e0617345149cd1eaec2e643d61d130aa6a)
(MIT): `doc/classes/CanvasItem.xml`,
`doc/classes/RenderingServer.xml` and
`modules/godot_physics_2d/godot_step_2d.cpp`.

The observed architectural separation was useful: a source model emits
representations, while separate drawing resources/servers convert them to
pixels. Redraw can be requested on change instead of recomputing physics from
frames. **No Godot code, artifacts, scene format, runtime, SDK or license was
copied into A/B.** Original A/B code remains A/B-owned and governed by the
repository's existing All Rights Reserved intention.

The earlier [PR #236](https://github.com/huntingthereferent/autobots-assemble/pull/236)
used Godot as the viewer and was intentionally **closed unmerged** because that
mistook source swallowing for adopting another engine.

## Actual implementation

* `views/renderer_native/scene.py` is a source-owned, read-only **scene
  adapter**. It traverses the actual
  `work.arc_like_maze.math.World(3, (0,1,2))`, independently checks **every**
  transition against
  `systems.workspace.ab_relational_cluster._independent_step`, and emits a
  bounded 27-state, 54-directed-transition scene JSON with the original
  Python source's SHA-256 digest. This is one selected mathematical witness;
  no universal A/B law, real physical result or native worker result is
  asserted.
* `docs/live/ab-renderer.js` is a **new original A/B browser renderer**,
  using the browser's primitive Canvas2D drawing surface. It validates every
  state and transition again before drawing anything. It owns its graph
  camera, shapes, layers, edge arrowheads, history, event loop, redraw,
  inspection, interactions and editorial layout, with no external runtime.
* `docs/live/ab-renderer.html` is a minimal self-hosted interaction
  surface. A/B advances only through the recorded A/B edges; Backspace
  navigates **the viewer's own action history** (not a claimed inverse).
  Click inspects a state without teleportation; pan, wheel zoom and fit
  change only the camera. Replay uses a bounded recorded action word.
* `docs/live/ab-renderer-scene.json` is **generated data**, not a second
  definition of the math or a source of newly invented states.

The visible graph layout uses BFS minimum step counts as a presentation
choice. Spacing between rows, pixels, colors, the yellow moving cursor, and
the interpolation between actual endpoint states are not mathematical or
physical measurements. A future renderer scene can preserve a different
source's units and time semantics without imposing F3 on it.

## Reproduce

From the repository root:

```sh
python -m views.renderer_native.scene --check
python -m unittest -v network.tests.test_ab_native_renderer

# Open from a local static web server, not file://
python -m http.server 8000 -d docs
# Then visit http://127.0.0.1:8000/live/ab-renderer.html
```

The dedicated GitHub workflow `.github/workflows/ab-owned-renderer.yml`
installs Chromium for **actual browser interaction**, including source
replay, buttons, keyboard, pan/zoom, and rejection of a deliberately
tampered source transition. It retains a real browser screenshot and JSON
replay receipt.

Neither a browser test nor a screenshot establishes the truth of a model
outside the declared finite state space. They demonstrate fidelity to the
recorded native source and correct implementation of this presentation
lane, with the retained source/replay available for inspection.

## Boundaries

The JavaScript can only read an explicitly generated scene; it cannot
create a native worker, admit a task, promote an edition, run ARC, or modify
WORLD/NIH/W13 or GitHub source. A/B owns and tests the renderer; it does not
inherit Godot's scene tree, physics, or license. More dimensions,
alternative finite models, and observed physical trajectories are separate
scene contracts that must be admitted on their own evidence rather than
invented by expanding the drawings.
