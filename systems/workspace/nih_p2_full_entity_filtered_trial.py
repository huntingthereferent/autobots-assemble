"""Full finite-universe, filtered PharmKG heldout ranking with independent oracle.

Re-use EXACT fixed TRAIN-only mixed metapath rules. Compute scores against the
declared union of original source train/test/valid entity IDs (not merely nine
or 129 hand-picked candidates). Published test/valid labels only filter out
*other known positives* in metric computation, never create graph features,
change rules or enter A/B witness paths. This is still not the published NIH
benchmark, not a temporal test, and not a biological implication.
"""
from __future__ import annotations
from collections import defaultdict
from hashlib import sha256
from pathlib import Path
import argparse
import json

from . import ab_pharmkg_training_metapath_witness as mixed
from . import nih_p2_pharmkg_frozen_heterogeneous_trial as previous
from . import nih_p2_external_pharmkg_heldout_trial as original
from . import nih_p2_broad_heldout_trial as broad

SCHEMA="nih-p2-pharmkg-frozen-full-entity-filtered-ranking-v1"
MAX_ENTITIES=12000
MAX_WORK=800000
REQUIRED_CASES=64


def original_entity_universe(train, test, valid):
    # Exactly the original submitted splits, not expanded to an unrelated
    # entity dictionary or selectively filtered by target relation.
    values=sorted({s for rows in (train,test,valid) for a,r,b in rows
                   for s in (a,b)})
    if not values or len(values)>MAX_ENTITIES:
        raise ValueError("original entity universe outside declared bounds")
    return values


def ab_scores_for_head(graph, head, patterns, allowed):
    """Direct bounded *source-graph* two-edge movement, once per head.

    Compute path-exists score from original TRAIN adjacency, no test answers.
    Matches the semantics of mixed.witness for all nondirect, non-self targets.
    """
    output={}
    for position,(first,second) in enumerate(patterns,1):
        if first==second or not first or not second:
            raise ValueError("invalid frozen two-code pattern")
        for r1,mid in graph["forward"].get(head,()):
            if r1!=first or mid==head:
                continue
            for r2,tail in graph["forward"].get(mid,()):
                if r2!=second or tail in (head,mid) or tail not in allowed:
                    continue
                if (head,first,mid) not in graph["triples"] or (mid,second,tail) not in graph["triples"]:
                    raise ValueError("source-owned relation path not present")
                # Frozen pattern order is primary. Do not rerank on TEST labels.
                if tail not in output:
                    output[tail]=1/position
    return output


def tie_aware_rank(target_score, candidate_scores):
    better=0
    tied=0
    for val in candidate_scores:
        if val>target_score:better+=1
        if val==target_score:tied+=1
    if tied==0:
        raise ValueError("target has vanished from source candidate universe")
    return 1 + better + (tied-1)/2


