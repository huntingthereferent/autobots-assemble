"""Lane A2: read-only original author CSV-to-clean TRAIN type metadata audit.

A source-owned raw csv is an *external input*, not a typed proof by itself.
No TRAIN/TEST labels enter rules or link prediction. No raw rows distributed.
"""
from __future__ import annotations
import argparse, csv, json, re
from collections import defaultdict, Counter
from hashlib import sha1, sha256
from pathlib import Path
from . import nih_p2_external_pharmkg_heldout_trial as source

SCHEMA = "nih-p2-pharmkg-original-csv-train-id-type-reconciliation-v1"
ORIGINAL_RAW_GIT_BLOB = "7ac5b6d87a7d183566229592fb411b5dc9a9742e"
MAX_BYTES = 27000000
MAX_ROWS = 600000
ORIGINAL_OWNER_PREPROCESS_BLOB="8fc71ebd0a90c81ac7e6b5b89185374ee281bfc9"

def original_preprocess_source_projection(raw):
    """Authenticate author preprocessing contract; never run untrusted source."""
    import ast
    if not isinstance(raw,bytes) or source.git_blob_sha1(raw)!=ORIGINAL_OWNER_PREPROCESS_BLOB:
        raise ValueError("author preprocessing source blob does not match")
    tree=ast.parse(raw.decode("utf-8"))
    projections=[]
    for node in ast.walk(tree):
        if not isinstance(node,ast.Subscript) or not isinstance(node.value,ast.Name) or node.value.id!="df":
            continue
        sl=node.slice
        if isinstance(sl,(ast.List,ast.Tuple)):
            values=[x.value for x in sl.elts if isinstance(x,ast.Constant)]
            if len(values)==len(sl.elts) and len(values)==3:
                projections.append(values)
    exact=["Entity1_ID","relation","Entity2_ID"]
    if projections.count(exact)!=1:
        raise ValueError("source-owned direct CSV projection was not found uniquely")
    return {
        "owner_preprocess_git_blob_sha1":ORIGINAL_OWNER_PREPROCESS_BLOB,
        "direct_raw_projection_fields":exact,
        "author_pipeline_source_proven":True,
        "published_clean_split_lineage_proven":False,
        "raw_ID_crosswalk_documented_in_author_pipeline":False,
    }


def normalized(value):
    return re.sub(r"[^a-z0-9]", "", value.casefold())
