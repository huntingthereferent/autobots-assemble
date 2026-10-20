"""Audit independent LS20 native raw frames; never coerce them into F3 states."""
from __future__ import annotations
import argparse
from hashlib import blake2b, sha256
import json
from pathlib import Path
import numpy as np
from work.arc_like_maze.math import inverse_candidates

PREFIXES=(("34","43",True),("23","32",True),("12","21",False))
HISTORICAL_SUFFIXES=("1","2","3","4","12","21")
NEW_SUFFIXES=("11","22","31","42")
KIND="ARC3_NATIVE_VISIBLE_STATE_SUFFIX_DISCRIMINATION"

def _hash(data:bytes)->str:
    return blake2b(data,digest_size=16).hexdigest()

def frame_summary(g:np.ndarray)->dict:
    if not isinstance(g,np.ndarray) or g.shape!=(64,64) or g.dtype!=np.uint8:
        raise ValueError("requires original uint8 64x64 native pixels")
    return {"whole":_hash(g.tobytes()),
            "glyph":_hash(np.isin(g,(9,12)).astype(np.uint8).tobytes()),
            "trace":_hash((g==11).astype(np.uint8).tobytes()),
            "glyph_by_color":{str(c):_hash((g==c).astype(np.uint8).tobytes())
                              for c in (9,12)},
            "trace_cells":int(np.count_nonzero(g==11))}

