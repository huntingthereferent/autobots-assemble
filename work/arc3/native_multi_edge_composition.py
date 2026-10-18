"""A/B: frozen two- and three-NEW-edge native LS20 geometry predictions.

No REA and no mapping of visible ARC frames into F3 state. This experiment
replays verified raw prior evidence and predicts composition across edges not
present in ANY previously recorded native trajectory.
"""
from __future__ import annotations
import argparse
from collections import defaultdict, deque, Counter
from hashlib import sha256
import json
from pathlib import Path
import numpy as np
from .native_geometry_frontier import load_source
from .native_geometry_unknown_edge import predict
from .native_geometry_unknown_edge_verify import position
from .native_observation_bridge import frame_summary

PROTOCOL="AB_LS20_MULTINEW_EDGE_COMPOSITION_V1"
FRONTIER_SHA256={
    "frozen-full-frontier.json":"566344fddadc42a4b39de3ae64aa8522ba5873ad22e5390ed30429d1f5be9dae",
    "native-full-frontier.json":"01336fcf72873596c23c411352711f76b09afd202b77e32cc412230cc7632bd9",
    "native-full-frontier.npz":"022a5f41cc034297d99139b50da953c35686b1c2f2e5ad1f69e1622bd3393152",
    "independent-verdict.json":"ccee061e5dbf1fad1f9d517b4d0ad18755f3e521391346a45ca516f6567f5fe0",
}
ROOT=(45,34)

def load_all_edges(prior:Path,last:Path,frontier:Path):
    terrain,edges,root_hash=load_source(prior,last)
    for filename,expected in FRONTIER_SHA256.items():
        if sha256((frontier/filename).read_bytes()).hexdigest()!=expected:
            raise ValueError("independent complete-frontier source bytes changed: "+filename)
    frozen=json.loads((frontier/"frozen-full-frontier.json").read_text())
    native=json.loads((frontier/"native-full-frontier.json").read_text())
    verdict=json.loads((frontier/"independent-verdict.json").read_text())
    if (frozen.get("kind")!="AB_NATIVE_SOURCE_FROZEN_COMPLETE_FRONTIER_V1" or
        frozen.get("known_native_edge_count")!=45 or
        frozen.get("unique_unmeasured_edges")!=39 or
        verdict.get("all_preregistered_trials_passed") is not True or
        verdict.get("successful_exact_new_edge_trials")!=78 or
        verdict.get("direct_and_delayed_actual_agreement")!=39 or
        len(frozen.get("source_frozen_trials",[]))!=78 or
        len(native.get("native_trials",[]))!=78 or
        native.get("game")!="ls20"):
        raise ValueError("prior native full-frontier verification missing")
    added=set()
    initial_roots=set()
    with np.load(frontier/"native-full-frontier.npz",allow_pickle=False) as arrays:
        if set(arrays.files)!={f"trial_{i:03d}" for i in range(78)}:
            raise ValueError("original native raw array coverage incomplete")
        for i,(proposal,record) in enumerate(zip(
            frozen["source_frozen_trials"],native["native_trials"]
        )):
            key=f"trial_{i:03d}"
            trajectory=record.get("native_path")
            word=proposal["word"]
            if (record.get("trial_key")!=key or
                record.get("edge_id")!=proposal["edge_id"] or
                record.get("history")!=proposal["history"] or
                trajectory.get("word")!=word or
                trajectory.get("completed") is not True or
                trajectory.get("interruption") is not None or
                trajectory.get("steps")!=len(word) or
                len(trajectory.get("states",[]))!=len(word)+1):
                raise ValueError("prior native trial identity or completion invalid")
            grids=arrays[key]
            if grids.dtype!=np.uint8 or grids.shape!=(len(word)+1,64,64):
                raise ValueError("missing original native pixels")
            observed=[]
            for depth,image in enumerate(grids):
                state=trajectory["states"][depth]
                if (state.get("index")!=depth or
                    state.get("action")!=(None if depth==0 else int(word[depth-1])) or
                    state.get("observation")!=frame_summary(image)):
                    raise ValueError("previous native observation does not match raw pixels")
                observed.append(list(position(image)))
            initial_roots.add(trajectory["states"][0]["observation"]["whole"])
            if (observed[:-1]!=proposal["known_prefix_positions"] or
                observed[-1]!=proposal["predicted_final_position"]):
                raise ValueError("previously verified native position prediction no longer replayed")
            if proposal["history"]=="direct":
                pair=(tuple(proposal["unseen_source_position"]),proposal["unseen_action"])
                if pair in edges or pair in added:
                    raise ValueError("prior new edge duplicate")
                added.add(pair)
                edges[pair]=tuple(observed[-1])
    if len(added)!=39 or len(edges)!=84 or initial_roots!={root_hash}:
        raise ValueError("known native source graph incomplete")
    for (state,action),destination in edges.items():
        if predict(terrain,state,action)!=destination:
            raise ValueError("unchanged source geometry does not reproduce all 84 native edges")
    return terrain,edges,root_hash

