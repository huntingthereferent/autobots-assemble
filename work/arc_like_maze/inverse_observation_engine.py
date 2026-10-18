"""Native F3 inverse observation from the preexisting mathematical World laws.

One precise finite formalization of A/B, not Language Referent's definition.
No REA dependency, no inferred native ARC correspondence, no bot wrapper.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
from .math import World, inverse_candidates


@dataclass(frozen=True)
class Observation:
    word: str
    endpoint: tuple[int, int, int]

    def __post_init__(self):
        if (not isinstance(self.word, str) or not self.word
                or len(self.word) > 12 or any(x not in "AB" for x in self.word)):
            raise ValueError("observation word must consist of A/B")
        if (not isinstance(self.endpoint, tuple) or len(self.endpoint) != 3
                or any(type(n) is not int or n not in range(3) for n in self.endpoint)):
            raise ValueError("requires a complete mathematical F3^3 endpoint")


@dataclass(frozen=True)
class Probe:
    word: str
    worst_case_survivors: int
    eliminated_pairs: int
    possible_outcomes: tuple


@dataclass(frozen=True)
class Investigation:
    observations: tuple[Observation, ...] = ()

    def __post_init__(self):
        if any(not isinstance(o, Observation) for o in self.observations):
            raise ValueError("invalid observation")
        words = [o.word for o in self.observations]
        if len(set(words)) != len(words):
            raise ValueError("duplicated observation word")

    def admit(self, observation: Observation) -> "Investigation":
        if not isinstance(observation, Observation):
            raise TypeError("requires an Observation")
        recorded = {o.word: o.endpoint for o in self.observations}
        if observation.word in recorded:
            if recorded[observation.word] != observation.endpoint:
                raise ValueError("conflicting repeat observation")
            return self
        return Investigation(self.observations + (observation,))

    @property
    def candidates(self) -> tuple[World, ...]:
        return tuple(w for w in inverse_candidates() if all(
            w.apply(o.word) == o.endpoint for o in self.observations))

    def next_probe(self, max_length: int = 6) -> Probe | None:
        """Minimax candidate partition from actual existing World.apply."""
        if type(max_length) is not int or not 1 <= max_length <= 8:
            raise ValueError("invalid search length budget")
        worlds = self.candidates
        if len(worlds) < 2:
            return None
        used = {o.word for o in self.observations}
        best = best_key = None
        for length in range(1, max_length + 1):
            for letters in product("AB", repeat=length):
                word = "".join(letters)
                if word in used:
                    continue
                groups = {}
                for world in worlds:
                    groups.setdefault(world.apply(word), []).append(world.phi)
                if len(groups) < 2:
                    continue
                groups = tuple((end, tuple(phis)) for end, phis in sorted(groups.items()))
                worst = max(len(phis) for _, phis in groups)
                total = len(worlds) * (len(worlds)-1) // 2
                left = sum(len(phis)*(len(phis)-1)//2 for _, phis in groups)
                separated = total-left
                key = (worst, -separated, length, word)
                if best_key is None or key < best_key:
                    best_key, best = key, Probe(word, worst, separated, groups)
        return best

    def receipt(self, max_length: int = 6) -> dict:
        candidates = self.candidates
        proposal = self.next_probe(max_length)
        status = ("CONTRADICTION" if not candidates else
                  "IDENTIFIED_WITHIN_F3_FAMILY" if len(candidates) == 1 else
                  "NEXT_OBSERVATION_PROPOSED" if proposal else "OBSERVATION_WALL")
        source = Path(__file__).resolve()
        return {
            "kind": "F3_ROOTED_INVERSE_OBSERVATION", "status": status,
            "scope": "nine original F3 worlds; only exact rooted full-math-state evidence",
            "source_sha256": {
                "original_math": sha256(source.with_name("math.py").read_bytes()).hexdigest(),
                "inverse_engine": sha256(source.read_bytes()).hexdigest(),
            },
            "observations": [{"word": o.word, "state": list(o.endpoint)}
                             for o in self.observations],
            "remaining_phi": [list(w.phi) for w in candidates],
            "next": None if proposal is None else {
                "word": proposal.word,
                "worst_case_survivors": proposal.worst_case_survivors,
                "separated_pairs": proposal.eliminated_pairs,
                "possible_outcomes": [
                    {"state": list(state), "phi": [list(p) for p in phis]}
                    for state, phis in proposal.possible_outcomes],
            },
            "native_arc_or_universal_ab_proof": False,
        }


def minimal_observations_certificate() -> dict:
    """Exact two-probe recovery and algebraic one-probe lower bound."""
    laws = inverse_candidates()
    signatures = {(w.apply("BB"), w.apply("BBB")) for w in laws}
    if len(laws) != 9 or len(signatures) != 9:
        raise AssertionError("original F3 source family changed")
    for world in laws:
        a, b = world.phi[1:]
        if world.apply("BB") != (0,2,a) or world.apply("BBB") != (0,0,(a+b)%3):
            raise AssertionError("two-word recovery formula failed")
    return {
        "status": "EXACT_WITHIN_NINE_F3_LAWS",
        "minimum_rooted_observations": 2,
        "distinguishing_words": ["BB","BBB"],
        "distinct_world_signatures": len(signatures),
        "recover": "a=z(BB); b=(z(BBB)-z(BB)) mod 3",
        "lower_bound": "first two coordinates independent of phi; x2 has three values",
        "no_native_arc_or_general_ab_correspondence": True,
    }


def _parse_endpoint(s: str) -> tuple[int, int, int]:
    try:
        value = tuple(int(p) for p in s.split(","))
    except ValueError as exc:
        raise ValueError("bad comma-separated full F3 state") from exc
    if len(value) != 3 or any(v not in range(3) for v in value):
        raise ValueError("requires F3^3 coordinates")
    return value


def main() -> None:
    p = argparse.ArgumentParser(description="Source-owned A/B finite inverse mathematical investigation")
    p.add_argument("--observe", action="append", default=[], help="WORD=x0,x1,x2")
    p.add_argument("--demo-phi", help="SYNTHETIC F3 source oracle a,b; NOT live ARC")
    p.add_argument("--max-length", type=int, default=6)
    p.add_argument("--certificate", action="store_true")
    args = p.parse_args()
    investigation = Investigation()
    for record in args.observe:
        word, equals, raw = record.partition("=")
        if not equals:
            p.error("use WORD=x0,x1,x2")
        investigation = investigation.admit(Observation(word, _parse_endpoint(raw)))
    result = {"initial": investigation.receipt(args.max_length)}
    if args.demo_phi is not None:
        a,b = tuple(int(v) for v in args.demo_phi.split(","))
        world = World(3,(0,a,b))
        moves = []
        for _ in range(9):
            probe = investigation.next_probe(args.max_length)
            if probe is None:
                break
            state = world.apply(probe.word)
            investigation = investigation.admit(Observation(probe.word,state))
            moves.append({"word":probe.word, "SYNTHETIC_state":list(state),
                          "remaining_phi":[list(w.phi) for w in investigation.candidates]})
        result["synthetic_F3_demonstration"] = {"oracle_phi": list(world.phi),
            "movements":moves,"final": investigation.receipt(args.max_length),
            "not_observed_native_ARC":True}
    if args.certificate:
        result["certificate"] = minimal_observations_certificate()
    print(json.dumps(result,indent=2))


if __name__ == "__main__":
    main()
