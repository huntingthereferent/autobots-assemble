"""Predeclared A/B native geometry frontier with two independent histories.

All previously recorded glyph-position/action edges are independently sourced.
Every unknown edge reachable through them is tested twice: shortest known
prefix and a three-roundtrip delayed prefix. The predictions are frozen before
official native LS20 execution, including collision and mixed-terrain cases.
No REA, simulated ARC, hidden-state inference, or F3 identification.
"""
from __future__ import annotations
import argparse
from collections import deque, Counter
from hashlib import sha256
import json
from pathlib import Path
import numpy as np
from .native_geometry_unknown_edge import source_material, predict
from .native_geometry_unknown_edge_verify import position
from .native_observation_bridge import frame_summary

PROTOCOL = "AB_LS20_COMPLETE_REACHABLE_UNKNOWN_FRONTIER_V1"
OLD_SOURCE_SHA256 = {
    "frozen-18-edges.json": "1dea0084a3cf56263c4986b17d715d146278b20f05511ff49a6a7c3bfbe2631c",
    "native-18-edges.json": "ad02f8dc4d96d61e164361430c22e02a5ba3a3de80de4cb2c4d740a169373f59",
    "native-18-edges.npz": "efc7f798dee3797c36bd5dc1d24c705c621e4ebe53470af1cd23d0ae77359a2d",
    "independent-verdict.json": "16c9346a0b5fa64706c8e13912ff5163cb6ea0fc993dae4a8f2dae309b5c292c",
}
ROOT = (45, 34)
ACTIONS = "1234"
DETOUR = "121212"  # Each of three 1->2 roundtrips was already observed.

def load_source(old: Path, last: Path):
    previous, terrain, original = source_material(old)
    for name, expected in OLD_SOURCE_SHA256.items():
        if sha256((last / name).read_bytes()).hexdigest() != expected:
            raise ValueError("previous independent native raw evidence changed: " + name)
    frozen = json.loads((last / "frozen-18-edges.json").read_text())
    native = json.loads((last / "native-18-edges.json").read_text())
    verdict = json.loads((last / "independent-verdict.json").read_text())
    if (frozen.get("kind") != "NATIVE_AB_GEOMETRY_SOURCE_FROZEN" or
        native.get("kind") != "AB_LS20_UNKNOWN_GEOMETRY_RAW_FRAMES_V1" or
        native.get("game") != "ls20" or
        verdict.get("all_unknown_edge_predictions_passed") is not True or
        verdict.get("exact_unknown_edge_predictions") != 18 or
        len(frozen.get("unseen_holdout_edge_predictions", [])) != 18 or
        len(native.get("trajectories", [])) != 18):
        raise ValueError("independent first geometry test was not verified")
    edges = {}
    for record in previous["partial_model"]:
        key = (tuple(record["glyph"]), record["action"])
        if key in edges:
            raise ValueError("duplicate original training edge")
        edges[key] = tuple(record["next_glyph"])
        if predict(terrain, key[0], key[1]) != edges[key]:
            raise ValueError("original known edge contradicts frozen source geometry")
    if len(edges) != 27:
        raise ValueError("incomplete original native glyph edge table")
    with np.load(last / "native-18-edges.npz", allow_pickle=False) as pixels:
        if set(pixels.files) != set(native["words"]):
            raise ValueError("incomplete original 18 native frames")
        roots = set()
        for expected, record in zip(frozen["unseen_holdout_edge_predictions"],
                                     native["trajectories"]):
            word = expected["word"]
            if (record.get("word") != word or record.get("completed") is not True or
                record.get("interruption") is not None or
                record.get("steps") != len(word) or
                len(record.get("states", [])) != len(word)+1):
                raise ValueError("previous independent native trajectory incomplete")
            frames = pixels[word]
            if frames.shape != (len(word)+1, 64, 64) or frames.dtype != np.uint8:
                raise ValueError("prior independent raw array invalid")
            observations = []
            for depth, frame in enumerate(frames):
                state = record["states"][depth]
                if (state.get("index") != depth or
                    state.get("action") != (None if depth == 0 else int(word[depth-1])) or
                    state.get("observation") != frame_summary(frame)):
                    raise ValueError("prior native step fails independent pixel replay")
                observations.append(list(position(frame)))
            roots.add(record["states"][0]["observation"]["whole"])
            if (observations[:-1] != expected["known_prefix_positions"] or
                observations[-1] != expected["predicted_next_position"]):
                raise ValueError("new original 18 source edge not independently reproduced")
            key = (tuple(observations[-2]), word[-1])
            if key in edges:
                raise ValueError("originally unobserved edge is duplicated in prior source")
            edges[key] = tuple(observations[-1])
            if predict(terrain, key[0], key[1]) != edges[key]:
                raise ValueError("first independent holdout contradicted original geometry")
        if len(roots) != 1:
            raise ValueError("original 18 resets do not share a native root")
    if len(edges) != 45 or edges.get((ROOT, "1")) != (40, 34) or \
       edges.get(((40, 34), "2")) != ROOT:
        raise ValueError("observed edge graph or proven detour differs")
    return terrain, edges, next(iter(roots))

