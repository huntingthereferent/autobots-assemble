"""Training-only A/B bounded heterogeneous source-relation patterns.

Discover SOURCE-OBSERVED 2-edge relation-code patterns only from original
PharmKG training rows; never look at heldout examples or their labels to choose
patterns. Each witness preserves two exact source triples and SHA-256 digests.
This measures graph association only: different relation codes do NOT create
valid biomedical entailment, clinical treatment or temporal knowledge.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from hashlib import sha256

SCHEMA = "ab-training-only-heterogeneous-source-metapaths/v1"
RELATIONS = ("GG", "T", "P", "I")
CALIBRATION_PER_RELATION = 64
TOP_PATTERNS = 3
TRAIN_SALT = "AB-P2-pharmkg-train-calibration-26023"
TEST_SALT = "AB-P2-pharmkg-untouched-test-26023"
MAX_TRAIN_EDGES = 500000
MAX_NODE_DEGREE = 20000


def selection_digest(item, salt):
    return sha256(("\t".join(item)+"|"+salt).encode("utf8")).hexdigest()


def training_graph(rows):
    if type(rows) is not list or len(rows) > MAX_TRAIN_EDGES:
        raise ValueError("original finite training triple source required")
    forward = defaultdict(list)
    reverse = defaultdict(list)
    ground = set()
    for raw in rows:
        if (type(raw) is not tuple or len(raw) != 3 or
            any(type(x) is not str or not x or len(x) > 256
                or "\t" in x or "\n" in x for x in raw)):
            raise ValueError("invalid exact source triple")
        if raw in ground:
            raise ValueError("source triples must be deduplicated before indexing")
        ground.add(raw)
        head, rel, tail = raw
        forward[head].append((rel, tail))
        reverse[tail].append((rel, head))
    if any(len(x) > MAX_NODE_DEGREE for x in list(forward.values())+list(reverse.values())):
        raise ValueError("source node degree exceeds declared bounded graph")
    for index in (forward, reverse):
        for values in index.values():
            values.sort()
    return {"forward":forward, "reverse":reverse, "triples":ground}


def observed_patterns(graph, head, tail):
    """Inspect original 2-edge source witnesses, not a guessed semantic rule."""
    incoming = defaultdict(set)
    for rel, mid in graph["reverse"].get(tail, ()):
        if mid not in (head, tail):
            incoming[mid].add(rel)
    result = {}
    for rel_a, mid in graph["forward"].get(head, ()):
        if mid not in incoming:
            continue
        for rel_b in incoming[mid]:
            if rel_a != rel_b:
                pair = (rel_a, rel_b)
                if pair not in result or mid < result[pair]:
                    result[pair] = mid
    return result


def discover(rows, graph):
    """Frozen train-only discovery; direct target edge never acts as a 2-hop witness."""
    choices = {}
    receipts = {}
    for target_rel in RELATIONS:
        training = [t for t in rows if t[1] == target_rel]
        sorted_train = sorted(
            training, key=lambda t:(selection_digest(t, TRAIN_SALT), t))
        if len(sorted_train) < CALIBRATION_PER_RELATION:
            raise ValueError("insufficient original training-only calibration edges")
        chosen = sorted_train[:CALIBRATION_PER_RELATION]
        support = Counter()
        for head, _, tail in chosen:
            # Excluding intermediate=head/tail prevents target direct edge
            # from being counted as a composed alternate source path.
            support.update(observed_patterns(graph, head, tail).keys())
        ranked = sorted(
            support.items(), key=lambda kv:(-kv[1],kv[0]))
        choices[target_rel] = tuple(k for k,_ in ranked[:TOP_PATTERNS])
        receipts[target_rel] = {
            "training_positive_samples":len(chosen),
            "observed_mixed_relation_patterns":len(support),
            "selected_patterns":[{
                "first_relation":first,"second_relation":second,
                "training_sample_support":support[(first, second)]
            } for first,second in choices[target_rel]],
            "calibration_source_sha256":sha256(
                "\n".join("\t".join(t) for t in chosen).encode()).hexdigest(),
        }
    return choices,receipts


def witness(graph, *, head, target_rel, tail, frozen_patterns):
    if type(frozen_patterns) not in (tuple,list):
        raise ValueError("frozen source metapaths required")
    if any(type(s) is not str or not s for s in (head,target_rel,tail)):
        raise ValueError("exact biomedical source query required")
    if (head,target_rel,tail) in graph["triples"]:
        raise ValueError("direct training edge must not be evaluated as heldout")
    all_pairs = observed_patterns(graph, head, tail)
    for rank,pair in enumerate(frozen_patterns, start=1):
        if (type(pair) is not tuple or len(pair)!=2
                or pair[0]==pair[1] or
                any(type(p) is not str or not p for p in pair)):
            raise ValueError("only explicitly frozen heterogeneous two-hop patterns")
        mid=all_pairs.get(pair)
        if mid is None:
            continue
        first=(head,pair[0],mid)
        second=(mid,pair[1],tail)
        if first not in graph["triples"] or second not in graph["triples"]:
            raise ValueError("source metapath fabricated a missing original edge")
        return {
            "schema":SCHEMA,
            "path_exists":True,
            "selected_pattern_rank":rank,
            "source_edge_triples":[list(first),list(second)],
            "source_edge_sha256":[sha256("\t".join(t).encode()).hexdigest()
                                  for t in (first,second)],
            "source_intermediate":mid,
            "ranking_feature":1/rank,
            "biomedical_entailment_established":False,
            "temporal_fact_established":False,
        }
    return {
        "schema":SCHEMA,"path_exists":False,"selected_pattern_rank":None,
        "source_edge_triples":[],"source_edge_sha256":[],
        "source_intermediate":None,"ranking_feature":0,
        "biomedical_entailment_established":False,
        "temporal_fact_established":False,
    }