def run(*, train_file:Path,test_file:Path,valid_file:Path):
    train,trid=original.read_source(train_file,"train.tsv")
    test,teid=original.read_source(test_file,"test.tsv")
    valid,vaid=original.read_source(valid_file,"valid.tsv")
    graph=mixed.training_graph(train)
    frozen,calibration=mixed.discover(train,graph)
    questions=broad.choose_new(test,train)
    universe=original_entity_universe(train,test,valid)
    if len(questions)!=REQUIRED_CASES or len(universe)*len(questions)>MAX_WORK:
        raise ValueError("predeclared finite full-entity capacity exceeded")
    entity_set=set(universe)
    known=defaultdict(set)
    for a,r,b in (*train,*test,*valid):
        known[(a,r)].add(b)
    independent=previous.independent_static_graph(train)
    cases=[]
    for head,rel,gold in questions:
        if gold not in entity_set:
            raise ValueError("original heldout gold absent from candidate universe")
        a_b=ab_scores_for_head(graph,head,frozen[rel],entity_set)
        # Genuine equal-strength static reasoner checks ALL original candidates.
        static=[]
        mismatches=0
        for tail in universe:
            oracle,_=previous.independent_pattern_score(independent,head,tail,frozen[rel])
            if tail==head:
                # A/B disallows repeated intermediate and self-target.
                oracle=0
            if oracle != a_b.get(tail,0):
                mismatches+=1
            static.append(oracle)
        if mismatches:
            raise ValueError("A/B exhaustive source path scores diverged from independent static graph")
        # Filter only OTHER known positives, including test/valid to avoid
        # penalizing a correctly ranked alternative source-positive. This
        # diagnostic filter does not feed path discovery or score generation.
        ignored=known[(head,rel)]-{gold}
        filtered=[a_b.get(t,0) for t in universe if t not in ignored]
        unfiltered=[a_b.get(t,0) for t in universe]
        target=a_b.get(gold,0)
        ab_direct=mixed.witness(graph,head=head,target_rel=rel,tail=gold,
                                frozen_patterns=frozen[rel])
        if target != ab_direct["ranking_feature"]:
            raise ValueError("optimized A/B path scorer disagrees with original A/B witness")
        cases.append({
            "head":head,"relation":rel,"heldout_gold":gold,
            "original_training_witness":ab_direct["source_edge_triples"],
            "original_witness_sha256":ab_direct["source_edge_sha256"],
            "candidate_universe_count":len(universe),
            "other_known_gold_excluded_from_filtered_rank":len(ignored & entity_set),
            "source_path_score":target,
            "full_unfiltered_tie_aware_rank":tie_aware_rank(target,unfiltered),
            "full_filtered_tie_aware_rank":tie_aware_rank(target,filtered),
            "independent_static_all_candidate_disagreements":0,
        })
    def metrics(field):
        rs=[c[field] for c in cases]
        return {"n":len(rs),"hits_at_1":sum(v<=1 for v in rs),
                "hits_at_3":sum(v<=3 for v in rs),
                "hits_at_10":sum(v<=10 for v in rs),
                "MRR":round(sum(1/v for v in rs)/len(rs),6),
                "mean_rank":round(sum(rs)/len(rs),6)}
    return {
        "schema":SCHEMA,
        "source_owner":original.ORIGIN,
        "source_commit":original.COMMIT,
        "source_files":{"train":trid,"test":teid,"valid":vaid},
        "calibration_from_train_only":calibration,
        "selection_sha256":sha256("\n".join("\t".join(t) for t in questions).encode()).hexdigest(),
        "original_source_entities_from_all_splits":len(universe),
        "full_candidate_universe_sha256":sha256("\n".join(universe).encode()).hexdigest(),
        "all_eligible_source_entities_scored":True,
        "candidate_limit_exceeded":False,
        "independent_equal_strength_static_feature_disagreements":0,
        "A_B_raw_unfiltered":metrics("full_unfiltered_tie_aware_rank"),
        "A_B_source_label_filtered":metrics("full_filtered_tie_aware_rank"),
        "equally_capable_static_scores_identical":True,
        "original_source_splits_chronological":False,
        "test_valid_labels_used_for_model_or_rule_selection":False,
        "test_valid_labels_used_only_to_filter_other_known_positives":True,
        "actual_negative_labels_known":False,
        "clinical_effectiveness_inferred":False,
        "original_W13_journal_modified":False,
        "official_NIH_benchmark":False,
        "cases":cases,
    }


def main():
    p=argparse.ArgumentParser()
    for key in ("train","test","valid","output"):
        p.add_argument("--"+key,type=Path,required=True)
    args=p.parse_args()
    result=run(train_file=args.train,test_file=args.test,valid_file=args.valid)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"n":result["A_B_source_label_filtered"]["n"],
                      "entity_candidates":result["original_source_entities_from_all_splits"],
                      "filtered":result["A_B_source_label_filtered"],
                      "unfiltered":result["A_B_raw_unfiltered"],
                      "NIH_completed":False},sort_keys=True))

if __name__=="__main__":
    main()