def audit(native:dict,raw:np.lib.npyio.NpzFile,*,kind:str)->dict:
    if kind not in ("historical","new"):raise ValueError("unknown observation protocol")
    suffixes=HISTORICAL_SUFFIXES if kind=="historical" else NEW_SUFFIXES
    if (type(native) is not dict or native.get("kind")!=KIND or
        native.get("game")!="ls20" or
        tuple(tuple(v) for v in native.get("predeclared_prefixes",()))!=PREFIXES or
        tuple(native.get("predeclared_suffixes",()))!=suffixes or
        native.get("all_runs_start_at_identical_root_frame") is not True):
        raise ValueError("native source game, root or predeclared action words invalid")
    if kind=="new" and native.get("protocol")!="AB_LS20_INDEPENDENT_SUFFIX_V2":
        raise ValueError("unrecognized new protocol")
    rows=native.get("comparisons")
    expected_rows=[(a,b,eq,s) for a,b,eq in PREFIXES for s in suffixes]
    if type(rows) is not list or len(rows)!=len(expected_rows):
        raise ValueError("missing native comparisons")
    keys=set()
    roots=set()
    counts={}
    reports=[]
    actions=0
    for record,(a,b,eq,suffix) in zip(rows,expected_rows):
        if (type(record) is not dict or
            record.get("prefix_pair")!=[a,b] or record.get("suffix")!=suffix or
            record.get("previous_relation")!=("VISIBLE_EQUAL" if eq else "VISIBLE_UNEQUAL")):
            raise ValueError("native comparison or word order changed")
        original=record.get("comparison")
        if type(original) is not dict or "status" in original:
            raise ValueError("incomplete native comparison")
        endpoints=[]
        for side,word in (("a",a+suffix),("b",b+suffix)):
            name=a+"_"+b+"_suffix_"+suffix+"_"+side
            keys.add(name)
            run=record.get("native_left" if side=="a" else "native_right")
            if (type(run) is not dict or run.get("completed") is not True or
                run.get("interruption") is not None or
                run.get("word")!=word or run.get("steps")!=len(word)):
                raise ValueError("native input trajectory incomplete or changed")
            states=run.get("states")
            if not isinstance(states,list) or len(states)!=len(word)+1 or name not in raw.files:
                raise ValueError("native raw pixels/states missing")
            frames=raw[name]
            if frames.shape!=(len(word)+1,64,64) or frames.dtype!=np.uint8:
                raise ValueError("native raw frame encoding/dimensions changed")
            level=states[0].get("levels_completed")
            if type(level) is not int:raise ValueError("missing level")
            for i,item in enumerate(states):
                if (type(item) is not dict or item.get("index")!=i or
                    item.get("action")!=(None if i==0 else int(word[i-1])) or
                    item.get("levels_completed")!=level or
                    item.get("observation")!=frame_summary(frames[i])):
                    raise ValueError("native reported snapshot disagrees with raw pixels")
            roots.add(states[0]["observation"]["whole"])
            endpoints.append((states[len(a)]["observation"],states[-1]["observation"]))
            actions+=len(word)
        (pl,fl),(pr,fr)=endpoints
        before=pl["whole"]==pr["whole"]
        after=fl["whole"]==fr["whole"]
        status=("VISIBLE_EQUAL_PREFIX_SPLIT_BY_SAME_SUFFIX" if before and not after
                else "VISIBLE_EQUAL_PREFIX_PRESERVED_ONE_SUFFIX" if before
                else "VISIBLE_UNEQUAL_PREFIX_CONVERGED_ONE_SUFFIX" if after
                else "VISIBLE_UNEQUAL_PREFIX_REMAINS_UNEQUAL")
        recomputed={
          "previously_observed_prefix_relation_reproduced":before==eq,
          "observed_equal_prefix_frames":before,
          "observed_equal_suffix_frames":after,
          "observed_equal_suffix_glyph_masks":fl["glyph"]==fr["glyph"],
          "observed_equal_suffix_trace_masks":fl["trace"]==fr["trace"],
          "left_prefix_frame":pl["whole"],"right_prefix_frame":pr["whole"],
          "left_after_frame":fl["whole"],"right_after_frame":fr["whole"],
          "classification":status}
        if original!=recomputed or before!=eq:
            raise ValueError("native source relation could not be reproduced")
        counts[status]=counts.get(status,0)+1
        reports.append({"native_prefix":[a,b],"suffix":suffix,
                        "visible_equal_before":before,"visible_equal_after":after,
                        "classification":status,
                        "left_frame_sha16":fl["whole"],"right_frame_sha16":fr["whole"],
                        "hidden_state_equality_observed":False})
    if (set(raw.files)!=keys or len(roots)!=1 or
        sorted(roots)!=native.get("distinct_native_root_hashes") or
        actions!=native.get("native_actions_including_independent_repetitions") or
        counts!=native.get("classification_counts")):
        raise ValueError("raw source archive incomplete or inconsistent")
    laws=inverse_candidates()
    if len(laws)!=9:raise AssertionError("F3 source no longer has nine laws")
    comparable=[]
    for row in reports:
        if row["native_prefix"]!=["12","21"] or not set(row["suffix"])<={"1","2"}:
            continue
        suffix=row["suffix"].replace("1","A").replace("2","B")
        distinct=sum(w.apply("AB"+suffix)!=w.apply("BA"+suffix) for w in laws)
        if distinct!=9:raise AssertionError("original F3 permutation law changed")
        comparable.append({"suffix":row["suffix"],
                          "distinct_F3_endpoints":distinct,
                          "native_visible_convergence":row["visible_equal_after"],
                          "direct_injective_visible_F3_obstructed":row["visible_equal_after"]})
    return {"kind":"AB_NATIVE_VISIBLE_EVIDENCE_AUDIT_V1",
            "dataset":kind,"environment":"actual native LS20; archived/raw verified",
            "native_actions":actions,"separate_reset_trajectories":len(keys),
            "comparisons":reports,"visible_classification_counts":counts,
            "native_root_frame_sha16":next(iter(roots)),
            "conditional_A1_A_A2_B_F3_comparisons":comparable,
            "admitted_evidence_contract":{
                "native_visible_frame_equality":True,
                "native_hidden_state_equality":False,
                "F3_full_state_endpoint":False,
                "window48_fixed_word_state_count":False,
                "window48_rooted_word_equality":False},
            "source_boundary":"Full native visible frames are not mathematical F3 state; unproved injective mappings cannot transfer observations.",
            "arc_game_solved":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--native",type=Path,required=True)
    p.add_argument("--raw",type=Path,required=True)
    p.add_argument("--dataset",choices=("historical","new"),required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    source=a.native.read_bytes()
    with np.load(a.raw,allow_pickle=False) as raw:
        result=audit(json.loads(source),raw,kind=a.dataset)
    result["source_provenance"]={
        "record_json_sha256":sha256(source).hexdigest(),
        "record_frames_npz_sha256":sha256(a.raw.read_bytes()).hexdigest()}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2)+"\n")
    print("AB_VERIFIED_NATIVE_VISIBLE "+json.dumps({
        "dataset":a.dataset,"actions":result["native_actions"],
        "paired_comparisons":len(result["comparisons"]),
        "observed_visible_convergences":sum(r["classification"]=="VISIBLE_UNEQUAL_PREFIX_CONVERGED_ONE_SUFFIX" for r in result["comparisons"]),
        "direct_visible_F3_obstructions":sum(r["direct_injective_visible_F3_obstructed"] for r in result["conditional_A1_A_A2_B_F3_comparisons"]),
        "admitted_native_to_F3_mapping":False},sort_keys=True))

if __name__=="__main__":main()
