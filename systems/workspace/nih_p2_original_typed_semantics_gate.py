"""Source-owner PharmKG relation/vocabulary evidence audit before typed rules.

An original README naming broad gene/disease/chemical groups is not a mapping
from each opaque vertex ID to an authenticated class, nor from GG/T/P/I codes
to justified clinical inference. This trial measures exact TRAIN-only graph
roles and deliberately refuses to claim a semantic type rule without the
additional owner-backed mapping. No TEST/VALID content is read here.
"""
from __future__ import annotations

import argparse
from collections import Counter,defaultdict
from hashlib import sha256
from pathlib import Path
import json

from . import nih_p2_external_pharmkg_heldout_trial as source

SCHEMA="nih-p2-pharmkg-source-role-profile-and-type-evidence-gate-v1"
OWNER_README_BLOB="d166875b9345729bc28de3b078af6479f167d255"
CODES=("GG","T","P","I")


def original_overview(raw:bytes):
    if type(raw) is not bytes or source.git_blob_sha1(raw)!=OWNER_README_BLOB:
        raise ValueError("immutable original source-owner README blob mismatch")
    text=raw.decode("utf8")
    if not all(name in text for name in ("Chemical","Disease","Gene","PharmKG-8k")):
        raise ValueError("original biomedical source overview changed")
    return {
        "owner":"biomed-AI/PharmKG",
        "source_commit":source.COMMIT,
        "README_git_blob_sha1":OWNER_README_BLOB,
        "published_overview_mentions_broad_entity_classes":["Chemical","Disease","Gene"],
        "identities_for_each_cleaned_TSV_entity_authenticated_here":False,
        "semantically_justified_predicate_composition_authenticated_here":False,
    }


def profile(rows):
    if type(rows) is not list:
        raise ValueError("deduplicated original training triples required")
    # First implementation: per-predicate pair source scan.
    by_rel=defaultdict(list)
    for item in rows:
        if (type(item) is not tuple or len(item)!=3 or
                any(type(s) is not str or not s for s in item)):
            raise ValueError("malformed owner-source triple")
        by_rel[item[1]].append((item[0],item[2]))
    observed={}
    for code in CODES:
        pairs=by_rel[code]
        heads={h for h,t in pairs}
        tails={t for h,t in pairs}
        observed[code]={
            "training_source_edges":len(pairs),
            "distinct_head_identifiers":len(heads),
            "distinct_tail_identifiers":len(tails),
            "source_identifiers_seen_as_both_roles":len(heads&tails),
        }
    # Independent direct source replay with separate counters and role sets.
    count=Counter(t[1] for t in rows)
    for code in CODES:
        unique_head=set()
        unique_tail=set()
        for h,rel,t in rows:
            if rel==code:
                unique_head.add(h)
                unique_tail.add(t)
        if observed[code] != {
            "training_source_edges":count[code],
            "distinct_head_identifiers":len(unique_head),
            "distinct_tail_identifiers":len(unique_tail),
            "source_identifiers_seen_as_both_roles":len(unique_head&unique_tail),
        }:
            raise ValueError("independent per-relation original-source profile disagrees")
    return observed


def cross_relation_role_overlap(rows):
    """Source-only directed overlap: TRAIN identifier roles, never clinical types.

    The independent oracle reconstructs every set by a separate exhaustive
    input scan. No TEST or VALID row can supply a role or a class label.
    """
    if not rows or type(rows) is not list:
        raise ValueError("original training triples are required")
    if any(type(t) is not tuple or len(t)!=3 or t[1] not in CODES
           or any(type(v) is not str or not v for v in t) for t in rows):
        raise ValueError("unknown predicate or malformed source role input")
    role_sets = {}
    for code in CODES:
        role_sets[(code,"head")]={h for h,r,t in rows if r==code}
        role_sets[(code,"tail")]={t for h,r,t in rows if r==code}
    # Independently encode role membership as per-identifier bit flags,
    # not quadratic pairs of source rows.
    from collections import defaultdict
    membership=defaultdict(int)
    code_bits={r:1 << (2*i) for i,r in enumerate(CODES)}
    for head,relation,tail in rows:
        bit=code_bits[relation]
        membership[head] |= bit
        membership[tail] |= bit << 1
    out={}
    for code_a in CODES:
        for role_a in ("head","tail"):
            for code_b in CODES:
                for role_b in ("head","tail"):
                    key=f"{code_a}:{role_a}|{code_b}:{role_b}"
                    n=len(role_sets[(code_a,role_a)] & role_sets[(code_b,role_b)])
                    bit_a=code_bits[code_a] << (role_a=="tail")
                    bit_b=code_bits[code_b] << (role_b=="tail")
                    independent=sum(bool(flags & bit_a) and bool(flags & bit_b)
                                    for flags in membership.values())
                    if n!=independent:
                        raise ValueError("independent original TRAIN role scan differs")
                    out[key]=n
    return {
        "original_train_unique_source_identifiers":len(
            {x for h,r,t in rows for x in (h,t)}),
        "directed_relation_role_overlap_counts":out,
        "authenticated_entity_class_labels_from_roles":False,
        "valid_or_test_labels_used":False,
        "original_source_relation_directions_are_semantically_proven":False,
    }


def execute(*,readme_file:Path,train_file:Path):
    owner=original_overview(readme_file.read_bytes())
    train,train_id=source.read_source(train_file,"train.tsv")
    output=profile(train)
    if any(output[c]["training_source_edges"]==0 for c in CODES):
        raise ValueError("expected original source relation category missing")
    return {
        "schema":SCHEMA,
        "original_owner_metadata":owner,
        "entire_original_train_source_identity":train_id,
        "training_only_relation_code_profile":output,
        "training_only_cross_relation_source_roles":cross_relation_role_overlap(train),
        "original_training_source_unique_rows":len(train),
        "independent_count_verification":"PASS",
        "external_owner_semantic_entity_id_mapping":"UNAVAILABLE_FROM_PINNED_README_AND_TRAIN_TSV",
        "type_grounded_metapath_rule_admission":"REFUSED_MISSING_SOURCE_OWNER_SEMANTICS",
        "clinical_biomedical_entailment_authenticated":False,
        "test_and_valid_used":False,
        "historical_edge_publication_times_known":False,
        "original_W13_modified":False,
        "official_NIH_benchmark":False,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--readme",required=True,type=Path)
    p.add_argument("--train",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    a=p.parse_args()
    result=execute(readme_file=a.readme,train_file=a.train)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "relation_edges":result["training_only_relation_code_profile"],
        "semantic_admission":result["type_grounded_metapath_rule_admission"],
        "NIH_complete":False,
    },sort_keys=True))


if __name__=="__main__":
    main()
