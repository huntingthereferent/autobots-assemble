"""Source-derived rooted equality observations for the original 48 A/B laws.

A fixed-word count is an unpointed conjugacy invariant. Equality of two
action-word endpoints *at the distinguished origin* is a different, pointed
invariant. Never turn a predicted relation into an admitted observation.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import argparse
import json

from .window_combined import CombinedWorld, classify_pair, family, rooted_conflict
from .window_inverse_observation import (
    Investigation as FixedInvestigation, Observation as FixedObservation,
    measured, ident, WORDS,
)

ROOT = (0, 0, 0)
WordPair = tuple[str, str]


@lru_cache(maxsize=1)
def witness_catalog() -> tuple[WordPair, ...]:
    """Derive admissible rooted probes from the original all-depth relation.

    These are mathematical potential probes, not externally observed truths.
    """
    pairs: set[WordPair] = set()
    for a, b in combinations(family(), 2):
        relation = classify_pair(a, b)
        if relation.kind is None or relation.root_preserving:
            continue
        witness = rooted_conflict(a, b)
        if witness is None:
            raise AssertionError("proved nonroot map has no rooted collision")
        word1, word2, same, result1, result2 = witness
        if (word1 == word2 or
            a.apply(ROOT, word1) != a.apply(ROOT, word2) or
            b.apply(ROOT, word1) == b.apply(ROOT, word2) or
            same != a.apply(ROOT, word1) or
            result1 != b.apply(ROOT, word1) or
            result2 != b.apply(ROOT, word2)):
            raise AssertionError("source-derived rooted probe did not replay")
        pairs.add(tuple(sorted((word1, word2))))
    if not pairs:
        raise AssertionError("no root-specific words found in source")
    return tuple(sorted(pairs, key=lambda words: (
        len(words[0]) + len(words[1]), max(map(len, words)), words
    )))


@dataclass(frozen=True)
class RootEqualityObservation:
    words: WordPair
    equal_at_origin: bool

    def __post_init__(self) -> None:
        if (not isinstance(self.words, tuple) or len(self.words) != 2
                or any(not isinstance(w, str) for w in self.words)
                or tuple(sorted(self.words)) not in witness_catalog()):
            raise ValueError("rooted probe not admitted by source witness catalog")
        if type(self.equal_at_origin) is not bool:
            raise ValueError("rooted equality observation requires an exact boolean")

    @property
    def key(self) -> WordPair:
        return tuple(sorted(self.words))


@lru_cache(maxsize=2048)
def rooted_equal(law: CombinedWorld, words: WordPair) -> bool:
    if words not in witness_catalog():
        raise ValueError("word pair is not an admitted rooted source probe")
    return law.apply(ROOT, words[0]) == law.apply(ROOT, words[1])


@dataclass(frozen=True)
class RootedInvestigation:
    fixed: FixedInvestigation = FixedInvestigation()
    rooted: tuple[RootEqualityObservation, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.fixed, FixedInvestigation) or any(
            not isinstance(o, RootEqualityObservation) for o in self.rooted
        ):
            raise ValueError("invalid evidence domain")
        if len({o.key for o in self.rooted}) != len(self.rooted):
            raise ValueError("duplicate rooted word pair")

    def admit_fixed(self, evidence: FixedObservation) -> "RootedInvestigation":
        next_fixed = self.fixed.admit(evidence)
        if next_fixed is self.fixed:
            return self
        return RootedInvestigation(next_fixed, self.rooted)

    def admit_root(self, evidence: RootEqualityObservation) -> "RootedInvestigation":
        if not isinstance(evidence, RootEqualityObservation):
            raise TypeError("rooted evidence required")
        prior = {o.key: o.equal_at_origin for o in self.rooted}
        if evidence.key in prior:
            if prior[evidence.key] != evidence.equal_at_origin:
                raise ValueError("conflicting rooted observation")
            return self
        return RootedInvestigation(self.fixed, self.rooted + (evidence,))

    @property
    def candidates(self) -> tuple[CombinedWorld, ...]:
        return tuple(w for w in self.fixed.candidates if all(
            rooted_equal(w, o.key) == o.equal_at_origin for o in self.rooted
        ))

    def next_fixed(self) -> dict | None:
        # Use the full unpointed source classifier before seeking a root-specific
        # probe. The previously admitted root evidence is never discarded.
        candidates = self.candidates
        if not candidates:
            return None
        used = {o.word for o in self.fixed.observations}
        best = None
        for word in WORDS:
            if word in used:
                continue
            buckets: dict[int, list[CombinedWorld]] = {}
            for law in candidates:
                buckets.setdefault(measured(law, word), []).append(law)
            if len(buckets) < 2:
                continue
            total_pairs = len(candidates) * (len(candidates)-1) // 2
            remaining = sum(len(group)*(len(group)-1)//2
                            for group in buckets.values())
            key = (max(map(len, buckets.values())), remaining, len(word), word)
            if best is None or key < best[0]:
                best = (key, word, buckets, total_pairs - remaining)
        if best is None:
            return None
        _, word, buckets, separated = best
        return {"word": word, "separated_pairs": separated,
                "predictions_NOT_admitted": [
                    {"count": n, "candidate_laws": [list(ident(w)) for w in laws]}
                    for n, laws in sorted(buckets.items())
                ]}

    def next_root(self) -> dict | None:
        candidates = self.candidates
        if len(candidates) < 2 or self.next_fixed() is not None:
            return None
        used = {o.key for o in self.rooted}
        best = None
        for words in witness_catalog():
            if words in used:
                continue
            groups: dict[bool, list[CombinedWorld]] = {}
            for law in candidates:
                groups.setdefault(rooted_equal(law, words), []).append(law)
            if len(groups) < 2:
                continue
            total = len(candidates)*(len(candidates)-1)//2
            remaining = sum(len(v)*(len(v)-1)//2 for v in groups.values())
            key = (max(map(len, groups.values())), remaining,
                   sum(map(len, words)), words)
            if best is None or key < best[0]:
                best = (key, words, groups, total-remaining)
        if best is None:
            return None
        _, words, groups, separated = best
        return {"words": list(words), "separated_pairs": separated,
                "possible_equality_results_NOT_observed": [
                    {"equal_at_origin": observed,
                     "candidate_laws": [list(ident(w)) for w in laws]}
                    for observed, laws in sorted(groups.items())
                ]}

    def receipt(self) -> dict:
        candidates = self.candidates
        fixed_probe = self.next_fixed()
        root_probe = self.next_root()
        all_root_equivalent = bool(candidates) and all(
            (rel.kind is not None and rel.root_preserving)
            for a, b in combinations(candidates, 2)
            for rel in (classify_pair(a, b),)
        )
        if not candidates:
            status = "CONTRADICTION"
        elif fixed_probe is not None:
            status = "NEXT_FIXED_COUNT_PROPOSED"
        elif root_probe is not None:
            status = "NEXT_ROOT_EQUALITY_PROPOSED"
        elif all_root_equivalent:
            status = "ROOTED_CLASS_IDENTIFIED_WITHIN_DECLARED_FAMILY"
        else:
            status = "ROOTED_OBSERVATION_WALL"
        original = Path(__file__).resolve()
        return {
            "kind": "A_B_WINDOW48_ROOTED_INVERSE",
            "status": status,
            "math_source_sha256": sha256(original.with_name("window_combined.py").read_bytes()).hexdigest(),
            "engine_source_sha256": sha256(original.read_bytes()).hexdigest(),
            "fixed_evidence": [
                {"word": o.word, "count": o.fixed} for o in self.fixed.observations
            ],
            "root_evidence": [
                {"words": list(o.key), "equal_at_origin": o.equal_at_origin}
                for o in self.rooted
            ],
            "surviving_laws": [list(ident(w)) for w in candidates],
            "next_fixed": fixed_probe,
            "next_root": root_probe,
            "unpointed_counts_do_not_imply_rooted_conjugacy": True,
            "predictions_are_not_observed_evidence": True,
            "native_arc_or_general_referent_claimed": False,
        }


def certify_rooted_inverse() -> dict:
    """Replay independent synthetic answers for every actual 48-law source."""
    results = []
    rooted_queries = 0
    for oracle in family():
        state = RootedInvestigation()
        fixed_steps = root_steps = 0
        for _ in range(8):
            fixed = state.next_fixed()
            if fixed is not None:
                state = state.admit_fixed(
                    FixedObservation(fixed["word"], measured(oracle, fixed["word"]))
                )
                fixed_steps += 1
                continue
            root = state.next_root()
            if root is not None:
                words = tuple(root["words"])
                state = state.admit_root(
                    RootEqualityObservation(words, rooted_equal(oracle, words))
                )
                root_steps += 1
                continue
            break
        if state.receipt()["status"] != "ROOTED_CLASS_IDENTIFIED_WITHIN_DECLARED_FAMILY":
            raise AssertionError("rooted inverse did not finish: " + str(ident(oracle)))
        if oracle not in state.candidates or len(state.candidates) != 3:
            raise AssertionError("correct rooted shear-class not recovered")
        results.append({"oracle_law": list(ident(oracle)),
                        "fixed_steps": fixed_steps,
                        "root_steps": root_steps,
                        "surviving_rooted_class": [list(ident(w)) for w in state.candidates]})
        rooted_queries += root_steps
    return {
        "status": "COMPLETE_WITHIN_DECLARED_WINDOW48",
        "mathematical_laws_checked": len(results),
        "distinct_rooted_classes": len({
            tuple(map(tuple, r["surviving_rooted_class"])) for r in results
        }),
        "root_probes_for_all_source_laws": rooted_queries,
        "maximum_root_probes_per_law": max(r["root_steps"] for r in results),
        "maximum_fixed_probes_per_law": max(r["fixed_steps"] for r in results),
        "root_witness_catalog_size": len(witness_catalog()),
        "not_live_arc_or_general_ab": True,
        "synthetic_oracle_checks": results,
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Rooted A/B observation over source 48-law F3 window")
    p.add_argument("--count", action="append", default=[], help="WORD=FIXED")
    p.add_argument("--root", action="append", default=[], help="WORD1,WORD2=true|false")
    p.add_argument("--demo-law", help="Synthetic oracle k,c,pulse,balanced; NOT ARC")
    p.add_argument("--certificate", action="store_true")
    args = p.parse_args()
    state = RootedInvestigation()
    for spec in args.count:
        word, sep, value = spec.partition("=")
        if not sep:
            p.error("count format WORD=FIXED")
        state = state.admit_fixed(FixedObservation(word, int(value)))
    for spec in args.root:
        words, sep, val = spec.partition("=")
        if not sep or val not in ("true", "false"):
            p.error("root format WORD1,WORD2=true|false")
        pair = tuple(sorted(words.split(",")))
        state = state.admit_root(RootEqualityObservation(pair, val == "true"))
    output = {"initial": state.receipt()}
    if args.demo_law:
        oracle = CombinedWorld(*(int(n) for n in args.demo_law.split(",")))
        steps = []
        for _ in range(8):
            fixed, rooted = state.next_fixed(), state.next_root()
            if fixed is not None:
                observed = measured(oracle, fixed["word"])
                state = state.admit_fixed(FixedObservation(fixed["word"], observed))
                steps.append({"source": "SYNTHETIC F3 oracle", "kind": "fixed",
                              "word": fixed["word"], "count": observed})
            elif rooted is not None:
                words = tuple(rooted["words"])
                value = rooted_equal(oracle, words)
                state = state.admit_root(RootEqualityObservation(words, value))
                steps.append({"source": "SYNTHETIC F3 oracle", "kind": "root",
                              "words": list(words), "equal_at_origin": value})
            else:
                break
        output["synthetic_demo"] = {
            "oracle_law": list(ident(oracle)), "steps": steps,
            "final": state.receipt(), "not_native_arc": True,
        }
    if args.certificate:
        output["certificate"] = certify_rooted_inverse()
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
