"""A/B native source-backed glyph transport inference, no REA or invented F3 map.

Admit only prior verified raw LS20 pixels and actions. The model is a partial
observed transition function (glyph position, native action) -> next position.
Unknown transitions remain unknown; it does not presume a global grid law.
Predictions for previously unrecorded eight-action words are frozen before
running the native environment.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import numpy as np
from work.arc3.native_observation_bridge import frame_summary

# Independent prior native archives, all collected before this experiment.
SOURCES=(
 ("historical","native-historical/f3-native-suffix.json",
   "native-historical/f3-native-suffix.npz",
   "51418edb3f403ce5696cd481cd25bbb593660bbd9f384212a468f5934dbac310",
   "e7036323f8febfeca5ccd453c83e9a9e44c21824f975ee3c9b6b2d8874966fa1"),
 ("suffix-holdout","native-new/f3-native-suffix.json",
   "native-new/f3-native-suffix.npz",
   "b3a1c793e3d3a41ff9660e4b1cd9e1ed2919767a8b8d47815c7704463fdbdcc6",
   "033c574999a656ebf57ff628f03be47bcccf16e85705eabe4867f489a7e6bf7f"),
 ("depth-holdout","native-holdout.json","native-holdout.npz",
   "c346fea8ab5ac12daaefec8fa2305f3bf57497f561b6c8c0042c83dea37ee685",
   "988892e6b2a43ee51859649bbe2d7d83d8c93d72cc16900275f931255d173b47"),
)
WORDS=(
 "12341234","21432143","34123412","43214321",
 "33333333","44444444","22222222","12121212",
 "34343434","43434343","21212121","24312431",
 "31423142","12431243","14321432","23142314","32143214",
)
PROTOCOL="AB_LS20_NATIVE_GLYPH_TRANSPORT_V1"

def digest(path:Path)->str:
    return sha256(path.read_bytes()).hexdigest()

def glyph_position(frame:np.ndarray)->tuple[int,int]:
    if not isinstance(frame,np.ndarray) or frame.shape!=(64,64) or frame.dtype!=np.uint8:
        raise ValueError("requires complete raw 64x64 native uint8 frame")
    coords=np.argwhere(frame==12)
    if coords.shape!=(10,2):
        raise ValueError("observed glyph is not a 10-pixel block")
    y,x=int(coords[:,0].min()),int(coords[:,1].min())
    exact=np.zeros((64,64),dtype=bool)
    exact[y:y+2,x:x+5]=True
    if not np.array_equal(exact,frame==12):
        raise ValueError("observed glyph is not exact 2x5 rectangle")
    return y,x

def trajectories(source_kind:str,manifest:dict,archive):
    if source_kind=="depth-holdout":
        if (manifest.get("kind")!="AB_LS20_REAL_NATIVE_HOLDOUT_RAW_FRAMES_V1"
                or manifest.get("game")!="ls20" or manifest.get("completed_trajectories")!=16):
            raise ValueError("untrusted prior depth holdout")
        for row in manifest["native_paths"]:
            yield row["word"],row,archive[row["word"]]
    else:
        if (manifest.get("kind")!="ARC3_NATIVE_VISIBLE_STATE_SUFFIX_DISCRIMINATION"
                or manifest.get("game")!="ls20"):
            raise ValueError("untrusted prior suffix observation")
        for item in manifest["comparisons"]:
            a,b=item["prefix_pair"]
            suffix=item["suffix"]
            for side,prefix in (("a",a),("b",b)):
                key=a+"_"+b+"_suffix_"+suffix+"_"+side
                yield prefix+suffix,item["native_left" if side=="a" else "native_right"],archive[key]

def infer_model(basis:Path,prior:Path)->dict:
    edges:dict[tuple[int,int,str],Counter]={}
    origins=set()
    sequence_count=0
    action_count=0
    hashes={}
    for label,metadata,compressed,metadata_sha,compressed_sha in SOURCES:
        root=basis if label!="depth-holdout" else prior
        mpath=root/metadata
        npath=root/compressed
        if digest(mpath)!=metadata_sha or digest(npath)!=compressed_sha:
            raise ValueError("original native evidence bytes differ from source-pinned SHA256: "+label)
        hashes[label]={"manifest":metadata_sha,"raw":compressed_sha}
        manifest=json.loads(mpath.read_text())
        with np.load(npath,allow_pickle=False) as archive:
            counted=0
            for word,row,frames in trajectories(label,manifest,archive):
                if (not isinstance(word,str) or not word or
                        any(ch not in "1234" for ch in word) or
                        frames.shape!=(len(word)+1,64,64) or frames.dtype!=np.uint8 or
                        row["word"]!=word or row["steps"]!=len(word) or
                        row["completed"] is not True or row["interruption"] is not None or
                        len(row["states"])!=len(word)+1):
                    raise ValueError("unverified native path or word mismatch")
                positions=[]
                origin=row["states"][0]["observation"]["whole"]
                origins.add(origin)
                for index,frame in enumerate(frames):
                    state=row["states"][index]
                    if (state["index"]!=index or
                            state["action"]!=(None if index==0 else int(word[index-1])) or
                            state["observation"]!=frame_summary(frame)):
                        raise ValueError("native raw pixel provenance mismatch")
                    positions.append(glyph_position(frame))
                for i,action in enumerate(word):
                    y,x=positions[i]
                    edges.setdefault((y,x,action),Counter())[positions[i+1]]+=1
                sequence_count+=1
                action_count+=len(word)
                counted+=1
            expected={"historical":36,"suffix-holdout":24,"depth-holdout":16}[label]
            if counted!=expected or len(archive.files)!=expected:
                raise ValueError("native training archive incomplete")
    if sequence_count!=76 or action_count!=304 or len(origins)!=1:
        raise ValueError("original source did not contain 76 trajectories, 304 actions, one root")
    if len(edges)!=27 or any(len(v)!=1 for v in edges.values()):
        raise ValueError("not a consistent partial source-derived action relation")
    model={key:next(iter(v)) for key,v in edges.items()}
    origin=(45,34)
    predictions=[]
    for word in WORDS:
        state=origin
        states=[list(state)]
        for action in word:
            candidate=model.get((state[0],state[1],action))
            if candidate is None:
                raise ValueError("new word requests unknown source transition: "+word)
            state=candidate
            states.append(list(state))
        predictions.append({"word":word,"glyph_top_left_by_depth":states})
    source_record={
        "protocol":PROTOCOL,
        "source":"real independent ARC-AGI-3 LS20 raw observations",
        "training_source_sha256":hashes,
        "training_trajectories":sequence_count,
        "training_native_actions":action_count,
        "unique_observed_state_action_edges":len(model),
        "conflicting_observed_edges":0,
        "new_words_committed_before_native_execution":list(WORDS),
        "predictions":predictions,
        "partial_model":[{"glyph":[y,x],"action":action,"next_glyph":list(next(iter(out))),
            "independent_observations":sum(out.values())}
            for (y,x,action),out in sorted(edges.items())],
        "claims":{"predicted_pixel_color":12,
                  "predicted_glyph_rectangle":[2,5],
                  "position_is_full_hidden_state":False,
                  "unknown_edges_are_accepted":False,
                  "native_f3_correspondence":False,
                  "complete_transition_law":False},
    }
    return source_record

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--basis",type=Path,required=True)
    p.add_argument("--previous-holdout",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    result=infer_model(a.basis,a.previous_holdout)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2)+"\n")
    print("AB_GLYPH_TRANSPORT_FROZEN "+json.dumps({
        "source_edges":result["unique_observed_state_action_edges"],
        "recorded_native_actions":result["training_native_actions"],
        "new_words":len(result["predictions"]),
        "target_depth":8,"source_trajectories":result["training_trajectories"]},sort_keys=True))

if __name__=="__main__":
    main()
