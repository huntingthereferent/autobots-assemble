"""Unstupid arena: deterministic challenge scoring for independent agents.

Agent responses are submitted externally. No LLM is instantiated here.
A challenge is scored by native transitions, not persuasive language.
"""
from dataclasses import dataclass
from work.arc_like_maze.math import World


@dataclass(frozen=True)
class Challenge:
    agent: str
    motive: str
    actions: str
    predicted: tuple[int, ...]


@dataclass(frozen=True)
class Verdict:
    agent: str
    motive: str
    actions: str
    predicted: tuple[int, ...]
    observed: tuple[int, ...]
    outcome: str


def adjudicate(world: World, challenges: tuple[Challenge, ...]) -> tuple[Verdict, ...]:
    verdicts = []
    for challenge in challenges:
        if not challenge.agent.strip():
            raise ValueError("agent id required")
        if any(action not in "AB" for action in challenge.actions):
            raise ValueError("invalid action")
        observed = world.apply(challenge.actions)
        outcome = "SUPPORTED" if challenge.predicted == observed else "CORRECTED"
        verdicts.append(Verdict(challenge.agent, challenge.motive,
                                challenge.actions, challenge.predicted,
                                observed, outcome))
    return tuple(verdicts)


def scoreboard(verdicts: tuple[Verdict, ...]) -> dict:
    return {
        "agents_entered": len({v.agent for v in verdicts}),
        "challenges": len(verdicts),
        "corrected": sum(v.outcome == "CORRECTED" for v in verdicts),
        "supported": sum(v.outcome == "SUPPORTED" for v in verdicts),
    }
