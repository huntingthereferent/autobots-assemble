"""Predeclared falsifiable LS20 visible trace + glyph/time hypotheses.

Derived only from independently archived *native raw frames* at depths 0..4.
Not an F3 hidden-state map, game solver, REA dependency, or ARC agent.
Holdout predictions for depths 5 and 6 are written before new SDK execution.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import numpy as np

# Frozen BEFORE new native action words are measured.
NATIVE_WORDS=(
    "11111", "22222", "33333", "44444",
    "12341", "21432", "34123", "43214",
    "111111", "222222", "333333", "444444",
    "123412", "214321", "341234", "432143",
)
HELD_OUT_DEPTHS=(5,6)
ROOT_GRID_SHAPE=(64,64)
TRACE_COLOR=11
GLYPH_COLORS=(9,12)
SOURCE_ARCHIVE="39091972954/12122494867/native-new/f3-native-suffix.npz"
PROTOCOL="AB_LS20_TRACE_GLYPH_PREREGISTERED_V1"

def predicted_trace(depth:int)->np.ndarray:
    if type(depth) is not int or depth not in range(7):
        raise ValueError("Only declared depths 0..6 have a prediction")
    predicted=np.zeros(ROOT_GRID_SHAPE,dtype=bool)
    predicted[61:63,13+depth:55]=True
    return predicted

def verify_training_archive(path:Path)->dict:
    """Require the exact independently recorded original train envelope."""
    with np.load(path,allow_pickle=False) as rows:
        if len(rows.files)!=24:
            raise ValueError("training source must retain all 24 independent trajectories")
        counts={str(step):0 for step in range(5)}
        glyph_to_frames={}
        for name in rows.files:
            frames=rows[name]
            if (frames.dtype!=np.uint8 or frames.shape[1:]!=ROOT_GRID_SHAPE
                    or len(frames) not in (4,5)):
                raise ValueError("training archive changed structure")
            for depth,frame in enumerate(frames):
                actual=(frame==TRACE_COLOR)
                if not np.array_equal(actual,predicted_trace(depth)):
                    raise ValueError("historical action-independent clock prediction disproved")
                counts[str(depth)]+=1
                key=(depth,np.isin(frame,GLYPH_COLORS).tobytes())
                prior=glyph_to_frames.setdefault(key,frame.tobytes())
                if prior!=frame.tobytes():
                    raise ValueError("historical same-glyph same-depth frame uniqueness disproved")
        if counts!={"0":24,"1":24,"2":24,"3":24,"4":24}:
            raise ValueError("historical source must reach all original depths")
    return {"training_depth_observations":counts,
            "unique_glyph_time_groups":len(glyph_to_frames),
            "source_archive_sha256":sha256(path.read_bytes()).hexdigest()}

def proposal(path:Path)->dict:
    baseline=verify_training_archive(path)
    return {"protocol":PROTOCOL,
        "basis":"strict raw official LS20 visible frames; not hidden state",
        "source":SOURCE_ARCHIVE,
        "training_archive":baseline,
        "committed_holdout_words":list(NATIVE_WORDS),
        "held_out_depths":list(HELD_OUT_DEPTHS),
        "hypotheses":[
            {"name":"action_independent_trace_exact",
             "frozen":"at t=5,6 native color-11 exactly occupies rows 61,62 and columns 13+t through 54 inclusive",
             "predicted_counts":{"5":74,"6":72}},
            {"name":"same_depth_same_glyph_implies_same_visible_frame",
             "frozen":"for any two separately reset trajectories, when their native {9,12} glyph pixel masks equal at identical depth, every native raw pixel also equals"},
        ],
        "f3_state_correspondence_assumed":False,
        "native_hidden_state_equivalence_claimed":False,
        "preregistered_without_holdout_results":True,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--basis",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    result=proposal(args.basis)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n")
    print("AB_PREREGISTERED_TRACE_PREDICTION "+json.dumps({
        "depths":result["held_out_depths"],
        "trace_cells":result["hypotheses"][0]["predicted_counts"],
        "out_of_sample_words":len(NATIVE_WORDS),
        "training_source_sha256":result["training_archive"]["source_archive_sha256"]},sort_keys=True))
if __name__=="__main__":
    main()
