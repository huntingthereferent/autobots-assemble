"""Original PharmKG-8K HELD-OUT biomedical triple evaluation.

Source owner published fixed train/test splits. Test edges are NEVER added to
training graph; no answer may be read from held-out targets by the A/B
predictor. This is a biomedical *link-prediction proxy*, NOT temporal
reasoning or proof that two-hop/three-hop paths imply biomedical relationships.
Compare a capable independent static 3-hop graph reasoner, and report no
temporal win when authentic event-time labels are absent.

All original dataset bodies are read-only and excluded from output/artifacts.
"""
from __future__ import annotations

from collections import Counter,defaultdict,deque
from hashlib import sha1,sha256
from pathlib import Path
from random import Random
import argparse
import json

from . import ab_heldout_biomedical_relation_paths as ab

SCHEMA="nih-p2-original-pharmkg-heldout-source-link-trial/v1"
ORIGIN="biomed-AI/PharmKG"
COMMIT="a7daec6b4d6c785c157b8cf693a4651756cb8647"
SOURCE_FILES={
    "train.tsv":"9047084dd741eab80499c19a5d11d80143d99906",
    "test.tsv":"6f842d19d8fd49017335ac71e2e7e9479ed75595",
    "valid.tsv":"1f82ceb4ac9b1eb4b8f9c98dccb531553501f4977",
}
# Frozen selection before observing source-specific model performance.
RELATIONS=("GG","T","P","I")
PER_RELATION=16
CONTROLS=8
SEED=26022
MAX_TSV_ROWS=500000


def git_blob_sha1(raw):
    return sha1(b"blob "+str(len(raw)).encode()+b"\x00"+raw).hexdigest()


def read_source(p,name):
    if name not in SOURCE_FILES:raise ValueError("not an original selected owner file")
    raw=Path(p).read_bytes()
    if git_blob_sha1(raw)!=SOURCE_FILES[name]:
        raise ValueError("original source bytes do not match Git owner object SHA1")
    rows=[]
    seen=set()
    for line in raw.decode("utf-8-sig").splitlines():
        parts=line.split("\t")
        if len(parts)!=3 or any(not x or len(x)>256 for x in parts):
            raise ValueError("invalid original biomedical triple row")
        triple=tuple(parts)
        if triple in seen:raise ValueError("original study source contains duplicate statement")
        seen.add(triple)
        rows.append(triple)
        if len(rows)>MAX_TSV_ROWS:raise ValueError("source exceeded finite declared benchmark")
    if not rows:raise ValueError("original owner data missing")
    return rows,{"source_file":name,"git_blob_sha1":SOURCE_FILES[name],
                 "raw_sha256":sha256(raw).hexdigest(),"rows":len(rows),
                 "original_owner":ORIGIN,"commit":COMMIT}


def static_shortest_path(index,head,relation,tail,max_hops=3):
    """Independent graph search; not a call into the A/B source witness."""
    if tail in index["forward"].get(relation,{}).get(head,set()):
        return 1
    adjacency=index["forward"].get(relation,{})
    work=deque([(head,0)])
    visited={head}
    while work:
        node,depth=work.popleft()
        if depth>=max_hops:continue
        for child in adjacency.get(node,()):
            if child==tail:return depth+1
            if child not in visited:
                visited.add(child)
                work.append((child,depth+1))
    return None


def candidate_score(hops):
    return 0 if hops is None else 1/hops


def rank_scores(rows,actual_index=0):
    # Tie-aware average rank avoids benefiting from arbitrary ID ordering.
    target=rows[actual_index]
    earlier=sum(x>target for x in rows)
    equal=sum(x==target for x in rows)
    return 1+earlier+(equal-1)/2


def select_test(test_rows,training):
    tr=set(training)
    selected=[]
    included=set()
    for rel in RELATIONS:
        choices=sorted(
            [row for row in test_rows if row[1]==rel and row not in tr],
            key=lambda t:(sha256(("\t".join(t)+"|heldout|26022").encode()).hexdigest(),t)
        )
        if len(choices)<PER_RELATION:
            raise ValueError("insufficient distinct external heldout positives for relation "+rel)
        selected.extend(choices[:PER_RELATION])
        included.update(choices[:PER_RELATION])
    if len(selected)!=len(included):raise ValueError("heldout queries duplicated")
    return selected


def controls_for(query,all_tail_by_relation,train_set,test_set,rng):
    head,rel,tail=query
    options=list(all_tail_by_relation[rel])
    if len(options)<CONTROLS+2:raise ValueError("missing original relation-tail alternatives")
    controls=[]
    used={tail}
    for _ in range(500):
        other=options[rng.randrange(len(options))]
        test=(head,rel,other)
        if (other not in used and test not in train_set and test not in test_set):
            used.add(other)
            controls.append(other)
            if len(controls)==CONTROLS:break
    if len(controls)!=CONTROLS:raise ValueError("not enough distinct unlabeled candidate tails")
    return controls


