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


def per_relation_failure_diagnostics(cases, entity_count):
    """Frozen heldout error diagnosis; no new model, rules, or negative labels."""
    if not cases or entity_count < 2:
        raise ValueError("missing source heldout cohort or candidate count")
    categories = sorted({c["relation"] for c in cases})
    result = {}
    for rel in categories:
        rows = [c for c in cases if c["relation"] == rel]
        if not rows:
            raise ValueError("empty original source relation cohort")
        null_reciprocal = 0.0
        scored = 0
        rank_deltas = []
        for c in rows:
            n = c["candidate_universe_count"]
            excluded = c["other_known_gold_excluded_from_filtered_rank"]
            if n != entity_count or type(excluded) is not int or not 0 <= excluded < n:
                raise ValueError("candidate denominator or positive-filter count changed")
            if c["full_filtered_tie_aware_rank"] > c["full_unfiltered_tie_aware_rank"]:
                raise ValueError("known-positive filter worsened ranking")
            if not 1 <= c["full_filtered_tie_aware_rank"] <= n-excluded:
                raise ValueError("filtered rank outside original eligible candidates")
            if c["source_path_score"] < 0:
                raise ValueError("negative original source witness score")
            scored += c["source_path_score"] > 0
            rank_deltas.append(c["full_unfiltered_tie_aware_rank"] -
                               c["full_filtered_tie_aware_rank"])
            # Independently declared all-constant-score baseline: every
            # eligible tail tied, no test labels used as model features.
            null_reciprocal += 2/(n-excluded+1)
        result[rel] = {
            "heldout_original_gold_cases": len(rows),
            "gold_with_frozen_training_source_path": scored,
            "gold_without_frozen_training_source_path": len(rows)-scored,
            "filtered_hits_at_10": sum(c["full_filtered_tie_aware_rank"]<=10 for c in rows),
            "filtered_MRR": round(sum(1/c["full_filtered_tie_aware_rank"] for c in rows)/len(rows),6),
            "all_equal_score_null_MRR": round(null_reciprocal/len(rows),6),
            "mean_known_positive_filter_rank_reduction": round(sum(rank_deltas)/len(rows),6),
            "unknown_alternatives_are_not_confirmed_negatives": True,
        }
    if sum(x["heldout_original_gold_cases"] for x in result.values())!=len(cases):
        raise ValueError("per-relation case aggregation mismatch")
    return result


def frozen_train_relation_tail_frequency(train):
    """TRAIN-only per-predicate tail count; zero source inference assumptions."""
    counts=defaultdict(int)
    for head,relation,tail in train:
        counts[(relation,tail)] += 1
    if not counts:
        raise ValueError("original TRAIN frequency source empty")
    return counts


def per_relation_frequency_baseline(train,universe,questions,known):
    """Score exactly the frozen 64 heldout questions on the original entity universe.

    TEST/VALID edges filter other known positive candidates only; they are
    never counted as TRAIN frequencies. This is a separate, weaker family of
    ranking models, not an equal-strength path reasoner.
    """
    freq=frozen_train_relation_tail_frequency(train)
    eligible=set(universe)
    results=[]
    for head,relation,gold in questions:
        if gold not in eligible:
            raise ValueError("gold missing from original candidate universe")
        other=known[(head,relation)]-{gold}
        scores=[freq.get((relation,tail),0) for tail in universe if tail not in other]
        gold_score=freq.get((relation,gold),0)
        rank=tie_aware_rank(gold_score,scores)
        if rank<1 or rank>len(scores):
            raise ValueError("source-only frequency rank out of bounds")
        results.append({"relation":relation,
                        "source_train_tail_frequency":gold_score,
                        "other_known_positives_excluded":len(other&eligible),
                        "filtered_tie_aware_rank":rank})
    ranks=[x["filtered_tie_aware_rank"] for x in results]
    return {
        "source":"original_train_only_relation_specific_tail_frequency",
        "n":len(ranks),
        "hits_at_1":sum(x<=1 for x in ranks),
        "hits_at_3":sum(x<=3 for x in ranks),
        "hits_at_10":sum(x<=10 for x in ranks),
        "MRR":round(sum(1/x for x in ranks)/len(ranks),6),
        "mean_rank":round(sum(ranks)/len(ranks),6),
        "test_valid_edges_used_for_training":False,
        "questions_or_frozen_rules_changed":False,
        "actual_negative_labels_known":False,
        "individual_case_diagnostics":results,
    }


