"""Independent native full-frame verifier of finite ARC4 coupled contact translations."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from collections import Counter
import numpy as np
from .native_sp80_stage4_diagonal_contact import FROZEN,PARENTS,ARMS,right_cmd,upper_cmd
from .native_sp80_multi_select import parse_plan
from .arc4_two_strand_composition_gate import compute,framehash

CONTRACT=Path("work/arc3/arc4_diagonal_contact_contract.json")
DEFAULT=Path("runtime/data/arc4/diagonal-contact/original-diagonal.json")
def require(ok,explanation):
    if not ok: raise ValueError("ORIGINAL_LEVEL4_DIAGONAL_SOURCE_WALL: "+explanation)
def bbox(frame,pixels):
    yy,xx=np.nonzero(frame==9)
    require(len(xx)==pixels,"selected true original native component area differs")
    return [int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max())]
def context():
    c=json.loads(CONTRACT.read_text())
    require(c["schema_version"]==1 and
            c["source_parent_run"]==40171838520 and
            c["source_parent_artifact"]==12590876301 and
            c["genuine_original_level4_root"]=="fa8fd32d3bfd2c8b3ff7765aec373512" and
            c["source_code"]=="work/arc3/native_sp80_stage4_diagonal_contact.py" and
            c["frozen_arms"]==[list(a) for a in ARMS] and
            c["frozen_clean_lower_parents"]==[p for p,*_ in PARENTS] and
            c["expected_genuine_original_sdk_resets"]==24 and
            c["independent_original_sdk_entry_histories"]==["A","B"] and
            len(FROZEN)==12 and len(set(n for n,w in FROZEN))==12,
            "frozen source original native Level4 domain altered")
    for name,word in FROZEN:
        cmds=parse_plan(word)
        require(cmds[-1][0]==5 and
                sum(a==6 for a,xy in cmds)==4 and
                sum(a==5 for a,xy in cmds)==1,
                "real SDK native original action grammar drift")
    require("levels_completed>=5" in c["native_success"],
            "official genuine SDK success oracle absent")
    return c

def inspect(c,p):
    p=Path(p)
    require(p.is_file() and p.with_suffix(".npz").is_file(),
            "real original SDK JSON and full NPZ frames missing")
    j=json.loads(p.read_text())
    require(j["kind"]=="ORIGINAL_SP80_LEVEL4_NATIVE_DIAGONAL_UPPER_RIGHT_CONTACT" and
            j["source_parent_run"]==40171838520 and
            j["true_original_level4_root"]==c["genuine_original_level4_root"] and
            j["frozen_source_words"]==[list(x) for x in FROZEN] and
            j["original_sdk_resets"]==24,
            "native original source identity changed")
    rows={(r["case"],r["witness"]):r for r in j["native_cases"]}
    require(len(rows)==24 and set(rows)=={(n,w) for n,_ in FROZEN
                                           for w in ("A","B")},
            "original independent SDK entries missing")
    originals={};progress=0;levels=Counter();blocked=[];controls=[]
    with np.load(p.with_suffix(".npz"),allow_pickle=False) as npz:
      for name,word in FROZEN:
        parent=next(p for p,*_ in PARENTS if name.startswith(p+"_"))
        tag=name[len(parent)+1:]
        rsteps,usteps=next((r,u) for t,r,u in ARMS if t==tag)
        midbase,Lbase,Lx,My=next((m,l,x,y) for p,m,l,x,y in PARENTS if p==parent)
        right_idx=len(parse_plan(right_cmd(rsteps)))
        middle_idx=len(parse_plan(right_cmd(rsteps)+" 6@24,33 "+midbase+" 4"))
        L_idx=len(parse_plan(right_cmd(rsteps)+" 6@24,33 "+midbase+
                            " 4 6@34,42 "+Lbase+" 4"))
        top_idx=len(parse_plan(right_cmd(rsteps)+" 6@24,33 "+midbase+
                              " 4 6@34,42 "+Lbase+" 4 "+upper_cmd(usteps)))
        expected={
            "right":[41-3*rsteps,32,55-3*rsteps,34],
            "middle":[17,My,25,My+2],
            "L":[Lx+3,35,Lx+8,40],
            "upper":[29-3*usteps,20,40-3*usteps,22],
        }
        witnesses=[]
        for w in ("A","B"):
          r=rows[(name,w)];actions=parse_plan(word);led=r["actual_native_receipts"]
          require(r["frozen_original_stage4_word"]==word and
                  len(led)>0 and len(led)<=len(actions) and
                  r["actual_source_right_action_index"]==right_idx and
                  r["actual_source_middle_action_index"]==middle_idx and
                  r["actual_source_L_action_index"]==L_idx and
                  r["actual_source_upper_action_index"]==top_idx,
                  "native source factor indices and action receipt count differ")
          root=npz[f"{name}_{w}_entry3_34"][-1]
          require(root.shape==(64,64) and
                  framehash(root)==c["genuine_original_level4_root"],
                  "not actual original SDK Level4 root")
          previous=root
          for i,((act,click),item) in enumerate(zip(actions,led),1):
            frames=npz[f"{name}_{w}_stage4_{i}"]
            require(frames.ndim==3 and frames.shape[1:]==(64,64) and
                    len(frames)==item["original_sdk_frame_stack_count"] and
                    item["genuine_original_action"]==act and
                    item["real_native_click_xy"]==(list(click) if click is not None else None) and
                    act in item["original_legal_actions_before"] and
                    item["original_sdk_level_before"]>=4 and
                    item["source_frame_before_blake2b16"]==framehash(previous) and
                    item["source_frame_after_blake2b16"]==framehash(frames[-1]),
                    "genuine SDK full source action frames/hash/click/legal receipts differ")
            if click is not None:
              x,y=click
              require(item["original_source_pixel_before_click"]==int(previous[y,x]),
                      "original native clicked palette pixel is not the recorded one")
            previous=frames[-1]
          state=led[-1]
          require(r["official_original_sdk_level"]==state["original_sdk_level_after"]
                and r["official_original_sdk_state"]==state["original_sdk_state_after"]
                and r["official_original_level5_or_WIN"]==
                  (r["official_original_sdk_level"]>=5 or r["official_original_sdk_state"]=="WIN"),
                "native official SDK state/action receipts differ")
          progress+=int(r["official_original_level5_or_WIN"])
          levels[str(r["official_original_sdk_level"])]+=1
          if not r["original_word_complete"]:
            require(r["official_original_level5_or_WIN"] and
                    r["measured_original_source"] is None,
                    "unverified early exit without SDK official advance")
            witnesses.append({"witness":w,"early_advance":True,
                              "official_level":r["official_original_sdk_level"]})
            continue
          require(len(led)==len(actions) and
                  state["genuine_original_action"]==5,
                  "genuine final ACTION5 source missing")
          observed={}
          for key,idx,size in (("right",right_idx,45),
                               ("middle",middle_idx,27),
                               ("L",L_idx,27),
                               ("upper",top_idx,36)):
            measured=bbox(npz[f"{name}_{w}_stage4_{idx}"][-1],size)
            require(measured==r["actual_selected_"+key+"_bbox"] if key in ("right","upper","middle") else
                    measured==r["actual_selected_L_bbox"],
                    "original source selected geometry differs from saved original action")
            if measured!=expected[key]:
              if measured[1]==expected[key][1] and measured[3]==expected[key][3]:
                blocked.append([name,w,key,measured,expected[key]])
              else:
                require(False,"unexpected original native action selected component geometry")
            observed[key]=measured
          pre=npz[f"{name}_{w}_stage4_{len(actions)-1}"][-1]
          pour=npz[f"{name}_{w}_stage4_{len(actions)}"]
          obs=compute(root,pre,pour)
          saved=r["measured_original_source"]
          require(saved is not None,"missing genuine source measurement")
          source=saved["genuine_original_source_metrics"]
          require(source["original_source_cup_first_full_frames"]==obs["cups_first"] and
                  source["original_source_cup_max_palette13_pixels"]==obs["cups_max"] and
                  source["native_first_simultaneously_full_four_cups"]==obs["first_four"] and
                  all((None if source["first_original_color6_at_3_upper_sites"][n] is None
                       else source["first_original_color6_at_3_upper_sites"][n]["native_original_frame"])==f
                       for n,f in obs["site_first"].items()) and
                  all((None if source["native_first_source_border_changes"][n] is None
                       else source["native_first_source_border_changes"][n]["native_original_frame"])==f
                       for n,f in obs["border_first"].items()),
                  "native source cup, strand or boundary outcomes disagreed")
          first={}
          for x in (5,8,11,14,17,20):
            first[f"x{x}_{x+2}"]=next(
                (i for i,frame in enumerate(pour)
                 if np.any((pre[5:8,x:x+3]!=6)&(frame[5:8,x:x+3]==6))),
                None)
          require(first==saved["source_upper_left_new6_first_by_3px_band"] and
                  saved["native_cup_max_palette13"]==obs["cups_max"] and
                  saved["native_four_cups_together"]==(obs["first_four"] is not None) and
                  saved["prepour_original_hash"]==framehash(pre) and
                  saved["final_original_hash"]==framehash(pour[-1]),
                  "independent native source pixel band/cup/hash observation mismatch")
          witnesses.append({"witness":w,"official_level":r["official_original_sdk_level"],
                            "source_selected":observed,
                            "original_cups":obs["cups_max"],"four_cups_frame":obs["first_four"],
                            "new_palette6_upper_left":first,
                            "left_strand_absent":obs["P_leftmost_absent"],
                            "right_strand_absent":obs["Q_rightmost_absent"],
                            "top_border":obs["border_first"]["top"],
                            "right_border":obs["border_first"]["right"]})
        require(len(witnesses)==2 and witnesses[0]["witness"]=="A" and witnesses[1]["witness"]=="B"
                and {k:v for k,v in witnesses[0].items() if k!="witness"}==
                    {k:v for k,v in witnesses[1].items() if k!="witness"},
                "genuine original independent A/B game replay differs")
        originals[name]=witnesses[0]
    require(progress==j["official_level5_or_WIN_count"],
            "official SDK advance count drift")
    for parent,*_ in PARENTS:
      ctrl=originals[parent+"_C22"]
      if (ctrl.get("new_palette6_upper_left",{}).get("x14_16") is None or
          ctrl.get("original_cups",{}).get("top_middle")!=45 or
          ctrl.get("four_cups_frame") is None or ctrl.get("official_level")!=4):
        controls.append({"case":parent+"_C22","observed":ctrl})
    relations=[{"lower_context":parent,
                "source_controls":{tag:originals[parent+"_"+tag] for tag,r,u in ARMS}}
               for parent,*_ in PARENTS]
    return {"kind":"ORIGINAL_SP80_LEVEL4_DIAGONAL_SOURCE_VERIFIED",
            "real_original_sdk_resets":len(rows),"official_sdk_level_histogram":dict(levels),
            "official_native_level5_or_WIN_count":progress,
            "state":"REPLICATION_REQUIRED" if progress else
                    "WALL_CONTROL_DRIFT" if controls else "PARTIAL",
            "historic_control_drift":controls,
            "real_native_source_pose_discrepancies":blocked,
            "finite_right_upper_correspondence":relations,
            "math_scope":"Finite authentic original SDK R/U paired action-word source relation with fixed compensated L/middle. No F3 generator mapping, engine model or image-only goal.",
            "next_movement":c["next_progress"] if progress else c["next_no_progress"],
            "walls":c["walls"]}
def main():
    p=argparse.ArgumentParser();p.add_argument("phase",choices=("pre","post"))
    p.add_argument("--result",type=Path,default=DEFAULT)
    args=p.parse_args();c=context()
    if args.phase=="pre":
        print("ARC4_DIAGONAL_PREFLIGHT "+json.dumps({"contract":c["id"],"resets":24},sort_keys=True))
    else:
        result=inspect(c,args.result)
        args.result.with_suffix(".protocol.json").write_text(json.dumps(result,indent=2)+"\n")
        print("ARC4_DIAGONAL_VERIFIED "+json.dumps(result,sort_keys=True),flush=True)
if __name__=="__main__":main()
