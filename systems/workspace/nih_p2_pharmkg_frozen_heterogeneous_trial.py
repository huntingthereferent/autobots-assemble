"""Independent new-heldout PharmKG experiment with training-frozen mixed metapaths.

The target heldout split is separate from the training-only metapath
discovery. Exclude every previously evaluated heldout positive from the new
64-question subset using a new fixed salt. Score the new A/B mixed-relation
feature against (a) unchanged same-relation predecessor, (b) independently
implemented full-static frozen-pattern traversal, and (c) a static untyped
two-hop connectivity comparator. These test-only candidates are UNLABELED
alternatives, not confirmed false. No temporal source dates are invented.
"""
from __future__ import annotations

from collections import defaultdict,Counter
from hashlib import sha256
from pathlib import Path
from random import Random
import argparse
import json

from . import ab_pharmkg_training_metapath_witness as mixed
from . import ab_heldout_biomedical_relation_paths as earlier
from . import nih_p2_external_pharmkg_heldout_trial as original

SCHEMA="nih-p2-pharmkg-heldout-mixed-relation-structural-proxy/v1"
NEW_SEED=26023
QUESTIONS_PER_RELATION=16


def untouched_new_heldout(test_rows, train_rows):
    old=set(original.select_test(test_rows,train_rows))
    tr=set(train_rows)
    chosen=[]
    for rel in mixed.RELATIONS:
        admissible=sorted(
            (t for t in test_rows
             if t[1]==rel and t not in old and t not in tr),
            key=lambda t:(mixed.selection_digest(t,mixed.TEST_SALT),t))
        if len(admissible)<QUESTIONS_PER_RELATION:
            raise ValueError("not enough genuinely new original heldout tests")
        chosen.extend(admissible[:QUESTIONS_PER_RELATION])
    if len(set(chosen))!=len(chosen) or set(chosen)&old or set(chosen)&tr:
        raise ValueError("new heldout selection leaked prior or training triples")
    return chosen,sha256("\n".join("\t".join(t) for t in chosen).encode()).hexdigest()


def independent_static_graph(rows):
    """Separate original static adjacency: no A/B functions or output reused."""
    forward=defaultdict(set)
    reverse=defaultdict(set)
    all_forward=defaultdict(set)
    all_reverse=defaultdict(set)
    for a,r,b in rows:
        forward[(a,r)].add(b)
        reverse[(b,r)].add(a)
        all_forward[a].add(b)
        all_reverse[b].add(a)
    return {
        "forward":forward,"reverse":reverse,
        "all_forward":all_forward,"all_reverse":all_reverse
    }


def independent_pattern_score(index,head,tail,patterns):
    """Compute rank directly from original graph set joins, independently."""
    for i,(r1,r2) in enumerate(patterns,start=1):
        mids=(index["forward"].get((head,r1),set()) &
              index["reverse"].get((tail,r2),set()))-{head,tail}
        if mids:
            return 1/i,sorted(mids)[0]
    return 0,None


def static_any_twohop(index,head,tail):
    return bool((index["all_forward"].get(head,set()) &
                 index["all_reverse"].get(tail,set()))-{head,tail})