def prefix_positions(edges, word):
    state = ROOT
    positions = [list(state)]
    for action in word:
        key = (state, action)
        if key not in edges:
            raise ValueError("candidate known prefix contains an unobserved edge")
        state = edges[key]
        positions.append(list(state))
    return positions

def freeze(old: Path, last: Path) -> dict:
    terrain, edges, source_root = load_source(old, last)
    paths = {ROOT: ""}
    q = deque([ROOT])
    while q:
        at = q.popleft()
        for action in ACTIONS:
            dest = edges.get((at, action))
            if dest is not None and dest not in paths:
                paths[dest] = paths[at] + action
                q.append(dest)
    if len(paths) != 21:
        raise ValueError("the source-reachable observed graph changed")
    trials = []
    pair_ids = set()
    moved = blocked = 0
    terrain_kinds = Counter()
    for at, known_path in paths.items():
        for action in ACTIONS:
            if (at, action) in edges:
                continue
            pair_id = str(at[0]) + "," + str(at[1]) + "/" + action
            if pair_id in pair_ids:
                raise ValueError("duplicate observed frontier identity")
            pair_ids.add(pair_id)
            expected = predict(terrain, at, action)
            if expected == at: blocked += 1
            else: moved += 1
            dy, dx = {"1":(-5,0), "2":(5,0), "3":(0,-5), "4":(0,5)}[action]
            y, x = at[0]+dy, at[1]+dx
            patch = terrain[y:y+5, x:x+5] if (
                y >= 0 and x >= 0 and y+5 <= 64 and x+5 <= 64) else None
            colors = [] if patch is None else sorted(set(int(n) for n in patch.ravel()))
            terrain_kinds[",".join(str(n) for n in colors) or "outside"] += 1
            for tag, prefix in (("direct", known_path), ("delayed", DETOUR + known_path)):
                word = prefix + action
                positions = prefix_positions(edges, prefix)
                if positions[-1] != list(at):
                    raise ValueError("known source path does not reach source vertex")
                trials.append({
                    "edge_id": pair_id, "history": tag, "word": word,
                    "known_prefix_positions": positions,
                    "unseen_source_position": list(at), "unseen_action": action,
                    "destination_tile_colors": colors,
                    "predicted_final_position": list(expected),
                    "predicted_moved": expected != at,
                    "unseen_edge_not_present_in_any_source": True,
                })
    if (len(pair_ids) != 39 or len(trials) != 78 or moved != 28 or
        blocked != 11 or terrain_kinds != Counter({
            "3":28, "4":8, "3,4,5":2, "5,9":1
        }) or len({t["word"] for t in trials}) != 78):
        raise ValueError("predeclared full reachable edge frontier changed")
    return {
        "kind": "AB_NATIVE_SOURCE_FROZEN_COMPLETE_FRONTIER_V1",
        "protocol": PROTOCOL,
        "source_experiment": "real official LS20, already independently observed",
        "past_source_sha256": OLD_SOURCE_SHA256,
        "known_native_edge_count": len(edges),
        "source_reachable_vertices": len(paths),
        "unique_unmeasured_edges": len(pair_ids),
        "predicted_moving_edges": moved, "predicted_blocked_edges": blocked,
        "predicted_destination_terrain_categories": dict(terrain_kinds),
        "histories_per_edge": ["direct", "delayed"],
        "delayed_known_source_roundtrips": 3,
        "original_native_root_hash": source_root,
        "source_frozen_trials": trials,
        "not_hidden_state": True, "not_general_F3": True,
        "not_previously_observed_final_edge": True
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--prior", type=Path, required=True)
    p.add_argument("--last", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    result = freeze(a.prior, a.last)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2) + "\n")
    print("AB_FROZEN_COMPLETE_FRONTIER " + json.dumps({
        "unmeasured_edges": result["unique_unmeasured_edges"],
        "direct_and_delayed_trials": len(result["source_frozen_trials"]),
        "move": result["predicted_moving_edges"],
        "block": result["predicted_blocked_edges"]
    }, sort_keys=True))

if __name__ == "__main__":
    main()
