from __future__ import annotations

from collections import Counter, defaultdict, deque
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

from latent_state import perceive
from program_synthesis import parse_synthesis
from symbolic_program_solver import parse_program, solve_program


def click(env, xy, why):
    x, y = xy
    action = GameAction.ACTION6
    action.set_data({"x": int(x), "y": int(y)})
    return env.step(
        action,
        data={"x": int(x), "y": int(y)},
        reasoning={"generic_latent_solver": why},
    )


def execute_symbolic(env, obs):
    model = parse_program(perceive(obs))
    if model is None:
        return None, 0, "symbolic:no-model"

    assignment = solve_program(model)
    if assignment is None:
        return None, 0, "symbolic:no-solution"

    resources = {r.idx: r for r in model.resources}
    used = set()
    actions = 0
    cur = obs

    for xy, rid in assignment.items():
        if rid in used:
            return None, actions, "symbolic:resource-reused"
        used.add(rid)
        res = resources[rid]
        cur = click(env, res.xy, f"select {res.kind} resource {rid}:{res.color}")
        actions += 1
        cur = click(env, xy, f"write symbolic variable {xy}")
        actions += 1

    cur = env.step(
        GameAction.ACTION5,
        data={},
        reasoning={"generic_latent_solver": "execute synthesized program"},
    )
    actions += 1
    return cur, actions, "symbolic"


def execute_direct_flatten(env, obs):
    s = parse_synthesis(perceive(obs))
    if s is None or len(s.leaves) != len(s.target):
        return None, 0, "direct:no-shape"

    queues = defaultdict(deque)
    for color, xy in s.palette:
        queues[color].append(xy)

    need = Counter(s.target)
    have = Counter({color: len(q) for color, q in queues.items()})
    if any(have[color] < n for color, n in need.items()):
        return None, 0, "direct:insufficient-resources"

    cur = obs
    actions = 0
    for color, xy in zip(s.target, s.leaves):
        resource_xy = queues[color].popleft()
        cur = click(env, resource_xy, f"select terminal {color}")
        actions += 1
        cur = click(env, xy, f"write direct leaf {xy}")
        actions += 1

    cur = env.step(
        GameAction.ACTION5,
        data={},
        reasoning={"generic_latent_solver": "execute direct flattened program"},
    )
    actions += 1
    return cur, actions, "direct"


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: generic_latent_controller.py GAME_ID")

    game_id = sys.argv[1]
    arcade = arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    env = arcade.make(game_id)
    obs = env.observation_space

    total_actions = 0
    history = []

    for _ in range(32):
        level = int(obs.levels_completed)
        if "WIN" in str(obs.state):
            break

        # Prefer the richer symbolic constraint model whenever it can prove a
        # complete assignment. Fall back to direct visual flattening only when
        # the simple leaf relation is fully supported.
        nxt, used, mode = execute_symbolic(env, obs)
        if nxt is None:
            nxt, used, mode = execute_direct_flatten(env, obs)

        if nxt is None:
            print("WALL", level, mode)
            break

        total_actions += used
        new_level = int(nxt.levels_completed)
        history.append((level, new_level, mode, used))
        print("MOVE", level, "->", new_level, mode, "actions", used)

        if new_level <= level and "WIN" not in str(nxt.state):
            print("WALL no level progress")
            break

        obs = nxt

    print("FINAL", obs.levels_completed, obs.win_levels, obs.state)
    print("TOTAL_ACTIONS", total_actions)
    print("HISTORY", history)


if __name__ == "__main__":
    main()
