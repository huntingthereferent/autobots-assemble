"""Predeclare shifted-time native mixed-tile entry vs matched non-entry controls.

Tests if trace plateau follows a specific visible entry event, rather than a
fixed depth. Frozen prior to new native observations, with original raw pixel
SHA256. This is NOT a retrofit of the earlier invalid clock forecast.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import numpy as np
from .native_special_tile_successor import PREFIXES, BASELINE_FRAME, BASELINE_GLYPH
from .native_observation_bridge import frame_summary
from .native_geometry_unknown_edge_verify import position

PROTOCOL="AB_LS20_SHIFTED_SPECIAL_ENTRY_CLOCK_V1"
LOOPS=("","12","1212","121212")
# Final action must enter the original mixed tile; matched control does not.
CONTROL_ACTION={"11113323":"4","11113332":"1","33311413":"4"}
PRIOR_SHA256={
 "frozen-multistep.json":"200d14e7dbe2ea0e10fb0838595f61d823a60a8c91fabea6d25917e17712b16f",
 "native-multistep.json":"712d539c6d18ac641b2a2e0f6ecbb31f35c5d1e4ad10125de919884e5355c699",
 "native-multistep.npz":"88fd9bc9857cfa2fa8ba5febf1327d772f009ed7aac0c2beb4e161722b087f25",
 "independent-verdict.json":"c09c14d52e8d30926f67dfb8018c2b92508c7fae560506e7fb7d9bc95b0035b0",
}
LOOP_SOURCE_SHA256={
 "preregistered-transport.json":"4d66bfdbb7d213cd2c1ca065b9b0f8484a57110146fbf7b53fb57e21a3c6be0c",
 "native-transport.json":"7e3e4accd90c39199c0d23fa40dc52b1af12802439635d322d9016c55780c466",
 "native-transport.npz":"09683abcb4cc534bac76d53ef0aabda31342b5d53029077cece14284844e91be",
 "independent-verdict.json":"190a8a09510219af7ba362decb381ddd51a8ee37ea44c68d224a262879bd5727",
}

def authenticate_prior(special:Path,loops:Path)->dict:
    for filename,digest in PRIOR_SHA256.items():
        if sha256((special/filename).read_bytes()).hexdigest()!=digest:
            raise ValueError("source original multistep native evidence changed: "+filename)
    for filename,digest in LOOP_SOURCE_SHA256.items():
        if sha256((loops/filename).read_bytes()).hexdigest()!=digest:
            raise ValueError("original source root-loop evidence changed: "+filename)
    verdict=json.loads((special/"independent-verdict.json").read_text())
    manifest=json.loads((special/"native-multistep.json").read_text())
    forecast=json.loads((special/"frozen-multistep.json").read_text())
    if (verdict.get("full_frame_equal_pairs")!=132 or
        verdict.get("exit_return_with_advanced_visible_clock")!=12 or
        verdict.get("trace_masks_exact")!=0 or
        verdict.get("all_hypotheses_passed") is not False or
        len(manifest.get("native_paths",[]))!=36 or
        len(forecast.get("registered_trials",[]))!=36):
        raise ValueError("prior invalid clock prediction was not preserved")
    with np.load(special/"native-multistep.npz",allow_pickle=False) as old:
        if set(old.files)!={f"trial_{n:02d}" for n in range(36)}:
            raise ValueError("prior special-tile raw frame archive incomplete")
        for n in range(36):
            record=manifest["native_paths"][n]["native_path"]
            images=old[f"trial_{n:02d}"]
            word=forecast["registered_trials"][n]["word"]
            if (record.get("word")!=word or record.get("completed") is not True or
                len(record["states"])!=len(images) or
                images.shape!=(len(word)+1,64,64) or images.dtype!=np.uint8):
                raise ValueError("prior source trajectory incomplete")
            for i,frame in enumerate(images):
                state=record["states"][i]
                if (state["index"]!=i or
                    state["action"]!=(None if i==0 else int(word[i-1])) or
                    state["observation"]!=frame_summary(frame)):
                    raise ValueError("prior source pixels and metadata disagree")
            if (frame_summary(images[8])["whole"]!=BASELINE_FRAME or
                int(np.count_nonzero(images[7]==11))!=70 or
                int(np.count_nonzero(images[8]==11))!=70 or
                position(images[8])!=BASELINE_GLYPH):
                raise ValueError("special source event plateau not independently witnessed")
    with np.load(loops/"native-transport.npz",allow_pickle=False) as arr:
        frames=arr["12121212"]
        if frames.shape!=(9,64,64) or frames.dtype!=np.uint8:
            raise ValueError("original independent roundtrip source unavailable")
        for i in (0,2,4,6,8):
            if position(frames[i])!=(45,34):
                raise ValueError("claimed native root-return loop never observed")
        if any(int(np.count_nonzero(frames[i]==11))!=84-2*i for i in range(9)):
            raise ValueError("ordinary non-entry clock control is inconsistent")
    return {"observed_event_plateau_at_depth8":True,
            "independent_source_root_roundtrip_replayed":True,
            "original_raw_source_sha256":PRIOR_SHA256,
            "original_root_return_sha256":LOOP_SOURCE_SHA256}

def freeze(special:Path,loops:Path)->dict:
    sources=authenticate_prior(special,loops)
    trials=[]
    for detour in LOOPS:
        for prefix in PREFIXES:
            for category,action in (("enter",prefix[-1]),
                                    ("matched_nonentry",CONTROL_ACTION[prefix])):
                word=detour+prefix[:-1]+action
                trials.append({
                    "detour":detour,"original_history":prefix,
                    "kind":category,"word":word,
                    "known_root_detour_steps":len(detour),
                    "entry_or_control_step":len(word),
                    "expected_entry_glyph":list(BASELINE_GLYPH) if category=="enter" else None,
                    "prediction":"entry: trace mask stays equal between final two frames; matched nonentry: trace loses exactly two pixels",
                })
    if len(trials)!=24 or len({t["word"] for t in trials})!=24:
        raise ValueError("missing or nonindependent native holdout words")
    return {"kind":"AB_FROZEN_SHIFTED_NATIVE_TILE_ENTRY_V1",
            "protocol":PROTOCOL,
            "sources":sources,
            "detour_lengths":[len(w) for w in LOOPS],
            "original_histories":list(PREFIXES),
            "frozen_trials":trials,
            "expected_native_trials":24,
            "distinct_entry_depths":[8,10,12,14],
            "entry_pause_predictions":12,
            "matched_control_progress_predictions":12,
            "hypothesis":"native color11 trace stalls exactly on step entering mixed tile, even when entry is delayed by preverified return loops",
            "original_invalid_absolute_clock_prediction_not_reused":True,
            "hidden_native_state_identity_NOT_claimed":True}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--special",type=Path,required=True)
    p.add_argument("--loops",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    result=freeze(a.special,a.loops)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2)+"\n")
    print("AB_FROZEN_SHIFTED_TILE_ENTRY "+json.dumps({
      "trials":24,"entry_depths":[8,10,12,14],
      "actions":sum(len(t["word"]) for t in result["frozen_trials"])},sort_keys=True))
if __name__=="__main__":main()