def execute(*,train_file,test_file,valid_file):
    train,train_id=read_source(train_file,"train.tsv")
    test,test_id=read_source(test_file,"test.tsv")
    valid,valid_id=read_source(valid_file,"valid.tsv")
    # No validation/test source statements are admitted to the graph.
    indexed=ab.build(train)
    training=set(train)
    tests=set(test)
    positives=select_test(test,train)
    tail_by_type=defaultdict(set)
    for _,r,t in train:
        if r in RELATIONS:tail_by_type[r].add(t)
    for _,r,t in test:
        if r in RELATIONS:tail_by_type[r].add(t)
    tails={r:sorted(v) for r,v in tail_by_type.items()}
    rng=Random(SEED)
    results=[]
    for head,rel,tail in positives:
        choices=[tail]+controls_for((head,rel,tail),tails,training,tests,rng)
        candidate_results=[]
        for x in choices:
            new=ab.witness(indexed,head=head,relation=rel,tail=x,max_hops=3)
            static=static_shortest_path(indexed,head,rel,x,3)
            if new["direct_training_edge_exists"]:
                # Controls exclude training but always state this wall explicitly.
                raise ValueError("unintended direct edge in heldout candidate")
            expected_exists=static in (2,3)
            if new["path_exists"]!=expected_exists:
                raise ValueError("independent static 3-hop reasoner disagrees with A/B")
            if new["path_exists"] and new["source_path_hops"]!=static:
                raise ValueError("A/B source witness is not the shortest static path")
            for a,b,h in zip(new["source_path_nodes"],
                             new["source_path_nodes"][1:],
                             new["source_edge_sha256"]):
                if (a,rel,b) not in training or h!=ab.edge_hash(a,rel,b):
                    raise ValueError("fabricated biomedical relationship in source witness")
            candidate_results.append({
                "candidate":x,
                "is_original_test_positive":x==tail,
                "AB_path_hops":new["source_path_hops"],
                "independent_static_path_hops":static,
                "AB_path_exists":new["path_exists"],
                "source_witness_nodes":new["source_path_nodes"],
                "source_witness_edge_sha256":new["source_edge_sha256"],
            })
        vals=[candidate_score(x["AB_path_hops"]) for x in candidate_results]
        static_vals=[candidate_score(x["independent_static_path_hops"])
                     for x in candidate_results]
        rank=rank_scores(vals)
        baseline_rank=rank_scores(static_vals)
        results.append({
            "source_head":head,"source_relation_code":rel,
            "heldout_original_target":tail,
            "test_positive_excluded_from_training":True,
            "unlabeled_controls_not_proven_false":True,
            "heldout_true_relation_inferred_from_path":False,
            "positive_has_alternative_source_path":candidate_results[0]["AB_path_exists"],
            "rank_among_filtered_candidates":rank,
            "independent_static_rank":baseline_rank,
            "candidate_results":candidate_results,
        })
    per_relation={
        r:{
            "cases":sum(x["source_relation_code"]==r for x in results),
            "heldout_positives_with_alternative_source_path":
                sum(x["source_relation_code"]==r and
                    x["positive_has_alternative_source_path"] for x in results),
            "mean_rank":round(
                sum(x["rank_among_filtered_candidates"] for x in results
                    if x["source_relation_code"]==r)/PER_RELATION,4),
        } for r in RELATIONS
    }
    hits1=sum(r["rank_among_filtered_candidates"]<=1 for r in results)
    hits3=sum(r["rank_among_filtered_candidates"]<=3 for r in results)
    stat_hits1=sum(r["independent_static_rank"]<=1 for r in results)
    reciprocal=sum(1/r["rank_among_filtered_candidates"] for r in results)/len(results)
    return {
        "schema":SCHEMA,"source_owner":ORIGIN,"original_source_commit":COMMIT,
        "real_original_split_identity":{
            "train":train_id,"test":test_id,"valid":valid_id,
        },
        "original_training_relation_counts":indexed["original_source_relation_counts"],
        "original_heldout_test_relation_counts":dict(Counter(x[1] for x in test)),
        "source_selection":"frozen_sha256_rank_of_external_test_rows",
        "heldout_relation_codes":list(RELATIONS),"cases_per_relation":PER_RELATION,
        "heldout_test_questions":len(results),
        "unlabeled_candidate_controls_per_question":CONTROLS,
        "AB_link_proxy_hits_at_1":hits1,
        "AB_link_proxy_hits_at_3":hits3,
        "AB_link_proxy_MRR":round(reciprocal,6),
        "independent_full_training_static_3hop_hits_at_1":stat_hits1,
        "source_path_result_mismatches_vs_static_reasoner":0,
        "static_training_graph_fed_test_or_validation_data":False,
        "source_split_is_chronological":False,
        "observed_original_event_known_at":False,
        "patient_level_or_clinical_event_claim":False,
        "source_path_proves_direct_heldout_biomedical_relation":False,
        "unlabeled_control_tails_confirmed_false":False,
        "official_NIH_Phase2_benchmark_reproduced":False,
        "original_W13_journal_modified":False,
        "original_W13_temporal_python_modified":False,
        "World48_required":False,
        "original_external_dataset_bodies_redistributed":False,
        "relation_results":per_relation,
        "case_results":results,
    }


def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument("--train",type=Path,required=True)
    a.add_argument("--test",type=Path,required=True)
    a.add_argument("--valid",type=Path,required=True)
    a.add_argument("--output",type=Path,required=True)
    opt=a.parse_args()
    x=execute(train_file=opt.train,test_file=opt.test,valid_file=opt.valid)
    opt.output.parent.mkdir(parents=True,exist_ok=True)
    opt.output.write_text(json.dumps(x,sort_keys=True,indent=2)+"\n",encoding="utf8")
    print(json.dumps({
        "real_original_heldout_questions":x["heldout_test_questions"],
        "AB_proxy_hits1":x["AB_link_proxy_hits_at_1"],
        "AB_proxy_hits3":x["AB_link_proxy_hits_at_3"],
        "AB_proxy_MRR":x["AB_link_proxy_MRR"],
        "independent_static_hits1":x["independent_full_training_static_3hop_hits_at_1"],
        "original_static_path_disagreements":x["source_path_result_mismatches_vs_static_reasoner"],
        "Phase2_completed":False,
    },sort_keys=True))


if __name__=="__main__":
    main()
