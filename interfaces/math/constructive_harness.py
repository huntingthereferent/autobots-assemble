"""Constructive Unstupid harness experiments.

Challenges against the finite world generate evidence. Candidate extensions
are proposed from discrepancies but never silently promoted to world rules.
"""
from dataclasses import dataclass
from work.arc_like_maze.math import World, inverse_candidates
from interfaces.math.arena import Challenge, adjudicate, scoreboard


@dataclass(frozen=True)
class Experiment:
    baseline: tuple[int, int, int]
    challenge_results: tuple
    score: dict
    proposed_extensions: tuple[tuple[int, int, int], ...]
    tested_extensions: tuple[tuple[int, int, int], ...]
    status: str


def construct_and_test(reference: World, challenges: tuple[Challenge, ...]) -> Experiment:
    """Score challenges, propose finite candidate alternatives, test against observations.

    Proposals remain distinct from accepted rules. An alternative is retained
    only when it reproduces every provided prediction AND differs from the
    reference on at least one tested path. These are mathematical proposals,
    not evidence that an AI has changed its mind.
    """
    if reference.depth != 3:
        raise ValueError("this experiment uses three-dimensional candidates")
    verdicts = adjudicate(reference, challenges)
    proposals = []
    verified = []
    for candidate in inverse_candidates():
        if candidate == reference:
            continue
        if any(candidate.apply(c.actions) != reference.apply(c.actions) for c in challenges):
            proposals.append(candidate.phi)
            if all(candidate.apply(c.actions) == c.predicted for c in challenges):
                verified.append(candidate.phi)
    return Experiment(reference.phi, verdicts, scoreboard(verdicts),
                      tuple(proposals), tuple(verified),
                      "PROPOSALS_REQUIRE_INDEPENDENT_OBSERVATION")


def demonstration() -> Experiment:
    reference = World(3, (0, 1, 2))
    alternative = World(3, (0, 2, 1))
    return construct_and_test(reference, (
        Challenge("baseline", "test expected rule", "ABB", reference.apply("ABB")),
        Challenge("challenger", "test alternative relation", "ABB", alternative.apply("ABB")),
        Challenge("skeptic", "deny A movement", "A", (0, 0, 0)),
    ))
