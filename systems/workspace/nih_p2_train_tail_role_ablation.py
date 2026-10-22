"""Original PharmKG TRAIN-tail source-role candidate ablation.

This is a negative/control test for `type` talk, not a biomedical type system.
A source-observed tail-role set can restrict candidate IDs without establishing
gene/drug/disease classes or semantic composition. Test/VALID remain outside
the source graph. Missing gold in TRAIN-tail roles is a coverage failure.
"""
from __future__ import annotations
from collections import defaultdict
from hashlib import sha256
from pathlib import Path
import argparse,json

from . import ab_pharmkg_training_metapath_witness as mixed
from . import nih_p2_pharmkg_frozen_heterogeneous_trial as prior
from . import nih_p2_external_pharmkg_heldout_trial as source

SCHEMA="nih-p2-pharmkg-structural-tail-role-ablation-v1"
SEED="nih-p2-broad-untouched-20261022-v1"
CAP=12000


def independent_new_questions(train,test):
    original_old=set(source.select_test(test,train))
    previously=set(prior.untouched_new_heldout(test,train)[0])
    training=set(train)
    selected=[]
    for r in mixed.RELATIONS:
        viable=sorted((row for row in test if row[1]==r and
                      row not in original_old and row not in previously and
                      row not in training),
                      key=lambda x:(sha256(("\t".join(x)+"|"+SEED).encode()).hexdigest(),x))
        if len(viable)<16:
            raise ValueError("source original untouched question underflow")
        selected.extend(viable[:16])
    if len(set(selected))!=64:
        raise ValueError("source selected test overlap")
    return selected


def score_map(graph,head,patterns):
    scored={}
    for idx,(one,two) in enumerate(patterns,1):
        if one==two:
            raise ValueError("frozen pattern is not heterogeneous")
        for r,mid in graph["forward"].get(head,()):
            if r!=one or mid==head:continue
            for second,dest in graph["forward"].get(mid,()):
                if second==two and dest not in (head,mid):
                    if (head,one,mid) not in graph["triples"] or (
                        mid,two,dest) not in graph["triples"]:
                        raise ValueError("fabricated source movement")
                    scored.setdefault(dest,1/idx)
    return scored


def rank(gold,universe,scores):
    if gold not in universe:
        return None
    k=scores.get(gold,0)
    better=sum(scores.get(t,0)>k for t in universe)
    ties=sum(scores.get(t,0)==k for t in universe)
    if ties<1:
        raise ValueError("rank lost its reference")
    return 1+better+(ties-1)/2


def execute(train_file:Path,test_file:Path,valid_file:Path):
    train,tr_id=source.read_source(train_file,"train.tsv")
    test,te_id=source.read_source(test_file,"test.tsv")
    valid,va_id=source.read_source(valid_file,"valid.tsv")
    rules,calibration=mixed.discover(train,mixed.training_graph(train))
    graph=mixed.training_graph(train)
    static=prior.independent_static_graph(train)
    selected=independent_new_questions(train,test)
    universe=sorted({node for rows in (train,test,valid) for h,r,t in rows
                     for node in (h,t)})
    if not (0<len(universe)<=CAP):
        raise ValueError("original source entity budget exceeded")
    roles=defaultdict(set)
    for _,r,t in train:
        roles[r].add(t)
    cases=[]
    for h,r,gold in selected:
        scores=score_map(graph,h,rules[r])
        witness=mixed.witness(graph,head=h,target_rel=r,tail=gold,
                              frozen_patterns=rules[r])
        if scores.get(gold,0)!=witness["ranking_feature"]:
            raise ValueError("source-owned original A/B witness changed")
        candidate_roles=roles[r]
        if not candidate_roles:
            raise ValueError("source target relation has no TRAIN tail role")
        if len(candidate_roles)>CAP:
            raise ValueError("relation source-tail role budget exceeded")
        mismatches=0
        for t in candidate_roles:
            independent,_=prior.independent_pattern_score(
                static,h,t,rules[r])
            if t==h:independent=0
            mismatches+=independent!=scores.get(t,0)
        if mismatches:
            raise ValueError("TRAIN-role scoring differs from independent static")
        constrained=rank(gold,candidate_roles,scores)
        full=rank(gold,universe,scores)
        cases.append({
            "original_head":h,"original_relation":r,"original_heldout_positive":gold,
            "all_source_entities":len(universe),
            "training_observed_tail_role_count":len(candidate_roles),
            "gold_tail_seen_with_relation_in_train":gold in candidate_roles,
            "all_entities_rank":full,
            "train_tail_role_rank_or_unavailable":constrained,
            "independent_equal_capability_static_score_mismatches":0,
            "witness_original_source_edges":witness["source_edge_triples"],
            "role_is_biological_type":False,
        })
    def summarize(key):
        scored=[i[key] for i in cases]
        available=[v for v in scored if v is not None]
        return {
            "total_questions":len(scored),
            "scorable_questions":len(available),
            "unscorable_gold_outside_source_roles":len(scored)-len(available),
            "hits_at_1_total_denominator":sum(v<=1 for v in available),
            "hits_at_3_total_denominator":sum(v<=3 for v in available),
            "hits_at_10_total_denominator":sum(v<=10 for v in available),
            "MRR_with_unscorable_as_zero":round(sum(1/v for v in available)/len(scored),6),
        }
    return {
        "schema":SCHEMA,"source_owner":source.ORIGIN,
        "source_commit":source.COMMIT,
        "whole_source_files":{"train":tr_id,"test":te_id,"valid":va_id},
        "original_rules_frozen_from_TRAIN_only":calibration,
        "questions_sha256":sha256("\n".join("\t".join(row) for row in selected).encode()).hexdigest(),
        "rank_full_source_entity_universe":summarize("all_entities_rank"),
        "rank_train_observed_relation_tail_role":summarize("train_tail_role_rank_or_unavailable"),
        "source_entity_universe":len(universe),
        "all_questions_have_static_equivalent":True,
        "candidate_restriction_is_source_structural_role_not_biomedical_class":True,
        "published_semantic_composition_verified":False,
        "test_valid_gold_admitted_to_training":False,
        "source_data_has_authenticated_clinical_time":False,
        "official_NIH_benchmark":False,
        "original_W13_modified":False,
        "cases":cases,
    }


def main():
    p=argparse.ArgumentParser()
    for key in ("train","test","valid","output"):
        p.add_argument("--"+key,type=Path,required=True)
    x=p.parse_args()
    result=execute(x.train,x.test,x.valid)
    x.output.parent.mkdir(parents=True,exist_ok=True)
    x.output.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print(json.dumps({
        "full":result["rank_full_source_entity_universe"],
        "role_gated":result["rank_train_observed_relation_tail_role"],
        "source_roles_not_biomedical_types":True,
        "NIH_completed":False},sort_keys=True))


if __name__=="__main__":
    main()