def shortest_known_paths(edges):
    paths={ROOT:""}
    todo=deque([ROOT])
    while todo:
        state=todo.popleft()
        for action in "1234":
            next_state=edges.get((state,action))
            if next_state is not None and next_state not in paths:
                paths[next_state]=paths[state]+action
                todo.append(next_state)
    if len(paths)!=27:
        raise ValueError("source verified graph does not have expected reachable positions")
    return paths

def observed_prefix(edges,word):
    at=ROOT
    positions=[list(at)]
    for action in word:
        if (at,action) not in edges:
            raise ValueError("a purported known prefix contains an unknown edge")
        at=edges[(at,action)]
        positions.append(list(at))
    return positions

def freeze(prior:Path,last:Path,frontier:Path):
    terrain,edges,root_hash=load_all_edges(prior,last,frontier)
    paths=shortest_known_paths(edges)
    two=[]
    triple=[]
    for start,prefix in sorted(paths.items(),key=lambda item:(len(item[1]),item[1])):
        for a in "1234":
            if (start,a) in edges:
                continue
            first=predict(terrain,start,a)
            if first==start:
                continue  # A blocked first edge cannot explore a second new vertex.
            for b in "1234":
                if (first,b) in edges:
                    continue
                second=predict(terrain,first,b)
                two.append((prefix,start,(a,b),(first,second)))
                if second==first:
                    continue
                for c in "1234":
                    if (second,c) not in edges:
                        third=predict(terrain,second,c)
                        triple.append((prefix,start,(a,b,c),(first,second,third)))
    if len(two)!=52 or len(triple)!=120:
        raise ValueError("the novel geometry composition frontier changed")
    # This deliberately selected index sequence is declared in code, not chosen
    # after observing new results. It spreads 12 three-edge cases through the
    # complete candidate set and retains blocked outcomes if selected.
    triple=sorted(triple,key=lambda item:(item[0]+''.join(item[2])))
    chosen_three=triple[4::10]
    if len(chosen_three)!=12:
        raise ValueError("fixed three-edge coverage changed")
    trials=[]
    for class_name,rows in (("two-new-edges",two),
                            ("three-new-edges",chosen_three)):
        for prefix,start,actions,outcomes in rows:
            if len(actions)<2 or any((start,a) in edges for a in actions[:1]):
                raise ValueError("not a genuinely new edge series")
            word=prefix+"".join(actions)
            if len(word)>15:
                raise ValueError("new native holdout unexpectedly long")
            positions=observed_prefix(edges,prefix)
            if positions[-1]!=list(start):
                raise ValueError("failed source-known prefix")
            states=[start,*outcomes]
            if any((state,action) in edges for state,action in zip(states,actions)):
                raise ValueError("one proposed new action was already independently measured")
            trials.append({
                "kind":class_name,"word":word,
                "known_prefix":prefix,"known_prefix_positions":positions,
                "previously_unobserved_actions":"".join(actions),
                "predicted_new_positions":[list(v) for v in outcomes],
                "predicted_movement":[b!=a for a,b in zip(states,outcomes)],
                "no_predicted_value_admitted_as_observation":True
            })
    if len(trials)!=64 or len({t["word"] for t in trials})!=64:
        raise ValueError("repeated or incomplete preregistered native multi-edge words")
    return {
        "kind":"AB_NATIVE_MULTI_UNKNOWN_EDGE_FROZEN_V1","protocol":PROTOCOL,
        "provenance":"Source-verified independent official LS20 raw observations",
        "prior_frontier_source_sha256":FRONTIER_SHA256,
        "known_edges_independently_replayed":84,
        "known_reachable_positions":27,
        "two_new_edge_candidates_exhaustively_tested":52,
        "three_new_edge_candidates_total":120,
        "three_new_edge_candidates_preselected":12,
        "native_holdout_trials":trials,
        "estimated_native_actions":sum(len(t["word"]) for t in trials),
        "common_native_root_sha16":root_hash,
        "geometry_rule_not_retrained":True,
        "observed_hidden_state":False,"F3_state_mapping":False,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--prior",type=Path,required=True)
    p.add_argument("--last",type=Path,required=True)
    p.add_argument("--frontier",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    result=freeze(a.prior,a.last,a.frontier)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2)+"\n")
    print("AB_NATIVE_FROZEN_MULTI_EDGE "+json.dumps({
        "two_edge_trials":52,"three_edge_trials":12,
        "source_edges":result["known_edges_independently_replayed"],
        "native_actions_planned":result["estimated_native_actions"]},sort_keys=True))

if __name__=="__main__":
    main()
