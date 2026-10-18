"""Independent raw-frame proof/contradiction of shift-in-time native event pause."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import numpy as np
from .native_shifted_tile_entry import PROTOCOL
from .native_observation_bridge import frame_summary
from .native_geometry_unknown_edge_verify import position

def evaluate(frozen,native,raw)->dict:
    trials=frozen.get("frozen_trials")
    received=native.get("trials")
    if (frozen.get("kind")!="AB_FROZEN_SHIFTED_NATIVE_TILE_ENTRY_V1" or
        frozen.get("protocol")!=PROTOCOL or
        native.get("kind")!="AB_NATIVE_SHIFTED_TILE_ENTRY_RAW_V1" or
        native.get("protocol")!=PROTOCOL or native.get("game")!="ls20" or
        not isinstance(trials,list) or len(trials)!=24 or
        not isinstance(received,list) or len(received)!=24 or
        set(raw.files)!={f"trial_{n:02d}" for n in range(24)}):
        raise ValueError("missing source-qualified preregistration or native data")
    roots=set()
    rows=[]
    interrupted=[]
    entry_ok=control_ok=0
    for n,(pre,observed) in enumerate(zip(trials,received)):
        key=f"trial_{n:02d}"
        path=observed.get("path")
        word=pre["word"]
        if (observed.get("key")!=key or observed.get("kind")!=pre["kind"] or
            not isinstance(path,dict) or path.get("word")!=word):
            raise ValueError("source changed native action word or group identity")
        frames=raw[key]
        states=path.get("states")
        if (frames.dtype!=np.uint8 or frames.ndim!=3 or
            frames.shape[1:]!=(64,64) or
            not isinstance(states,list) or len(states)!=len(frames)):
            raise ValueError("native raw pixels missing")
        for depth,(state,image) in enumerate(zip(states,frames)):
            if (state.get("index")!=depth or
                state.get("action")!=(None if depth==0 else int(word[depth-1])) or
                state.get("observation")!=frame_summary(image)):
                raise ValueError("native raw pixel or action provenance changed")
        roots.add(states[0]["observation"]["whole"])
        if (path.get("completed") is not True or path.get("interruption") is not None
                or path.get("steps")!=len(word) or len(frames)!=len(word)+1):
            interrupted.append({"word":word,"reason":path.get("interruption"),
                                "actual_steps":path.get("steps")})
            continue
        before=frames[-2]
        after=frames[-1]
        before_mask=(before==11)
        after_mask=(after==11)
        prev_count=int(np.count_nonzero(before_mask))
        count=int(np.count_nonzero(after_mask))
        same_trace=bool(np.array_equal(before_mask,after_mask))
        position_last=position(after)
        if pre["kind"]=="enter":
            correct=(same_trace and position_last==(30,19))
            entry_ok+=int(correct)
        else:
            correct=(prev_count-count==2 and not same_trace and position_last!=(30,19))
            control_ok+=int(correct)
        rows.append({"word":word,"kind":pre["kind"],"entry_step":len(word),
                    "before_trace_cells":prev_count,"after_trace_cells":count,
                    "trace_stayed_exactly_same":same_trace,
                    "actual_glyph_position":list(position_last),
                    "prediction_passed":correct,
                    "raw_final_frame_sha16":states[-1]["observation"]["whole"],
                    "native_state":states[-1]["state"]})
    if (len(roots)!=1 or sorted(roots)!=native.get("roots") or
        native.get("native_actions")!=sum(x["path"]["steps"] for x in received)):
        raise ValueError("native root or action sequence integrity failed")
    return {"kind":"AB_LS20_SHIFTED_ENTRY_EVENT_VERDICT",
            "native_actions":native["native_actions"],
            "complete_trials":len(rows),"interruptions":interrupted,
            "entry_pause_passed":entry_ok,"entry_pause_tested":12,
            "matched_nonentry_progress_passed":control_ok,
            "matched_nonentry_tested":12,
            "all_event_hypotheses_passed":entry_ok==12 and control_ok==12 and not interrupted,
            "actual_frame_observations":rows,
            "no_hidden_state_or_F3_equivalence_claimed":True}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--frozen",type=Path,required=True)
    p.add_argument("--native",type=Path,required=True)
    p.add_argument("--raw",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    with np.load(a.raw,allow_pickle=False) as frames:
        result=evaluate(json.loads(a.frozen.read_text()),json.loads(a.native.read_text()),frames)
    result["source_sha256"]={
        "preregistered":sha256(a.frozen.read_bytes()).hexdigest(),
        "actual_native_manifest":sha256(a.native.read_bytes()).hexdigest(),
        "actual_raw_pixels":sha256(a.raw.read_bytes()).hexdigest()}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2)+"\n")
    print("AB_NATIVE_SHIFTED_ENTRY_VERDICT "+json.dumps({
        "pass":result["all_event_hypotheses_passed"],
        "entry":result["entry_pause_passed"],
        "control":result["matched_nonentry_progress_passed"],
        "native_actions":result["native_actions"],
        "interruptions":len(result["interruptions"])},sort_keys=True))
    if not result["all_event_hypotheses_passed"]:
        raise SystemExit("Native mixed-tile event-pause hypothesis falsified; raw evidence retained")

if __name__=="__main__":main()
