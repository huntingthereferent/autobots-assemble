"""Independent broader-pool PharmKG heldout measurement; no biological inference.

The original source-owner test split is selected only for evaluation. Everything
that determines ranking, including the three mixed metapath patterns, comes
from source-authenticated TRAIN alone. The 128 TRAIN-vocabulary candidate
tails per question are a frozen, deterministic *sample*, not full entity ranking
and not verified negatives. An independent static scorer is mandatory.
"""
from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
from pathlib import Path
import argparse
import json

from . import ab_pharmkg_training_metapath_witness as ab
from . import nih_p2_pharmkg_frozen_heterogeneous_trial as prior
from . import nih_p2_external_pharmkg_heldout_trial as source

SCHEMA = "nih-p2-bounded-broad-pharmkg-heldout-v1"
SALT = "nih-p2-broad-untouched-20261022-v1"
POOL = 128
PER_RELATION = 16
MAX_CASES = PER_RELATION * len(ab.RELATIONS)


def choose_new(test, train):
    old_a = set(source.select_test(test, train))
    old_b = set(prior.untouched_new_heldout(test, train)[0])
    tr = set(train)
    selected = []
    for rel in ab.RELATIONS:
        eligible = (row for row in test if row[1] == rel
                    and row not in old_a and row not in old_b and row not in tr)
        ordered = sorted(set(eligible), key=lambda t: (
            sha256(("\t".join(t) + "|" + SALT).encode()).hexdigest(), t))
        if len(ordered) < PER_RELATION:
            raise ValueError("insufficient independent untouched heldout positives")
        selected.extend(ordered[:PER_RELATION])
    if (len(selected) != MAX_CASES or len(set(selected)) != MAX_CASES or
            set(selected) & (old_a | old_b | tr)):
        raise ValueError("candidate selection overlaps source precedent or training")
    return selected


def choose_pool(head, rel, positive, vocabulary, known, pool=POOL):
    if not 2 <= pool <= 512:
        raise ValueError("bounded source candidate count required")
    if not isinstance(positive, str) or not positive:
        raise ValueError("positive candidate missing")
    # Use *TRAIN vocabulary only*. No TEST/VALID tail used to manufacture a
    # conveniently easy negative. Test/valid are used after scoring ONLY to
    # report known-positive collisions, never for ranking feature discovery.
    candidates = sorted((tail for tail in vocabulary[rel]
                         if tail != positive and (head, rel, tail) not in known),
                        key=lambda x: (sha256((SALT+"|"+head+"|"+rel+"|"+x)
                                              .encode()).hexdigest(), x))
    if len(candidates) < pool:
        raise ValueError("too few source TRAIN-vocabulary alternatives")
    return [positive] + candidates[:pool]


def rank(scores):
    """Tie-aware fractional rank: 1 + better scores + half of other ties."""
    if not scores or any(type(x) not in (int, float) or x < 0 for x in scores):
        raise ValueError("numeric nonnegative source scores required")
    return 1 + sum(x > scores[0] for x in scores[1:]) + (
        sum(x == scores[0] for x in scores[1:]) / 2)