def reconcile(reader, train):
    cols = tuple(reader.fieldnames or ())
    byname = {normalized(name):name for name in cols}
    must = ("entity1id", "relation", "entity2id")
    if any(k not in byname for k in must):
        raise ValueError("original author CSV lacks preprocessing source ID/predicate columns")
    core = [byname[k] for k in must]
    types = [byname.get("entity1type"), byname.get("entity2type")]
    train_set=set(train)
    if len(train_set)!=len(train):
        raise ValueError("original TRAIN contains repeated source triples")
    matched=set()
    clean_ids={node for h,r,t in train for node in (h,t)}
    clean_pairs={(h,t) for h,r,t in train}
    raw_id_intersection=set()
    raw_relation_counts=Counter()
    raw_author_type_pairs=Counter()
    raw_author_relation_type_pairs=Counter()
    raw_unknown_type_rows=0
    clean_relation_counts=Counter(r for h,r,t in train)
    raw_pairs_matching_clean=0
    class_by_id=defaultdict(set)
    source_rows=0
    source_matched_rows=0
    for row in reader:
        source_rows+=1
        if source_rows>MAX_ROWS:raise ValueError("source row limit exceeded")
        t=tuple(row.get(k, "") for k in core)
        raw_relation_counts[t[1]]+=1
        if all(types):
            left=(row.get(types[0]) or "").strip()
            right=(row.get(types[1]) or "").strip()
            if left and right:
                raw_author_type_pairs[(left,right)]+=1
                raw_author_relation_type_pairs[(t[1],left,right)]+=1
            else:
                raw_unknown_type_rows+=1
        else:
            raw_unknown_type_rows+=1
        raw_id_intersection.update(node for node in (t[0],t[2]) if node in clean_ids)
        raw_pairs_matching_clean += (t[0],t[2]) in clean_pairs
        if t not in train_set:
            continue
        source_matched_rows+=1
        matched.add(t)
        for id_pos,label_col in ((0,types[0]),(2,types[1])):
            if label_col:
                label=(row.get(label_col) or "").strip()
                if label:
                    class_by_id[t[id_pos]].add(label)
    seen={val for head,rel,tail in train for val in (head,tail)}
    coherent={key for key in seen if len(class_by_id.get(key,()))==1}
    conflict={key for key in seen if len(class_by_id.get(key,()))>1}
    if len(coherent)+len(conflict)>len(seen):raise ValueError("ID type partition invalid")
    return {
        "source_original_csv_header_names":list(cols),
        "source_original_csv_rows":source_rows,
        "original_raw_relation_code_counts":dict(sorted(raw_relation_counts.items())),
        "raw_author_relation_and_type_pair_counts":[
            {"raw_source_relation_code":rel,"source_head_type":head,"source_tail_type":tail,
             "source_raw_row_count":count}
            for (rel,head,tail),count in sorted(raw_author_relation_type_pairs.items())
        ],
        "raw_author_type_pair_counts":[
            {"source_head_type":head,"source_tail_type":tail,"source_raw_row_count":count}
            for (head,tail),count in sorted(raw_author_type_pairs.items())
        ],
        "raw_author_rows_without_both_type_fields":raw_unknown_type_rows,
        "raw_author_type_pairs_are_not_cleaned_8k_semantics":True,
        "no_clean_train_id_type_mapping_inferred":True,
        "original_clean_train_relation_code_counts":dict(sorted(clean_relation_counts.items())),
        "original_raw_entity_identifiers_seen_in_clean_train":len(raw_id_intersection),
        "original_raw_subject_object_pairs_matching_clean_train":raw_pairs_matching_clean,
        "source_original_rows_matching_train":source_matched_rows,
        "distinct_authored_raw_triples_matching_original_train":len(matched),
        "original_train_triples":len(train_set),
        "original_train_unmatched_triples":len(train_set-matched),
        "original_train_entity_identifiers":len(seen),
        "original_train_entity_ids_with_one_raw_type":len(coherent),
        "original_train_entity_ids_with_conflicting_raw_types":len(conflict),
        "original_train_entity_ids_without_raw_type":len(seen)-len(coherent)-len(conflict),
        "original_raw_entity_type_columns_present":all(types),
        "type_metadata_join_is_train_edge_scoped":True,
        "test_or_valid_label_used_for_model":False,
        "typed_biomedical_path_rule_admitted":False,
        "full_entity_semantic_type_validation_proven":False,
        "original_train_coverage_digest":sha256("\n".join(sorted("\t".join(t) for t in matched)).encode()).hexdigest(),
    }
def audit(raw_path,train_path,preprocess_path=None):
    raw=Path(raw_path).read_bytes()
    if len(raw)>MAX_BYTES or source.git_blob_sha1(raw)!=ORIGINAL_RAW_GIT_BLOB:
        raise ValueError("original raw author CSV Git blob mismatch")
    train,receipt=source.read_source(train_path,"train.tsv")
    from io import StringIO
    report=reconcile(csv.DictReader(StringIO(raw.decode("utf-8-sig"))),train)
    if preprocess_path is not None:
        report["author_original_preprocessing_contract"]=original_preprocess_source_projection(
            Path(preprocess_path).read_bytes())
    report.update({"schema":SCHEMA,"original_raw_git_blob":ORIGINAL_RAW_GIT_BLOB,
                   "original_train_blob":receipt["git_blob_sha1"],
                   "original_source_commit":source.COMMIT,
                   "original_raw_sha256":sha256(raw).hexdigest(),
                   "source_input_authenticated":True,"official_NIH_benchmark":False,
                   "original_W13_modified":False})
    return report
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--raw",required=True,type=Path)
    p.add_argument("--train",required=True,type=Path)
    p.add_argument("--preprocess",type=Path)
    p.add_argument("--output",required=True,type=Path)
    a=p.parse_args()
    result=audit(a.raw,a.train,preprocess_path=a.preprocess)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:result[k] for k in
          ("source_original_csv_rows","original_train_triples",
           "distinct_authored_raw_triples_matching_original_train",
           "original_raw_entity_identifiers_seen_in_clean_train",
           "original_raw_subject_object_pairs_matching_clean_train",
           "original_raw_entity_type_columns_present",
           "original_train_entity_ids_with_one_raw_type",
           "original_train_entity_ids_with_conflicting_raw_types",
           "official_NIH_benchmark")},sort_keys=True))
if __name__=="__main__":
    main()
