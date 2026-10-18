"""Independent raw frame verifier of predeclared A/B glyph transport results."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import numpy as np
from work.arc3.native_observation_bridge import frame_summary
from work.arc3.native_glyph_transport_prediction import WORDS,PROTOCOL,glyph_position

def evaluate(frozen:dict,record:dict,archive)->dict:
    if (frozen.get("protocol")!=PROTOCOL or
            frozen.get("new_words_committed_before_native_execution")!=list(WORDS) or
            record.get("protocol")!=PROTOCOL or
            record.get("kind")!="AB_LS20_GLYPH_TRANSPORT_NATIVE_CAPTURE_V1" or
            record.get("game")!="ls20" or
            record.get("words")!=list(WORDS) or
            set(archive.files)!=set(WORDS) or
            len(frozen.get("predictions",[]))!=len(WORDS) or
            len(record.get("native_paths",[]))!=len(WORDS)):
        raise ValueError("incomplete or unrecognized holdout source")
    roots=set()
    rows=[]
    predictions=0
    correct=0
    false=[]
    completed=0
    for word,actual,forecast in zip(WORDS,record["native_paths"],frozen["predictions"]):
        if (actual.get("word")!=word or forecast.get("word")!=word or
                actual.get("steps")!=len(word) or
                actual.get("completed") is not True or
                actual.get("interruption") is not None or
                len(actual.get("states",[]))!=len(word)+1):
            raise ValueError("incomplete native continuation")
        sequence=archive[word]
        if sequence.shape!=(len(word)+1,64,64) or sequence.dtype!=np.uint8:
            raise ValueError("missing raw native pixels")
        predicted=forecast["glyph_top_left_by_depth"]
        if len(predicted)!=len(word)+1:
            raise ValueError("missing preregistered position at native depth")
        positions=[]
        for t,frame in enumerate(sequence):
            observation=actual["states"][t]
            if (observation["index"]!=t or
                observation["action"]!=(None if t==0 else int(word[t-1])) or
                frame_summary(frame)!=observation["observation"]):
                raise ValueError("raw native evidence mismatch")
            pos=list(glyph_position(frame))
            positions.append(pos)
            predictions+=1
            if pos==predicted[t]:
                correct+=1
            else:
                false.append({"word":word,"depth":t,"predicted":predicted[t],
                              "actual":pos})
        roots.add(actual["states"][0]["observation"]["whole"])
        completed+=1
        rows.append({"word":word,"predicted_positions":predicted,
                     "observed_positions":positions,
                     "exact_positions":sum(a==b for a,b in zip(positions,predicted))})
    if (len(roots)!=1 or record.get("all_roots_identical") is not True or
            sorted(roots)!=record.get("root_hashes") or
            completed!=len(WORDS) or record.get("native_actions")!=sum(map(len,WORDS))):
        raise ValueError("native source root/metadata inconsistent")
    return {"kind":"AB_LS20_GLYPH_TRANSPORT_OUT_OF_SAMPLE_VERDICT",
        "protocol":PROTOCOL,
        "independent_native_trajectories":completed,
        "new_native_actions":sum(map(len,WORDS)),
        "total_predeclared_glyph_positions":predictions,
        "correct_exact_glyph_positions":correct,
        "all_exact_positions":correct==predictions,
        "first_disagreements":false,
        "per_word":rows,
        "visible_state_only_no_hidden_or_F3_claim":True}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--prediction",type=Path,required=True)
    p.add_argument("--native",type=Path,required=True)
    p.add_argument("--raw",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    with np.load(a.raw,allow_pickle=False) as archive:
        result=evaluate(json.loads(a.prediction.read_text()),
                        json.loads(a.native.read_text()),archive)
    result["source_sha256"]={
        "prediction":sha256(a.prediction.read_bytes()).hexdigest(),
        "native_json":sha256(a.native.read_bytes()).hexdigest(),
        "native_frames":sha256(a.raw.read_bytes()).hexdigest()}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2)+"\n")
    print("AB_GLYPH_TRANSPORT_VERDICT "+json.dumps({
        "trajectories":result["independent_native_trajectories"],
        "positions":result["total_predeclared_glyph_positions"],
        "correct":result["correct_exact_glyph_positions"],
        "pass":result["all_exact_positions"]},sort_keys=True))
    if not result["all_exact_positions"]:
        raise SystemExit("FALSIFIED observed local action relation in new native sequence")
if __name__=="__main__":
    main()
