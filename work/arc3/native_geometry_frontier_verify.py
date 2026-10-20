"""Separate raw-pixel verifier; records falsifications and interruptions as evidence."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import numpy as np
from .native_observation_bridge import frame_summary
from .native_geometry_unknown_edge_verify import position
from .native_geometry_frontier import PROTOCOL

def check(frozen: dict, source: dict, arrays) -> dict:
    trials = frozen.get("source_frozen_trials")
    rows = source.get("native_trials")
    if (frozen.get("kind") != "AB_NATIVE_SOURCE_FROZEN_COMPLETE_FRONTIER_V1" or
        source.get("kind") != "AB_REAL_NATIVE_COMPLETE_FRONTIER_RAW_V1" or
        frozen.get("protocol") != PROTOCOL or source.get("protocol") != PROTOCOL or
        source.get("game") != "ls20" or
        not isinstance(trials,list) or len(trials)!=78 or
        not isinstance(rows,list) or len(rows)!=78 or
        set(arrays.files) != {f"trial_{i:03d}" for i in range(78)}):
        raise ValueError("missing original native source or preregistered trials")
    observations = []
    roots = set()
    pair_results = {}
    interruptions = []
    verified_prefixes = 0
    successes = 0
    for index,(proposal,row) in enumerate(zip(trials,rows)):
        key = f"trial_{index:03d}"
        record = row.get("native_path")
        if (row.get("trial_key")!=key or
            row.get("edge_id")!=proposal["edge_id"] or
            row.get("history")!=proposal["history"] or
            not isinstance(record,dict) or record.get("word")!=proposal["word"]):
            raise ValueError("recorded native path identity changed")
        frames = arrays[key]
        states = record.get("states")
        if (not isinstance(states,list) or frames.dtype!=np.uint8 or
            frames.ndim!=3 or frames.shape[1:]!=(64,64) or
            len(frames)!=len(states)):
            raise ValueError("original native raw pixel source incomplete")
        actual = []
        for depth, (state,frame) in enumerate(zip(states,frames)):
            if (state.get("index")!=depth or
                state.get("action")!=(
                    None if depth==0 else int(proposal["word"][depth-1])
                ) or state.get("observation")!=frame_summary(frame)):
                raise ValueError("original native pixel/action provenance mismatch")
            actual.append(list(position(frame)))
        if not actual:
            raise ValueError("no actual native root")
        roots.add(states[0]["observation"]["whole"])
        if (record.get("completed") is not True or
            record.get("steps")!=len(proposal["word"]) or
            len(actual)!=len(proposal["word"])+1 or
            record.get("interruption") is not None):
            interruptions.append({"trial":key,"word":proposal["word"],
                                  "reason":record.get("interruption"),
                                  "observed_steps":record.get("steps")})
            observations.append({"trial_key":key,"edge_id":proposal["edge_id"],
                                 "history":proposal["history"],
                                 "status":"INTERRUPTED","actual_positions":actual})
            continue
        prefix_match = actual[:-1]==proposal["known_prefix_positions"]
        final_match = actual[-1]==proposal["predicted_final_position"]
        if prefix_match:
            verified_prefixes += 1
        if prefix_match and final_match:
            successes += 1
        row_out = {
            "trial_key":key,"edge_id":proposal["edge_id"],
            "history":proposal["history"],"word":proposal["word"],
            "status": "MATCH" if prefix_match and final_match else "COUNTEREXAMPLE",
            "known_prefix_replayed":prefix_match,"predicted":proposal["predicted_final_position"],
            "observed":actual[-1],"predicted_moved":proposal["predicted_moved"],
            "terrain_colors":proposal["destination_tile_colors"],
            "actual_positions":actual,
            "native_final_raw_sha16":states[-1]["observation"]["whole"]
        }
        pair_results.setdefault(proposal["edge_id"],{})[proposal["history"]] = row_out
        observations.append(row_out)
    if (len(roots)!=1 or list(roots)!=source.get("actual_initial_native_root_hashes") or
        next(iter(roots))!=frozen["original_native_root_hash"] or
        source.get("native_actions")!=sum(
            r["native_path"]["steps"] for r in rows
        )):
        raise ValueError("original native roots or action counts disagree")
    direct_matches = sum(1 for r in observations if
                         r["history"]=="direct" and r["status"]=="MATCH")
    delayed_matches = sum(1 for r in observations if
                          r["history"]=="delayed" and r["status"]=="MATCH")
    pairs_complete = sum(1 for pair in pair_results.values() if
                         "direct" in pair and "delayed" in pair)
    histories_agree = sum(1 for pair in pair_results.values() if
                           "direct" in pair and "delayed" in pair and
                           pair["direct"]["observed"]==pair["delayed"]["observed"])
    return {
        "kind":"AB_NATIVE_FULL_FRONTIER_INDEPENDENT_VERDICT_V1",
        "preregistered_new_edge_count":frozen["unique_unmeasured_edges"],
        "preregistered_trial_count":len(trials),
        "native_actions":source["native_actions"],
        "traceable_native_root_sha16":next(iter(roots)),
        "successful_exact_new_edge_trials":successes,
        "known_prefixes_replayed":verified_prefixes,
        "direct_predictions_passed":direct_matches,
        "delayed_predictions_passed":delayed_matches,
        "pairs_with_both_observations":pairs_complete,
        "direct_and_delayed_actual_agreement":histories_agree,
        "interrupted_trials":interruptions,
        "all_preregistered_trials_passed":successes==len(trials),
        "per_trial":observations,
        "no_hidden_state_or_F3_equivalence_claim":True
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--frozen",type=Path,required=True)
    p.add_argument("--native",type=Path,required=True)
    p.add_argument("--raw",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    with np.load(a.raw,allow_pickle=False) as frames:
        verdict=check(json.loads(a.frozen.read_text()),
                      json.loads(a.native.read_text()),frames)
    verdict["source_sha256"]={
        "predeclared_prediction":sha256(a.frozen.read_bytes()).hexdigest(),
        "native_manifest":sha256(a.native.read_bytes()).hexdigest(),
        "complete_native_raw_arrays":sha256(a.raw.read_bytes()).hexdigest()
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(verdict,indent=2)+"\n")
    print("AB_NATIVE_FRONTIER_VERDICT "+json.dumps({
        "passed":verdict["successful_exact_new_edge_trials"],
        "tested":verdict["preregistered_trial_count"],
        "direct":verdict["direct_predictions_passed"],
        "delayed":verdict["delayed_predictions_passed"],
        "matched_histories":verdict["direct_and_delayed_actual_agreement"],
        "interrupted":len(verdict["interrupted_trials"])
    },sort_keys=True))
    if not verdict["all_preregistered_trials_passed"]:
        raise SystemExit("Native A/B frontier prediction falsified or interrupted; raw evidence retained")

if __name__=="__main__":
    main()
