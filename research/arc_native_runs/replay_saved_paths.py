"""Replay saved ARC-AGI-3 native action routes from archived research.
These routes are not independent agents; required SDK/data are external.
No official competition submission, unseen-game success, or current SDK result is claimed.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from arc_agi import Arcade, OperationMode
from arcengine import GameAction

ROOT = Path(__file__).resolve().parent

def replay(game_id: str):
    record = json.loads((ROOT / f"{game_id}_route.json").read_text(encoding="utf-8"))
    paths = record.get("coordinate_paths_by_level") or record.get("game_action_ids_by_level")
    assert sum(len(x) for x in paths) == record["locally_reported"]["actions"]
    arcade = Arcade(operation_mode=OperationMode.NORMAL)
    env = arcade.make(game_id)
    executed = 0
    transitions = []
    last_level = 0
    for level, actions in enumerate(paths, 1):
        for value in actions:
            if game_id == "ft09":
                x, y = value
                obs = env.step(GameAction.ACTION6, data={"x": x, "y": y})
            elif game_id == "sk48" and value == 6:
                # From original local replay: reads engine-private controller objects.
                # May be incompatible with a different ARC SDK implementation.
                internal = env._game
                other = next(k for k in internal.xpmcmtbcv if k != internal.vzvypfsnt)
                obs = env.step(GameAction.ACTION6, data={"x": int(other.x+2), "y": int(other.y+2)})
            else:
                obs = env.step(GameAction.from_id(value), data={})
            executed += 1
            if obs.levels_completed > last_level:
                last_level = obs.levels_completed
                transitions.append((executed, last_level))
            if obs.state.name == "WIN":
                break
        if obs.state.name == "WIN":
            break
    print(json.dumps({
        "game": game_id,
        "native_state": obs.state.name,
        "levels_completed": obs.levels_completed,
        "actions": executed,
        "milestones": transitions,
        "matches_reported_completion": bool(
            obs.state.name == "WIN"
            and obs.levels_completed == record["locally_reported"]["levels"]
            and executed == record["locally_reported"]["actions"]
            and [m[0] for m in transitions] == record["recorded_milestones"]
        )
    }, indent=2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("game", choices=("ft09","ls20","sk48"))
    replay(parser.parse_args().game)
