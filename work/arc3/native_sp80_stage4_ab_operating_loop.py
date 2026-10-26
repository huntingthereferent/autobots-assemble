"""ARC original SDK: error-led A/B movement, not externally replayed answers.

A/B is the operating method here: make a real move, observe its failure,
put a second real move against it, and let the *observed discrepancy*
generate the next move. Do not reject cases because they worsen cups
or accidentally click a nonselectable pixel: those are evidence.
Only original Arcade(NORMAL) SDK levels_completed >=5 or WIN is an
actual Level4 game advance.

This runner NEVER loads any published solution/action words and never
imports the separate public-positive-replay modules. Seed is exclusively
the repository's owned, historically FAILED BASE geometry.
The finite F3-48 math is untouched; native A/B movement is not
gated behind a purported F3-to-SDK mapping.
"""
from __future__ import annotations
import argparse,json
from collections import deque
from hashlib import blake2b
from pathlib import Path
import numpy as np
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_entry_inventory import run_case
from .native_sp80_stage4_four_cup_followup import BASE,CUPS
from .native_sp80_multi_select import parse_plan
from .native_sp80_legal_pairs import hash_frame

MAX_AB_ROUNDS=3
assert len(parse_plan(BASE))==21 and len(STAGE1_WITNESSES)==2

def hasharray(arr):
    return blake2b(np.ascontiguousarray(arr).tobytes(),digest_size=16).hexdigest()

