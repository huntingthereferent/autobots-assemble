"""ChatGPT Run: bounded native ARC-AGI-3 feasibility lane.

Two explicit policies: the archived FT09 visible-frame rule policy, or an
OpenAI-backed LLM from the official ARC-AGI-3-Agents harness. No archived
routes are read. This is a local opt-in experiment, not a competition claim.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Callable


def frame_digest(observation: Any) -> str | None:
    """Hash a complete publicly returned 64x64 palette frame, not private game state."""
    frames = getattr(observation, "frame", None)
    if frames is None or len(frames) == 0:
        return None
    latest = frames[-1]
    if hasattr(latest, "tolist"):
        latest = latest.tolist()
    def flatten(value):
        if isinstance(value, (tuple, list)):
            for item in value:
                yield from flatten(item)
        else:
            yield int(value)
    try:
        cells = list(flatten(latest))
    except (TypeError, ValueError):
        return None
    if len(cells) != 4096 or any(cell < 0 or cell > 15 for cell in cells):
        return None
    return hashlib.sha256(bytes(cells)).hexdigest()


def value_name(value: Any) -> str | None:
    if value is None:
        return None
    result = getattr(value, "name", value)
    return str(result)


class ObservedArc:
    """Transparent step wrapper: captures what native SDK returned.

    A capture does not independently certify the policy, its motives, or
    frame ownership. The underlying official SDK remains the environment.
    """
    def __init__(self, environment: Any):
        self.environment = environment
        self.transitions: list[dict[str, Any]] = []

    def __getattr__(self, name: str) -> Any:
        return getattr(self.environment, name)

    def step(self, action: Any, *args: Any, **kwargs: Any) -> Any:
        before = getattr(self.environment, "observation_space", None)
        after = self.environment.step(action, *args, **kwargs)
        supplied_data = kwargs.get("data", args[0] if args else None)
        # Action data is bounded to public scalar coordinates in the receipt.
        data = {}
        if isinstance(supplied_data, dict):
            for key in ("x", "y"):
                val = supplied_data.get(key)
                if type(val) is int and 0 <= val < 64:
                    data[key] = val
        if not data:
            embedded = getattr(action, "data", None)
            if isinstance(embedded, dict):
                for key in ("x", "y"):
                    val = embedded.get(key)
                    if type(val) is int and 0 <= val < 64:
                        data[key] = val
        self.transitions.append({
            "index": len(self.transitions) + 1,
            "action": value_name(action),
            "coordinates": data,
            "before_frame_sha256": frame_digest(before),
            "after_frame_sha256": frame_digest(after),
            "native_state": value_name(getattr(after, "state", None)),
            "levels_completed": getattr(after, "levels_completed", None),
        })
        return after


def make_policy(
    policy: str,
    game: str,
    budget: int,
    model: str | None,
    observed: ObservedArc,
    *,
    policy_class: type | None = None,
) -> Any:
    """Import the appropriate agent only after explicit policy admission."""
    if policy_class is None:
        if policy == "ft09-visible":
            from research.arc_native_runs.ft09_visible_causal_agent import VisibleCausalPolicy
            policy_class = VisibleCausalPolicy
        else:
            from agents.templates.llm_agents import LLM
            policy_class = LLM
    attrs: dict[str, Any] = {"MAX_ACTIONS": budget}
    if policy == "chatgpt-model":
        attrs["MODEL"] = model
    bounded = type("BoundedChatGPTRunPolicy", (policy_class,), attrs)
    return bounded(
        card_id="chatgpt-run",
        game_id=game,
        agent_name="chatgpt-run-" + policy,
        ROOT_URL="http://localhost",
        record=False,
        arc_env=observed,
    )


def validate(game: str, policy: str, budget: int, model: str | None, *, key: str | None) -> None:
    if not game or not all(c.isalnum() or c in "-_" for c in game):
        raise ValueError("a safe exact game ID is required")
    if policy not in {"ft09-visible", "chatgpt-model"}:
        raise ValueError("unknown policy")
    if not 1 <= budget <= 200:
        raise ValueError("action budget must be between 1 and 200")
    if policy == "ft09-visible" and game.lower() != "ft09":
        raise ValueError("FT09 visible policy is only valid for FT09")
    if policy == "chatgpt-model" and (not model or not key):
        raise ValueError("model policy needs --model and OPENAI_API_KEY")


def run(
    *, game: str, policy: str, budget: int, model: str | None, output: Path,
    api_key: str | None = None,
    arcade_factory: Callable[[], Any] | None = None,
    policy_class: type | None = None,
) -> dict[str, Any]:
    validate(game, policy, budget, model, key=api_key)
    if arcade_factory is None:
        from arc_agi import Arcade, OperationMode
        arcade_factory = lambda: Arcade(operation_mode=OperationMode.OFFLINE)
    arc = arcade_factory()
    env = arc.make(game.lower())
    observed = ObservedArc(env)
    agent = make_policy(policy, game.lower(), budget, model, observed, policy_class=policy_class)
    failure = None
    try:
        agent.main()
    except Exception as exc:
        failure = f"{type(exc).__name__}: {str(exc)[:250]}"
    frames = getattr(agent, "frames", []) or []
    latest = frames[-1] if frames else None
    state = value_name(getattr(latest, "state", None))
    levels = getattr(latest, "levels_completed", None)
    # A local win is only a native result. It is not an independent evaluation.
    won = bool(failure is None and observed.transitions and state == "WIN"
               and observed.transitions[-1]["native_state"] == "WIN")
    reported_failures = [str(x)[:200] for x in (getattr(agent, "failures", []) or [])]
    if reported_failures:
        won = False
    receipt = {
        "schema": "chatgpt-run-arc-feasibility-v1",
        "game": game.lower(),
        "policy": policy,
        "model": model if policy == "chatgpt-model" else None,
        "mode": "OFFLINE",
        "budget": budget,
        "action_count": len(observed.transitions),
        "native_state": state,
        "levels_completed": levels,
        "native_win_observed": won,
        "error": failure,
        "policy_failures": reported_failures,
        "claim": ("FRESH_LOCAL_NATIVE_WIN_NOT_INDEPENDENTLY_REPRODUCED"
                  if won else "NO_VERIFIED_WIN"),
        "evidence_boundary": (
            "FT09-specific visible-frame policy; not first-contact generalization"
            if policy == "ft09-visible" else
            "OpenAI API model-driven local actions; no independent external evaluator"
        ),
        "transitions": observed.transitions,
    }
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    temp = output.with_name(output.name + ".tmp")
    temp.write_text(json.dumps(receipt, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    temp.replace(output)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description="Bounded native ARC feasibility run; receipts kept separate from saved routes.")
    parser.add_argument("--game", default="ft09")
    parser.add_argument("--policy", choices=("ft09-visible", "chatgpt-model"), default="ft09-visible")
    parser.add_argument("--model", help="Explicit OpenAI API model ID; required with chatgpt-model")
    parser.add_argument("--budget", type=int, default=80)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = run(game=args.game, policy=args.policy, budget=args.budget,
                 model=args.model, output=args.output, api_key=os.environ.get("OPENAI_API_KEY"))
    print(json.dumps({key: result[key] for key in (
        "game", "policy", "action_count", "native_state", "levels_completed",
        "native_win_observed", "claim", "error"
    )}, indent=2))
    return 0 if result["native_win_observed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
