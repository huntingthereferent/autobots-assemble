# A/B finite motion — Godot source swallow

This is an **interactive Godot 4.7 viewer** for **one explicitly selected native finite A/B example**. It is *not* a replacement definition of A/B, a physical simulation, the 48-anchor working hypothesis, or the WORLD collision engine.

## Source provenance

External source **inspected and selectively regrounded**:
- [Godot Engine, commit `469659e0617345149cd1eaec2e643d61d130aa6a`](https://github.com/godotengine/godot/tree/469659e0617345149cd1eaec2e643d61d130aa6a) (MIT), especially `doc/classes/CanvasItem.xml` (a drawing-only scene element that redraws on demand), `doc/classes/RenderingServer.xml` (visual scene/canvas backends), and `modules/godot_physics_2d/godot_step_2d.cpp` (separate physics simulation path).

Original A/B source of all discrete model behavior:
- [`work/arc_like_maze/math.py`](../../work/arc_like_maze/math.py) `World(3, (0,1,2))`. That model's 27 reachable states and both possible `A`/`B` edges per state (54 source-derived transitions) are the only displayed mathematical facts.

**Actual swallow:** Godot's drawing/layer separation, event-driven redraw, user input and headless scene verification. Not its built-in physics, scene-world ontology, collision response, experimental simulation results, or source code. The scene and exporter are independently authored and contain **no copied Godot source**. Original A/B All Rights Reserved licensing remains; MIT notices stay attached to Godot's own separately installed binary/source under their original terms. Any future redistribution of the engine must follow Godot's license requirements.

## What runs

```bash
python -m views.godot_ab.export_finite --check
python -m unittest -v network.tests.test_godot_native_finite
godot --path views/godot_ab
```

Or open `views/godot_ab/project.godot` in Godot 4.7.2. Godot remains an external, separately downloaded **MIT-licensed runtime**; Python and the existing native repo remain the owners of their research records.

- `A` and `B`: follow the exact recorded transition out of the current state.
- `Backspace`: travel **back through the UI's recorded action history**. This is not a mathematical inverse assertion.
- `R`: reset to the admitted finite origin.
- `P`: replay the committed bounded `ABAABBABA` sequence.
- Click a node: inspect its label only, **not** teleport to an unwitnessed state.

The viewer arranges states by **source-computed minimum number of steps from origin**. Vertical ordering, edges as straight lines, colors, positions, and moving yellow markers are **presentation choices**. The yellow marker interpolates through pixels to illustrate one discrete edge; intermediate pixel positions are **not states in the native finite model**. A visible return to a state does not prove a physical orbit.

Godot recomputes the declared A/B transformation table and BFS distances before allowing any rendering. It rejects malformed or invented native edges, bad sample sequences, missing states, and incorrect model/source labels.

## Testing / status

The workflow [`godot-native-finite-view.yml`](../../.github/workflows/godot-native-finite-view.yml) first independently replays the native Python source and verifies a byte-for-byte generated JSON dataset. It then downloads official [Godot 4.7.2 stable](https://github.com/godotengine/godot-builds/releases/tag/4.7.2-stable) and verifies the SHA-256 digest reported for that release asset:

`cadd3204e728a35d3f13adb7fd0d7902636b79f6b95c40c265eb73b6c35329e4`

Only then does it import and instantiate the actual Godot scene **headlessly**. A CI pass supports syntax/scene loading/data validation; it does **not** yet prove screenshot fidelity, input hardware compatibility, user-facing visual quality, physical causality, or production readiness.

**No native worker is admitted or executed** by the Godot scene. `WORLD`, W13, NIH, ARC, and the workstation keep their distinct original source/runtime boundaries. Future lanes (larger finite models, recorded worker movement, WORLD physical source) require their own schemas and verification, not extending this one by assuming everything is an `F_3^3` state.