def examine(root,pre,frames,after):
    rects={"top":(slice(2,5),slice(5,59)),
           "right":(slice(5,59),slice(59,62))}
    warnings={}
    for label,(yy,xx) in rects.items():
        baseline=(pre[yy,xx]==1)
        all_hits=[]
        for t,frame in enumerate(frames):
            coords=np.argwhere(baseline & (frame[yy,xx]==14))
            for y,x in coords:
                all_hits.append((int(t),int(x)+xx.start,int(y)+yy.start))
        warnings[label]={
          "first_returned_contact":list(min(all_hits)) if all_hits else None,
          "distinct_pixels_hit":len({(x,y) for t,x,y in all_hits}),
        }
    counts=[]
    for frame in frames:
        current={}
        for label,(x0,y0,x1,y1) in CUPS.items():
            cup=(root[y0:y1+1,x0:x1+1]==11)
            current[label]=int(np.count_nonzero(
                cup & (frame[y0:y1+1,x0:x1+1]==13)))
        counts.append(current)
    best_index=max(range(len(counts)),key=lambda n:sum(counts[n].values()))
    best=counts[best_index]
    missing=[name for name,v in best.items() if v<45]
    first_top=warnings["top"]["first_returned_contact"]
    first_right=warnings["right"]["first_returned_contact"]
    if first_top:
        error={"kind":"actual_top_floor_contact","native_xy":first_top[1:],
               "first_returned_frame":first_top[0]}
    elif first_right:
        error={"kind":"actual_right_floor_contact","native_xy":first_right[1:],
               "first_returned_frame":first_right[0]}
    elif missing:
        target=missing[0];x0,y0,x1,y1=CUPS[target]
        error={"kind":"observed_unfilled_cup","cup":target,
               "native_xy":[(x0+x1)//2,(y0+y1)//2],
               "missing_source_pixels":45-best[target]}
    else:
        error={"kind":"unresolved_native_outcome","native_xy":[32,21]}
    score={
        "official_sdk_level":int(after["true_original_sdk_final_level"]),
        "official_sdk_state":after["true_original_sdk_final_state"],
        "official_level5_or_WIN":bool(after["official_original_level5_or_WIN"]),
        "four_native_cup_peak_counts":best,
        "four_native_cup_peak_frame":best_index,
        "floor_lines":warnings,
        "observed_error":error,
        "source6_full_animation_digest":hasharray(frames==6),
        "original_full_animation_digest":hasharray(frames),
    }
    return score

def source_bars(image):
    """Find real source palette8/9 native connected objects; NO idealized world."""
    out=[];seen=np.zeros((64,64),dtype=bool)
    palette=(image==8)|(image==9)
    for yy,xx in np.argwhere(palette):
        y,x=int(yy),int(xx)
        if seen[y,x]:continue
        seen[y,x]=True;queue=deque([(y,x)]);cells=[]
        while queue:
            cy,cx=queue.popleft();cells.append((cy,cx))
            for ny,nx in ((cy-1,cx),(cy+1,cx),(cy,cx-1),(cy,cx+1)):
                if 0<=ny<64 and 0<=nx<64 and palette[ny,nx] and not seen[ny,nx]:
                    seen[ny,nx]=True;queue.append((ny,nx))
        if len(cells)>=6:
            cy,cx=min(cells,key=lambda p:(abs(p[0]-(min(y for y,x in cells)+max(y for y,x in cells))/2)+
                                           abs(p[1]-(min(x for y,x in cells)+max(x for y,x in cells))/2)))
            out.append({"click":[cx,cy],"color_before_click":int(image[cy,cx]),
                        "cells":len(cells)})
    return out

def target_object(previous,used):
    err=previous["measure"]["observed_error"]
    ex,ey=err["native_xy"]
    bars=source_bars(previous["pre"])
    if not bars:raise RuntimeError("No observed selectable source objects: preserve error")
    def rank(b):
        x,y=b["click"]
        return (b["click"] in used, b["color_before_click"]!=8,
                abs(x-ex)+abs(y-ey),-b["cells"])
    return sorted(bars,key=rank)[0]

def one(case,witness,stage1,word):
    """A real trial is allowed to fail or make the target observation worse."""
    result,source=run_case(case,witness,stage1,word)
    root=source["entry3_34"][-1]
    ledger=result["genuine_original_stage4_action_ledger"]
    poured=[r for r in ledger if r["genuine_original_action"]==5]
    if not poured:
        return {"case":case,"witness":witness,"word":word,
                "mistake":{"kind":"actual_sdk_no_pour","receipts":ledger},
                "measure":{"official_sdk_level":result["true_original_sdk_final_level"],
                           "official_sdk_state":result["true_original_sdk_final_state"],
                           "official_level5_or_WIN":result["official_original_level5_or_WIN"],
                           "observed_error":{"kind":"actual_sdk_no_pour","native_xy":[32,21]}},
                "pre":root,"frames":None,"source":source,"ledger":ledger}
    step=poured[-1]["index"];pre=source[f"stage4_{step-1}"][-1]
    frames=source[f"stage4_{step}"]
    m=examine(root,pre,frames,result)
    return {"case":case,"witness":witness,"word":word,
            "measure":m,"pre":pre,"frames":frames,
            "source":source,"ledger":ledger,
            "native_root":result["native_original_stage4_entry"]["original_sdk_stage4_root_blake2b16"]}

def describe(prev,trial):
    a=prev["measure"];b=trial["measure"]
    if trial["frames"] is None:
        return {"changed":"SDK gave no animation","error":b["observed_error"]}
    before=prev["frames"];after=trial["frames"]
    peak=sum(b["four_native_cup_peak_counts"].values())
    pa=sum(a["four_native_cup_peak_counts"].values())
    t=a["floor_lines"]["top"]["distinct_pixels_hit"]
    nt=b["floor_lines"]["top"]["distinct_pixels_hit"]
    return {
        "original_cup_peak_change":peak-pa,
        "original_top_spill_changed_pixels":nt-t,
        "original_source6_animation_changed":
            (a["source6_full_animation_digest"]!=b["source6_full_animation_digest"]),
        "real_sdk_level_change":b["official_sdk_level"]-a["official_sdk_level"],
        "next_error":b["observed_error"],
    }

def select_branch(parent,left,right):
    """A/B follows changes, including failures, not a preapproved good result."""
    options=[left,right]
    for p in options:
        if p["measure"]["official_level5_or_WIN"]:return p,"verified original SDK advance"
    diffs=[describe(parent,p) for p in options]
    # Learn first from a new mistake. A bad move that changes the water
    # or exposes a missing cup is retained, not filtered out.
    for candidate,d in zip(options,diffs):
        if d.get("original_source6_animation_changed") or (
            d.get("original_cup_peak_change",0)!=0):
            return candidate,"follow new original source mistake (may worsen)"
    for candidate,d in zip(options,diffs):
        if d.get("original_top_spill_changed_pixels",0)!=0:
            return candidate,"follow observed floor difference"
    return options[-1],"A/B returned same observed water; next locate different source bar"

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    main_witness,main_entry=STAGE1_WITNESSES[0]
    reference=one("owned_original_wrong_BASE",main_witness,main_entry,BASE+" 5")
    roots={reference.get("native_root")}
    trials=[reference];relations=[];chosen=reference
    used=[];rooted_prefix=BASE
    for round_no in range(MAX_AB_ROUNDS):
        if chosen["measure"]["official_level5_or_WIN"]:break
        bar=target_object(chosen,used)
        used.append(bar["click"])
        x,y=bar["click"]
        mistake=chosen["measure"]["observed_error"]
        dirs=(3,4) if mistake["kind"] in ("actual_top_floor_contact","actual_right_floor_contact") else (1,2)
        pair=[]
        for side,action in (("A",dirs[0]),("B",dirs[1])):
            word=f"{rooted_prefix} 6@{x},{y} {action} 5"
            trial=one(f"mistake_{round_no}_{side}",main_witness,main_entry,word)
            trials.append(trial)
            roots.add(trial.get("native_root"))
            pair.append(trial)
        next_tr,reason=select_branch(chosen,*pair)
        comparisons=[{"candidate":v["case"],"actual_sdk_next":v["measure"],
                      "A_B_difference_from_parent":describe(chosen,v)}
                     for v in pair]
        relations.append({
           "iteration":round_no,"observed_parent_mistake":mistake,
           "source_bar_selected_from_actual_original_pixels":bar,
           "two_opposing_original_actions":list(dirs),
           "original_AB_pair":comparisons,
           "continued_from":next_tr["case"],"why":reason,
        })
        print("SP80_MISTAKE_LED_AB_MOVE "+json.dumps({
           "iteration":round_no,"parent_error":mistake,
           "bar":bar,"A_B_differences":[c["A_B_difference_from_parent"] for c in comparisons],
           "continued_from":next_tr["case"],"why":reason,
        },sort_keys=True),flush=True)
        chosen=next_tr
        rooted_prefix=chosen["word"].rsplit(" 5",1)[0]
    # Repeat the actual chosen outcome under the other independent
    # entrance to check reproducibility without vetoing earlier mistakes.
    second_witness,second_entry=STAGE1_WITNESSES[1]
    replicate=one("second_independent_entry_of_chosen_movement",
                  second_witness,second_entry,chosen["word"])
    trials.append(replicate)
    if replicate["measure"]["official_sdk_level"]!=chosen["measure"]["official_sdk_level"]:
        raise AssertionError("Independent original stage entry changed official result")
    raw={}
    saved=[]
    for t in trials:
        for key,stack in t["source"].items():
            if key=="entry3_34" or key.startswith("stage4_"):
                raw[f"{t['case']}_{t['witness']}_{key}"]=stack
        saved.append({k:v for k,v in t.items() if k not in ("source","pre","frames")})
    report={
       "kind":"ORIGINAL_SP80_NATIVE_MISTAKE_LED_AB_ACTIVE_CORRECTION",
       "origin":"owned unsuccessful 21-action BASE, not the external published solution",
       "operating_protocol":"actual A/B mistakes -> compare original SDK relationships -> use difference for the next action",
       "original_stage4_root_hashes":sorted(x for x in roots if x),
       "actual_sdk_games_run":len(trials),
       "rooted_movement_and_corrections":relations,
       "all_genuine_native_sdk_trial_receipts":saved,
       "chosen_result":chosen["case"],
       "actual_owned_method_progressions":[t["case"] for t in trials if
           t["measure"]["official_level5_or_WIN"]],
       "external_solutions_read_or_imported_by_runner":False,
       "math_scope":"Native rooted A/B is used directly. The separate exact F3-48 math is not rewritten or falsely mapped to native actions.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**raw)
    print("SP80_MISTAKE_LED_AB_RESULT "+json.dumps({
        k:v for k,v in report.items() if k not in
        ("rooted_movement_and_corrections","all_genuine_native_sdk_trial_receipts")
    },sort_keys=True),flush=True)

if __name__=="__main__":main()