def execute(*,train_file,test_file,valid_file):
    train,train_id=original.read_source(train_file,"train.tsv")
    test,test_id=original.read_source(test_file,"test.tsv")
    valid,valid_id=original.read_source(valid_file,"valid.tsv")
    del valid
    # Strict source-owner integrity checks happen before any pattern discovery.
    graph=mixed.training_graph(train)
    frozen,calibration=mixed.discover(train,graph)
    frozen_sha=sha256(json.dumps(
        calibration,sort_keys=True).encode()).hexdigest()
    selected,selection_sha=untouched_new_heldout(test,train)
    old=earlier.build(train)
    static=independent_static_graph(train)
    tr_set=set(train)
    te_set=set(test)
    tails=defaultdict(set)
    for h,rel,t in train:
        if rel in mixed.RELATIONS:tails[rel].add(t)
    for h,rel,t in test:
        if rel in mixed.RELATIONS:tails[rel].add(t)
    tails={k:sorted(v) for k,v in tails.items()}
    rng=Random(NEW_SEED)
    cases=[]
    for h,rel,target in selected:
        alternatives=original.controls_for(
            (h,rel,target),tails,tr_set,te_set,rng)
        scored=[]
        for dest in [target]+alternatives:
            ab=mixed.witness(
                graph,head=h,target_rel=rel,tail=dest,
                frozen_patterns=frozen[rel])
            baseline_score,static_middle=independent_pattern_score(
                static,h,dest,frozen[rel])
            if baseline_score!=ab["ranking_feature"]:
                raise ValueError("A/B training-frozen path disagrees with separate full static graph")
            if ab["path_exists"] and ab["source_intermediate"]!=static_middle:
                raise ValueError("independent static source path witness differs")
            for edge,hash_value in zip(ab["source_edge_triples"],ab["source_edge_sha256"]):
                if tuple(edge) not in tr_set or sha256(
                    "\t".join(edge).encode()).hexdigest()!=hash_value:
                    raise ValueError("training source relationship fabricated")
            prior=earlier.witness(
                old,head=h,relation=rel,tail=dest,max_hops=3)
            prev_score=original.candidate_score(prior["source_path_hops"])
            anypath=static_any_twohop(static,h,dest)
            scored.append({
                "candidate":dest,"is_external_test_positive":dest==target,
                "A_B_mixed_metapath_rank_feature":ab["ranking_feature"],
                "independent_static_frozen_metapath_feature":baseline_score,
                "A_B_selected_pattern_rank":ab["selected_pattern_rank"],
                "A_B_source_witness":ab["source_edge_triples"],
                "A_B_original_edge_sha256":ab["source_edge_sha256"],
                "predecessor_same_relation_3hop_feature":prev_score,
                "untyped_independent_static_any_2hop":anypath,
                "biomedical_entailment_claim":False,
            })
        own=original.rank_scores(
            [r["A_B_mixed_metapath_rank_feature"] for r in scored])
        control_rank=original.rank_scores(
            [r["independent_static_frozen_metapath_feature"] for r in scored])
        predecessor=original.rank_scores(
            [r["predecessor_same_relation_3hop_feature"] for r in scored])
        untyped_rank=original.rank_scores(
            [int(r["untyped_independent_static_any_2hop"]) for r in scored])
        cases.append({
            "original_test_head":h,"original_relation":rel,
            "original_test_positive_tail":target,
            "new_external_positive_excluded_from_graph":True,
            "old_previously_scored_positive_excluded":True,
            "mixed_source_path_for_heldout_positive":
                scored[0]["A_B_mixed_metapath_rank_feature"]>0,
            "mixed_rank":own,"equal_strength_independent_static_rank":control_rank,
            "predecessor_same_relation_rank":predecessor,
            "independent_static_untyped_twohop_rank":untyped_rank,
            "candidates":scored,
        })
    def summarize(key):
        vals=[r[key] for r in cases]
        return {"hits_at_1":sum(r<=1 for r in vals),
                "hits_at_3":sum(r<=3 for r in vals),
                "mean_reciprocal_rank":round(sum(1/r for r in vals)/len(vals),6),
                "mean_rank":round(sum(vals)/len(vals),6)}
    relation_results={}
    for rel in mixed.RELATIONS:
        subset=[r for r in cases if r["original_relation"]==rel]
        relation_results[rel]={
            "questions":len(subset),
            "positive_has_frozen_mixed_source_witness":
                sum(r["mixed_source_path_for_heldout_positive"] for r in subset),
            "mixed_hits1":sum(r["mixed_rank"]<=1 for r in subset),
            "prior_same_relation_hits1":
                sum(r["predecessor_same_relation_rank"]<=1 for r in subset),
        }
    a=summarize("mixed_rank")
    b=summarize("equal_strength_independent_static_rank")
    if a!=b:
        raise ValueError("A/B metapath ranking diverged from equally capable original static graph")
    return {
        "schema":SCHEMA,
        "external_owner":original.ORIGIN,
        "original_source_commit":original.COMMIT,
        "entire_source_split_identities":{
            "train":train_id,"test":test_id,"valid":valid_id},
        "source_owner_original_train_unique_rows":len(train),
        "training_calibration_only":True,
        "calibration_before_heldout_selection":True,
        "frozen_calibration_source_digest_sha256":frozen_sha,
        "frozen_patterns_training_only":calibration,
        "untouched_new_heldout_selection_digest_sha256":selection_sha,
        "previously_scored_test_selection_excluded":True,
        "new_heldout_questions":len(cases),
        "unlabeled_alternative_tails_per_question":original.CONTROLS,
        "all_graph_features_use_original_training_rows_only":True,
        "mixed_A_B_proxy":a,
        "independent_equal_strength_static_mixed_proxy":b,
        "prior_same_relation_3hop_proxy":summarize("predecessor_same_relation_rank"),
        "independent_untyped_static_2hop_proxy":summarize(
            "independent_static_untyped_twohop_rank"),
        "A_B_vs_equal_strength_static_disagreements":0,
        "by_original_relation":relation_results,
        "clinical_entailment_demonstrated":False,
        "real_biomedical_temporal_event_dates":False,
        "source_split_chronological":False,
        "official_NIH_Phase2_benchmark_reproduced":False,
        "original_W13_runtime_modified":False,
        "World48_required":False,
        "original_source_file_bodies_redistributed":False,
        "case_results":cases,
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ("train","test","valid","output"):
        p.add_argument("--"+k,required=True,type=Path)
    a=p.parse_args()
    result=execute(train_file=a.train,test_file=a.test,valid_file=a.valid)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n",
                        encoding="utf8")
    print(json.dumps({
        "new_heldout_questions":result["new_heldout_questions"],
        "AB_mixed":result["mixed_A_B_proxy"],
        "prior_same_relation":result["prior_same_relation_3hop_proxy"],
        "equal_strength_static":result["independent_equal_strength_static_mixed_proxy"],
        "untyped_static":result["independent_untyped_static_2hop_proxy"],
        "relation_results":result["by_original_relation"],
        "NIH_Phase2_completed":False,
    },sort_keys=True))


if __name__=="__main__":
    main()