def paired_path_frequency_rank_audit(cases,frequency):
    """D3: pair each unchanged source gold question across independent rankers."""
    rows=frequency.get("individual_case_diagnostics",())
    if not cases or len(rows)!=len(cases) or frequency.get("n")!=len(cases):
        raise ValueError("paired comparator denominators not identical")
    stats={}
    for src,other in zip(cases,rows):
        if (src["relation"]!=other["relation"] or
            src["other_known_gold_excluded_from_filtered_rank"] !=
            other["other_known_positives_excluded"]):
            raise ValueError("not the exact same original source question/filter")
        relation=src["relation"]
        item=stats.setdefault(relation,{
            "cases":0,"frequency_better_rank":0,"path_better_rank":0,
            "equal_rank":0,"frequency_hits_at_10":0,"path_hits_at_10":0,
            "path_source_witness_gold_cases":0,
            "frequency_reciprocal_sum":0.0,"path_reciprocal_sum":0.0})
        a=src["full_filtered_tie_aware_rank"]
        b=other["filtered_tie_aware_rank"]
        if not 1 <= a <= src["candidate_universe_count"] or not 1 <= b <= src["candidate_universe_count"]:
            raise ValueError("invalid paired rank")
        item["cases"]+=1
        item["frequency_better_rank"]+=int(b<a)
        item["path_better_rank"]+=int(a<b)
        item["equal_rank"]+=int(a==b)
        item["frequency_hits_at_10"]+=int(b<=10)
        item["path_hits_at_10"]+=int(a<=10)
        item["path_source_witness_gold_cases"]+=int(src["source_path_score"]>0)
        item["frequency_reciprocal_sum"]+=1/b
        item["path_reciprocal_sum"]+=1/a
    for val in stats.values():
        if val["frequency_better_rank"]+val["path_better_rank"]+val["equal_rank"]!=val["cases"]:
            raise ValueError("paired wins do not reconcile")
        val["frequency_MRR"]=round(val.pop("frequency_reciprocal_sum")/val["cases"],6)
        val["path_MRR"]=round(val.pop("path_reciprocal_sum")/val["cases"],6)
    return {
        "by_original_relation":dict(sorted(stats.items())),
        "same_frozen_original_heldout_queries":True,
        "different_model_family_not_equivalent_static_oracle":True,
        "original_model_features_unchanged":True,
        "test_labels_not_used_to_select_rules":True,
        "official_NIH_benchmark":False,
    }


NEXT_COHORT_SALT="nih-p2-lane-d2-frozen-next-cohort-20261022-v1"

def choose_d2_heldout(test,train):
    """Prospectively freeze an untouched 64-case cohort before scoring.

    Exclude prior original, mixed, broad/full, and separate A tail-role
    selections. No model feature depends on TEST answers.
    """
    # Build the 386k-row source index exactly once. Rebuilding it within
    # a 50k-row generator made the identical cohort needlessly expensive.
    train_set=set(train)
    prior_source=set(original.select_test(test,train))
    prior_mixed=set(previous.untouched_new_heldout(test,train)[0])
    earlier_full=set(broad.choose_new(test,train))
    # The independent TRAIN-tail role ablation in NIH A uses this exact
    # documented frozen source selector. Exclude it without importing A.
    from hashlib import sha256 as hash_source
    a_salt="nih-p2-broad-untouched-20261022-v1"
    prior_roles=set()
    for rel in mixed.RELATIONS:
        elig=sorted((t for t in test if t[1]==rel and
                     t not in prior_source and t not in prior_mixed and
                     t not in train_set),
                    key=lambda t:(hash_source(("\t".join(t)+"|"+a_salt).encode()).hexdigest(),t))
        prior_roles.update(elig[:16])
    excluded=prior_source|prior_mixed|earlier_full|prior_roles|train_set
    cohort=[]
    for rel in mixed.RELATIONS:
        eligible=sorted(
            {t for t in test if t[1]==rel and t not in excluded},
            key=lambda t:(hash_source(("\t".join(t)+"|"+NEXT_COHORT_SALT).encode()).hexdigest(),t))
        if len(eligible)<16:
            raise ValueError("frozen D2 source heldout underflow")
        cohort.extend(eligible[:16])
    if len(cohort)!=64 or len(set(cohort))!=64 or not set(cohort).isdisjoint(excluded):
        raise ValueError("D2 cohort reused prior measured source questions")
    return cohort


def run(*, train_file:Path,test_file:Path,valid_file:Path,selection="original"):
    train,trid=original.read_source(train_file,"train.tsv")
    test,teid=original.read_source(test_file,"test.tsv")
    valid,vaid=original.read_source(valid_file,"valid.tsv")
    graph=mixed.training_graph(train)
    frozen,calibration=mixed.discover(train,graph)
    if selection not in ("original","d2_untouched"):
        raise ValueError("unrecognized heldout selection protocol")
    questions=(broad.choose_new(test,train) if selection=="original"
               else choose_d2_heldout(test,train))
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
    frequency=per_relation_frequency_baseline(train,universe,questions,known)
    paired=paired_path_frequency_rank_audit(cases,frequency)
    return {
        "schema":SCHEMA,
        "source_owner":original.ORIGIN,
        "source_commit":original.COMMIT,
        "frozen_selection_protocol":selection,
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
        "per_relation_frozen_failure_diagnostics":per_relation_failure_diagnostics(cases,len(universe)),
        "original_train_frequency_baseline":frequency,
        "frozen_path_vs_train_frequency_paired_audit":paired,
        "cases":cases,
    }


def main():
    p=argparse.ArgumentParser()
    for key in ("train","test","valid","output"):
        p.add_argument("--"+key,type=Path,required=True)
    p.add_argument("--selection",choices=("original","d2_untouched"),default="original")
    args=p.parse_args()
    result=run(train_file=args.train,test_file=args.test,valid_file=args.valid,selection=args.selection)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"selection":result["frozen_selection_protocol"],
                      "n":result["A_B_source_label_filtered"]["n"],
                      "entity_candidates":result["original_source_entities_from_all_splits"],
                      "filtered":result["A_B_source_label_filtered"],
                      "unfiltered":result["A_B_raw_unfiltered"],
                      "train_frequency":{key:value for key,value in
                        result["original_train_frequency_baseline"].items()
                        if key!="individual_case_diagnostics"},
                      "NIH_completed":False},sort_keys=True))

if __name__=="__main__":
    main()
