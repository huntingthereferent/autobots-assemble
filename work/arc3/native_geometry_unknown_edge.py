"""A/B native map-geometry prediction for unobserved state/action edges.

Source-frozen before native collection. Training comes ONLY from verified,
SHA-pinned original native frames and the 27-edge previous transport record.
The source-driven map predicts movement into untested tiles, including walls.
No REA; no claimed F3 projection or hidden-state transition proof.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import numpy as np
from .native_observation_bridge import frame_summary

PROTOCOL="AB_LS20_UNKNOWN_EDGE_GEOMETRY_V1"
WORDS=(
    "41","113","114","144","332","334","441","442","443",
    "1113","1114","3331","3332","4441","4442","4443","11113","11114",
)
DELTA={"1":(-5,0),"2":(5,0),"3":(0,-5),"4":(0,5)}
EXPECTED={
    "preregistered-transport.json":"4d66bfdbb7d213cd2c1ca065b9b0f8484a57110146fbf7b53fb57e21a3c6be0c",
    "native-transport.json":"7e3e4accd90c39199c0d23fa40dc52b1af12802439635d322d9016c55780c466",
    "native-transport.npz":"09683abcb4cc534bac76d53ef0aabda31342b5d53029077cece14284844e91be",
    "independent-verdict.json":"190a8a09510219af7ba362decb381ddd51a8ee37ea44c68d224a262879bd5727",
}

def sha(path:Path)->str:
    return sha256(path.read_bytes()).hexdigest()

def source_material(root:Path)->tuple[dict,np.ndarray,dict]:
    for name,digest in EXPECTED.items():
        if sha(root/name)!=digest:
            raise ValueError("previous independently verified source digest changed: "+name)
    previous=json.loads((root/"preregistered-transport.json").read_text())
    receipt=json.loads((root/"independent-verdict.json").read_text())
    original=json.loads((root/"native-transport.json").read_text())
    if (previous["protocol"]!="AB_LS20_NATIVE_GLYPH_TRANSPORT_V1" or
            previous["unique_observed_state_action_edges"]!=27 or
            previous["training_native_actions"]!=304 or
            receipt["all_exact_positions"] is not True or
            receipt["correct_exact_glyph_positions"]!=153 or
            original.get("all_roots_identical") is not True):
        raise ValueError("last native source experiment not verified")
    with np.load(root/"native-transport.npz",allow_pickle=False) as archive:
        if set(archive.files)!=set(original["words"]):
            raise ValueError("last independent raw pixel archive incomplete")
        zero=archive["44444444"][0].copy()
        moved=archive["44444444"][1]
        if (frame_summary(zero)!=original["native_paths"][original["words"].index("44444444")]["states"][0]["observation"]
                or frame_summary(moved)!=original["native_paths"][original["words"].index("44444444")]["states"][1]["observation"]):
            raise ValueError("original training map has inconsistent raw pixels")
        if (not np.all(zero[45:47,34:39]==12) or
                not np.all(zero[47:50,34:39]==9) or
                not np.all(moved[45:50,34:39]==3)):
            raise ValueError("source did not reveal glyph-underlying walkable tile")
        zero[45:50,34:39]=moved[45:50,34:39]
    return previous,zero,original

def predict(map_:np.ndarray,state:tuple[int,int],action:str)->tuple[int,int]:
    y,x=state
    dy,dx=DELTA[action]
    ny,nx=y+dy,x+dx
    if ny<0 or nx<0 or ny+5>64 or nx+5>64:
        return state
    # Source geometric hypothesis: native color 3 / 5 tiles are passable,
    # and all other raw tiles block a complete 5x5 glyph footprint.
    destination=map_[ny:ny+5,nx:nx+5]
    return (ny,nx) if np.isin(destination,(3,5)).all() else state

def freeze(root:Path)->dict:
    previous,map_,original=source_material(root)
    edges={}
    for row in previous["partial_model"]:
        key=(tuple(row["glyph"]),row["action"])
        if key in edges or row["independent_observations"]<1:
            raise ValueError("duplicate or missing trained native relation")
        edges[key]=tuple(row["next_glyph"])
        if predict(map_,key[0],key[1])!=edges[key]:
            raise ValueError("geometry rule fails original 27 native transitions")
    if len(edges)!=27:
        raise ValueError("missing trained native action transitions")
    observations=[]
    unknowns=set()
    move_count=0
    for word in WORDS:
        state=(45,34)
        positions=[list(state)]
        for action in word[:-1]:
            if (state,action) not in edges:
                raise ValueError("trial prefix did not consist only of proven source transitions")
            state=edges[(state,action)]
            positions.append(list(state))
        action=word[-1]
        if (state,action) in edges:
            raise ValueError("holdout endpoint was already measured")
        if (state,action) in unknowns:
            raise ValueError("holdout repeated the same unseen edge")
        unknowns.add((state,action))
        ending=predict(map_,state,action)
        move_count+=ending!=state
        observations.append({"word":word,"known_prefix_positions":positions,
            "unobserved_source_position":list(state),"unobserved_action":action,
            "predicted_next_position":list(ending),
            "predicted_moved":ending!=state,
            "source_edge_was_previously_observed":False})
    if len(unknowns)!=len(WORDS) or not (move_count>0 and move_count<len(WORDS)):
        raise ValueError("holdouts are not a balanced set of distinct unknown edges")
    return {"protocol":PROTOCOL,"kind":"NATIVE_AB_GEOMETRY_SOURCE_FROZEN",
        "source_archive_sha256":EXPECTED,"source_observed_edges":len(edges),
        "source_observed_native_actions":304,
        "source_reproduced_geometry_edges":27,
        "frozen_holdout_words":list(WORDS),
        "native_map_walkable_colors":[3,5],
        "native_glyph_full_footprint":[5,5],
        "candidate_displacements":{k:list(v) for k,v in DELTA.items()},
        "unseen_holdout_edge_predictions":observations,
        "predicted_moved":move_count,
        "predicted_blocked":len(WORDS)-move_count,
        "no_native_hidden_state_claim":True,
        "no_F3_correspondence_claim":True,
        "source_evidence_not_same_as_predictions":True}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    receipt=freeze(a.source)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(receipt,indent=2)+"\n")
    print("AB_PREREGISTERED_UNKNOWN_EDGES "+json.dumps({
        "unseen_edges":len(WORDS),"predicted_moved":receipt["predicted_moved"],
        "predicted_blocked":receipt["predicted_blocked"]},sort_keys=True))

if __name__=="__main__":main()
