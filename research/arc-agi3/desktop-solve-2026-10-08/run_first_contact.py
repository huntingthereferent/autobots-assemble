"""Instrumented ARC-AGI-3 first-contact runner.

Run from a checkout of the official ARC-AGI-3-Kaggle-Starter, or pass
--starter-root. It preserves one untouched run as the discovery-inclusive
witness. By default it refuses to overwrite an existing first-contact result.

Example:
    python run_first_contact.py \
      --starter-root /path/to/ARC-AGI-3-Kaggle-Starter \
      --agent /path/to/my_agent.py \
      --out first_contact_run.json

The output records the agent SHA-256, public game roster, actual action_counter
for each game, levels completed, terminal state, and the official aggregate
scorecard representation. No banked/minimized replay is substituted.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_agent(path: Path):
    spec = importlib.util.spec_from_file_location("first_contact_agent", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    if not hasattr(mod, "MyAgent"):
        raise RuntimeError(f"{path} must define MyAgent")
    return mod.MyAgent


def frame_level_segments(frames) -> list[int]:
    """Best-effort action segments from recorded FrameData.

    The official scorecard remains authoritative. This helper is kept as an
    audit lens: it assumes each post-initial FrameData corresponds to one
    environment interaction.
    """
    if not frames:
        return []
    last = int(getattr(frames[0], "levels_completed", 0))
    seg = 0
    out = []
    for frame in frames[1:]:
        seg += 1
        cur = int(getattr(frame, "levels_completed", last))
        if cur > last:
            for _ in range(cur - last):
                out.append(seg)
                seg = 0
            last = cur
    return out


def scorecard_lens(sc):
    out = {"repr": repr(sc)}
    for name in ("score", "level_scores", "runs"):
        if hasattr(sc, name):
            v = getattr(sc, name)
            try:
                json.dumps(v)
                out[name] = v
            except TypeError:
                out[name] = repr(v)
    return out


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--starter-root", type=Path, required=True)
    p.add_argument("--agent", type=Path, required=True)
    p.add_argument("--out", type=Path, default=Path("first_contact_run.json"))
    p.add_argument("--max-actions", type=int, default=1200)
    p.add_argument("--allow-repeat", action="store_true")
    args = p.parse_args()

    if args.out.exists() and not args.allow_repeat:
        raise SystemExit(
            f"{args.out} already exists. Refusing to overwrite the first-contact "
            "witness. Use a new output path or --allow-repeat for a non-first run."
        )

    root = args.starter_root.resolve()
    agent_path = args.agent.resolve()
    vendor = root / "vendor" / "ARC-AGI-3-Agents"
    if not vendor.exists():
        raise SystemExit(f"{vendor} not found; run 'make setup' in the official starter first.")

    sys.path.insert(0, str(root))
    sys.path.insert(0, str(vendor))

    import arc_agi
    from arc_agi import OperationMode

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    MyAgent = load_agent(agent_path)
    if hasattr(MyAgent, "MAX_ACTIONS"):
        MyAgent.MAX_ACTIONS = min(int(MyAgent.MAX_ACTIONS), args.max_actions)

    arcade = arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    env_infos = arcade.get_environments()
    game_ids = [e.game_id.split("-", 1)[0] for e in env_infos]

    result = {
        "schema_version": 1,
        "kind": "ARC3_FIRST_CONTACT_DISCOVERY_INCLUSIVE",
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "agent_path": str(agent_path),
        "agent_sha256": sha256(agent_path),
        "starter_root": str(root),
        "game_roster": game_ids,
        "games": {},
        "rules": {
            "count_discovery_actions": True,
            "banked_replay_substitution_allowed": False,
            "per_game_hardcoding_allowed": False,
        },
    }

    # Write the manifest before play so even a crash preserves the exact agent
    # and declared first-contact start.
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n")

    for index, gid in enumerate(game_ids, 1):
        print(f"=== [{index}/{len(game_ids)}] {gid} ===", flush=True)
        env = arcade.make(gid)
        if env is None:
            row = {"error": "environment creation failed"}
            result["games"][gid] = row
            args.out.write_text(json.dumps(result, indent=2) + "\n")
            continue

        agent = MyAgent(
            card_id="first-contact-audit",
            game_id=gid,
            agent_name=f"FirstContact.{gid}",
            ROOT_URL="http://localhost",
            record=False,
            arc_env=env,
            tags=["first-contact", "discovery-inclusive"],
        )
        agent.main()

        final = agent.frames[-1]
        row = {
            "state": str(final.state),
            "levels_completed": int(getattr(final, "levels_completed", 0)),
            "win_levels": int(getattr(final, "win_levels", 0)),
            "actual_action_counter": int(agent.action_counter),
            "frame_count": len(agent.frames),
            "level_action_segments_best_effort": frame_level_segments(agent.frames),
        }
        result["games"][gid] = row
        args.out.write_text(json.dumps(result, indent=2) + "\n")
        print(row, flush=True)

    result["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
    result["official_scorecard"] = scorecard_lens(arcade.get_scorecard())
    result["summary"] = {
        "games_seen": len(result["games"]),
        "games_win_state": sum("WIN" in r.get("state", "") for r in result["games"].values()),
        "total_levels_completed": sum(r.get("levels_completed", 0) for r in result["games"].values()),
        "total_environment_actions": sum(r.get("actual_action_counter", 0) for r in result["games"].values()),
    }
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result["summary"], indent=2))


if __name__ == "__main__":
    main()