def evaluate(*, train_file: Path, test_file: Path, valid_file: Path,
             pool: int = POOL):
    train, tr_id = source.read_source(train_file, "train.tsv")
    test, te_id = source.read_source(test_file, "test.tsv")
    valid, va_id = source.read_source(valid_file, "valid.tsv")
    graph = ab.training_graph(train)
    rules, calibration = ab.discover(train, graph)
    static = prior.independent_static_graph(train)
    selected = choose_new(test, train)
    train_set = set(train)
    # These are only for known-positive collision counts / standard filtering.
    # The frozen candidate selection is independent of TEST/VALID labels.
    all_known = train_set | set(test) | set(valid)
    vocabulary = defaultdict(set)
    for _, relation, tail in train:
        vocabulary[relation].add(tail)
    cases = []
    for head, relation, positive in selected:
        candidates = choose_pool(head, relation, positive, vocabulary, train_set, pool)
        own_scores, oracle_scores = [], []
        source_witnesses = []
        for tail in candidates:
            if (head, relation, tail) in train_set:
                raise ValueError("candidate has direct training edge")
            actual = ab.witness(graph, head=head, target_rel=relation, tail=tail,
                                frozen_patterns=rules[relation])
            oracle, mid = prior.independent_pattern_score(
                static, head, tail, rules[relation])
            if oracle != actual["ranking_feature"]:
                raise ValueError("independent equally capable static rank disagrees")
            if actual["path_exists"] and mid != actual["source_intermediate"]:
                raise ValueError("original source intermediate mismatch")
            for edge, digest in zip(actual["source_edge_triples"],
                                    actual["source_edge_sha256"]):
                if tuple(edge) not in train_set or sha256(
                        "\t".join(edge).encode()).hexdigest() != digest:
                    raise ValueError("fabricated or corrupted original source edge")
            own_scores.append(actual["ranking_feature"])
            oracle_scores.append(oracle)
            if tail == positive:
                source_witnesses = actual["source_edge_triples"]
        arank = rank(own_scores)
        srank = rank(oracle_scores)
        if arank != srank:
            raise ValueError("A/B ranking differs from equally capable static oracle")
        # Diagnostic only: unknown alternative labels must not be called negatives.
        collided = sum((head, relation, tail) in all_known
                       for tail in candidates[1:])
        cases.append({
            "original_test_head": head,
            "original_relation_code": relation,
            "original_heldout_positive_tail": positive,
            "alternative_count": pool,
            "candidate_count": pool + 1,
            "candidate_selection_train_vocabulary_only": True,
            "unlabeled_alternatives_are_negatives": False,
            "known_positive_alternative_collisions": collided,
            "raw_tie_midrank": arank,
            "static_same_information_midrank": srank,
            "positive_score": own_scores[0],
            "num_higher_scored_alternatives": sum(x > own_scores[0] for x in own_scores[1:]),
            "num_equal_scored_alternatives": sum(x == own_scores[0] for x in own_scores[1:]),
            "positive_original_train_source_witness": source_witnesses,
            "positive_original_source_sha256": [
                sha256("\t".join(edge).encode()).hexdigest()
                for edge in source_witnesses],
        })
    def metrics():
        ranks = [x["raw_tie_midrank"] for x in cases]
        return {
            "cases": len(ranks),
            "hits_at_1": sum(r <= 1 for r in ranks),
            "hits_at_3": sum(r <= 3 for r in ranks),
            "hits_at_10": sum(r <= 10 for r in ranks),
            "MRR": round(sum(1/r for r in ranks)/len(ranks), 6),
            "mean_rank": round(sum(ranks)/len(ranks), 6),
        }
    cases_by_rel = {
        rel: {"cases": PER_RELATION,
              "hits_at_3": sum(c["raw_tie_midrank"] <= 3 for c in cases
                               if c["original_relation_code"] == rel)}
        for rel in ab.RELATIONS
    }
    return {
        "schema": SCHEMA,
        "source_owner": source.ORIGIN,
        "source_commit": source.COMMIT,
        "source_files": {"train": tr_id, "test": te_id, "valid": va_id},
        "selection_salt": SALT,
        "selected_digest_sha256": sha256("\n".join(
            "\t".join(t) for t in selected).encode()).hexdigest(),
        "calibration": calibration,
        "candidate_design": "TRAIN-tail-vocabulary-bounded-sha256-sample",
        "candidate_pool_alternatives": pool,
        "candidate_pool_is_full_entity_ranking": False,
        "test_and_valid_labels_used_for_training_or_scoring": False,
        "unlabeled_alternatives_confirmed_false": False,
        "original_splits_are_temporal": False,
        "official_NIH_benchmark": False,
        "original_W13_modified": False,
        "equally_capable_static_rank_disagreements": 0,
        "A_B_and_static_same_information_metrics": metrics(),
        "by_relation": cases_by_rel,
        "all_cases": cases,
    }


def main():
    a = argparse.ArgumentParser()
    for s in ("train", "test", "valid", "output"):
        a.add_argument("--"+s, type=Path, required=True)
    a.add_argument("--pool", type=int, default=POOL)
    x = a.parse_args()
    result = evaluate(train_file=x.train, test_file=x.test,
                      valid_file=x.valid, pool=x.pool)
    x.output.parent.mkdir(parents=True, exist_ok=True)
    x.output.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print(json.dumps({"status":"MEASURED_PROXY",
                      "sampled_alternatives":x.pool,
                      "scores":result["A_B_and_static_same_information_metrics"],
                      "NIH_complete":False}, sort_keys=True))


if __name__ == "__main__":
    main()
