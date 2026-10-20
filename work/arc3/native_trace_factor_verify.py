"""Separate verifier of preregistered LS20 depth and visible-factor predictions.

Reads actual SDK trajectory metadata and raw frames, not collector assertions.
Always writes outcomes before returning nonzero for a falsified hypothesis.
"""
from __future__ import annotations
import argparse
from hashlib import blake2b,sha256
import json
from pathlib import Path
import numpy as np
from .native_trace_factor_prediction import (
    PROTOCOL,NATIVE_WORDS,HELD_OUT_DEPTHS,GLYPH_COLORS,predicted_trace
)
from .native_observation_bridge import frame_summary

def evaluate(proposal:dict,record:dict,arrays:np.lib.npyio.NpzFile)->dict:
    if (proposal.get("protocol")!=PROTOCOL or
        proposal.get("committed_holdout_words")!=list(NATIVE_WORDS) or
        proposal.get("held_out_depths")!=list(HELD_OUT_DEPTHS) or
        record.get("kind")!="AB_LS20_REAL_NATIVE_HOLDOUT_RAW_FRAMES_V1" or
        record.get("protocol")!=PROTOCOL or record.get("game")!="ls20" or
        record.get("declared_words")!=list(NATIVE_WORDS) or
        set(arrays.files)!=set(NATIVE_WORDS)):
        raise ValueError("unrecognized or incomplete preregistered holdout sources")
    rows=record.get("native_paths")
    if not isinstance(rows,list) or len(rows)!=len(NATIVE_WORDS):
        raise ValueError("missing native paths")
    roots=set()
    predictions=[]
    factor_witnesses=[]
    glyph_to_frames={}
    time_counts={}
    complete=0
    actions=0
    for word,row in zip(NATIVE_WORDS,rows):
        if (type(row) is not dict or row.get("word")!=word or
            not isinstance(row.get("states"),list)):
            raise ValueError("source trajectory metadata disagrees with frozen word")
        states=row["states"]
        grid=arrays[word]
        if grid.ndim!=3 or grid.shape!=(len(word)+1,64,64) or grid.dtype!=np.uint8:
            raise ValueError("missing or malformed raw native frames")
        if len(states)!=len(word)+1:
            raise ValueError("missing native state sequence")
        if (row.get("completed") is not True or row.get("interruption") is not None or
            row.get("steps")!=len(word) or
            any(r.get("levels_completed")!=states[0].get("levels_completed") for r in states)):
            raise ValueError("native path was interrupted or level changed")
        complete+=1
        actions+=len(word)
        for depth,frame in enumerate(grid):
            state=states[depth]
            if (state.get("index")!=depth or
                state.get("action")!=(None if depth==0 else int(word[depth-1])) or
                state.get("observation")!=frame_summary(frame)):
                raise ValueError("native raw frame is inconsistent with snapshot")
            if depth==0:roots.add(frame_summary(frame)["whole"])
            if depth not in HELD_OUT_DEPTHS:continue
            exact=bool(np.array_equal(frame==11,predicted_trace(depth)))
            actual=int(np.count_nonzero(frame==11))
            time_counts[depth]=time_counts.get(depth,0)+1
            predictions.append({
                "word":word,"depth":depth,
                "trace_exact_match":exact,"actual_trace_cells":actual,
                "predicted_trace_cells":int(np.count_nonzero(predicted_trace(depth))),
                "raw_native_whole_sha16":frame_summary(frame)["whole"],
            })
            key=(depth,np.isin(frame,GLYPH_COLORS).tobytes())
            seen=glyph_to_frames.setdefault(key,(word,frame.tobytes()))
            if seen[0]!=word:
                factor_witnesses.append({
                    "depth":depth,"first_word":seen[0],"second_word":word,
                    "same_native_glyph_mask":True,
                    "same_full_visible_frame":seen[1]==frame.tobytes(),
                })
    if (complete!=len(NATIVE_WORDS) or
        not record.get("all_roots_identical") or
        len(roots)!=1 or record.get("root_hashes")!=sorted(roots) or
        actions!=record.get("native_actions") or
        time_counts.get(5)!=len(NATIVE_WORDS) or
        time_counts.get(6)!=sum(len(w)>=6 for w in NATIVE_WORDS)):
        raise ValueError("native evidence did not cover the registered holdout")
    trace_pass=all(row["trace_exact_match"] for row in predictions)
    factor_pass=all(row["same_full_visible_frame"] for row in factor_witnesses)
    return {
        "kind":"AB_NATIVE_TRACE_GLYPH_HELDOUT_VERDICT_V1",
        "word_count":len(NATIVE_WORDS),
        "actions":actions,"root_sha16":next(iter(roots)),
        "held_out_trace_evaluations":len(predictions),
        "trace_predicted_exact":sum(row["trace_exact_match"] for row in predictions),
        "trace_hypothesis_passed":trace_pass,
        "same_glyph_depth_cross_trajectory_comparisons":len(factor_witnesses),
        "same_glyph_implies_same_full_frame_passed":factor_pass if factor_witnesses else None,
        "glyph_factor_test_has_nonvacuous_pairs":bool(factor_witnesses),
        "per_word_trace":predictions,"glyph_factor_witnesses":factor_witnesses,
        "all_predictions_held_out":True,
        "hidden_state_equivalence":False,
        "F3_projection_established":False,
        "game_solved":False,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--prediction",type=Path,required=True)
    p.add_argument("--native",type=Path,required=True)
    p.add_argument("--raw",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    proposal=json.loads(a.prediction.read_text())
    record=json.loads(a.native.read_text())
    with np.load(a.raw,allow_pickle=False) as archive:
        result=evaluate(proposal,record,archive)
    result["sources_sha256"]={
        "frozen_prediction":sha256(a.prediction.read_bytes()).hexdigest(),
        "real_native_manifest":sha256(a.native.read_bytes()).hexdigest(),
        "real_native_raw_frames":sha256(a.raw.read_bytes()).hexdigest(),
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2)+"\n")
    print("AB_NATIVE_OUT_OF_SAMPLE_VERDICT "+json.dumps({
        "predictions_checked":result["held_out_trace_evaluations"],
        "trace_correct":result["trace_predicted_exact"],
        "trace_pass":result["trace_hypothesis_passed"],
        "glyph_pairs":result["same_glyph_depth_cross_trajectory_comparisons"],
        "glyph_pass":result["same_glyph_implies_same_full_frame_passed"]},sort_keys=True))
    if not result["trace_hypothesis_passed"] or result["same_glyph_implies_same_full_frame_passed"] is False:
        raise SystemExit("FALSIFIED native visible prediction; verified raw observations retained")
if __name__=="__main__":
    main()
