"""Original SDK SP80 Level4: finite two-operation source order comparison.

Hypothesis: after two physically distinct native SDK bar displacements R and U,
the observed board projection and next ACTION5 response may or may not be
independent of the order RU vs UR. Equal-length words finish with the identical
upper selection click, so selection state is not silently left different.

This is a partial finite action-word commutator test over actual original SDK
source observations, not a proof of full-state commutativity or F3 generator map.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from collections import Counter
import numpy as np
from .native_sp80_stage2_baseline import STAGE1_WITNESSES
from .native_sp80_stage4_entry_inventory import run_case
from .native_sp80_stage4_leftmost_upper_contact import measured_actual_native
from .native_sp80_multi_select import parse_plan
from .native_sp80_legal_pairs import hash_frame

PARENTS=(
 ("D3L2_L3U2","6@24,33 2 2 2 3 3","6@34,42 3 3 3 1 1"),
 ("D4L2_L4U2","6@24,33 2 2 2 2 3 3","6@34,42 3 3 3 3 1 1"),
)
RIGHT=(("R1","3"),("R2","3 3"))
UPPER=(("U1","3","6@30,21"),("U6","3 3 3 3 3 3","6@16,21"))
ORDERS=("RU","UR")

def native_word(lower,left,right,upper,terminal,order):
    R="6@46,33 "+right
    U="6@34,21 "+upper
    return " ".join((lower,left,*(R,U) if order=="RU" else (U,R),terminal,"5"))

FROZEN=tuple(
 (f"{parent}_{rn}_{un}_{order}",native_word(lower,left,rword,uword,terminal,order))
 for parent,lower,left in PARENTS
 for rn,rword in RIGHT for un,uword,terminal in UPPER
 for order in ORDERS
)
assert len(FROZEN)==16==len({n for n,_ in FROZEN})
assert tuple(n for n,_ in STAGE1_WITNESSES)==("A","B")
assert all(parse_plan(s)[-1][0]==5 and sum(a==5 for a,xy in parse_plan(s))==1
           and sum(a==6 for a,xy in parse_plan(s))==5 for n,s in FROZEN)
def selected_bbox(arr):
    y,x=np.nonzero(arr==9)
    return ([int(x.min()),int(y.min()),int(x.max()),int(y.max())]
            if len(x) else None)
def observe(root,pre,animation):
    m=measured_actual_native(root,pre,animation)
    max13=m["original_source_cup_max_palette13_pixels"]
    sites=m["first_original_color6_at_3_upper_sites"]
    edges=m["native_first_source_border_changes"]
    return {
       "actual_original_source":m,
       "four_cups_together":m["native_first_simultaneously_full_four_cups"] is not None,
       "topmiddle_max13":max13["top_middle"],
       "leftmost_strand_absent":sites["leftmost_outside_cup"] is None,
       "rightmost_strand_absent":sites["upper_right_outside"] is None,
       "top_and_right_edge_unchanged":edges["top"] is None and edges["right"] is None,
       "original_prepour_hash":hash_frame(pre),
       "original_postpour_hash":hash_frame(animation[-1]),
    }
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    rows=[];raw={};roots=set()
    for name,word in FROZEN:
        actions=parse_plan(word)
        for witness,entry in STAGE1_WITNESSES:
            native,source=run_case(name,witness,entry,word)
            root=source["entry3_34"][-1]
            roots.add(hash_frame(root))
            ledger=native["genuine_original_stage4_action_ledger"]
            complete=len(ledger)==len(actions)
            won=bool(native["official_original_level5_or_WIN"])
            if ([r["genuine_original_action"] for r in ledger]!=
                  [a for a,xy in actions[:len(ledger)]] or
                  (not complete and not won)):
                raise ValueError("original native SDK source action or official finish drift")
            pre=source["stage4_"+str(len(ledger)-1)][-1] if len(ledger)>1 else root
            animation=source["stage4_"+str(len(ledger))]
            seen=observe(root,pre,animation) if ledger[-1]["genuine_original_action"]==5 else None
            row={
               "case":name,"witness":witness,"frozen_original_stage4_word":word,
               "native_stage4_source_actions":len(ledger),
               "native_full_frozen_action_word":complete,
               "official_original_level":native["true_original_sdk_final_level"],
               "official_original_state":native["true_original_sdk_final_state"],
               "official_level5_or_WIN":won,
               "original_stage4_action_ledger":ledger,
               "selected_upper_after_common_terminal_click":selected_bbox(pre) if complete else None,
               "source_observed":seen,
            }
            rows.append(row)
            for phase,stack in source.items():
                raw[f"{name}_{witness}_{phase}"]=stack
            print("ARC4_OPERATOR_ORDER_SOURCE_CASE "+json.dumps({
               "case":name,"witness":witness,"official_level":row["official_original_level"],
               "official_progress":won,"pre_pour_hash":seen["original_prepour_hash"] if seen else None,
               "four_cups":seen["four_cups_together"] if seen else None,
               "topmiddle_max13":seen["topmiddle_max13"] if seen else None,
            },sort_keys=True),flush=True)
    if len(rows)!=32 or roots!={"fa8fd32d3bfd2c8b3ff7765aec373512"}:
        raise AssertionError("original source independent Level4 A/B root / case mismatch")
    for name,_ in FROZEN:
        pair=[r for r in rows if r["case"]==name]
        if len(pair)!=2 or {x["witness"] for x in pair}!={"A","B"} or (
            {k:v for k,v in pair[0].items() if k!="witness"} !=
            {k:v for k,v in pair[1].items() if k!="witness"}
        ):raise ValueError("independent original SDK A/B replay disagreement")
    out={
      "kind":"ORIGINAL_SP80_LEVEL4_NATIVE_ORDER_RU_VS_UR",
      "antecedent_sdk_native_run":40158241960,
      "original_sdk_level4_root_blake2b16":next(iter(roots)),
      "frozen_original_stage4_words":[list(item) for item in FROZEN],
      "original_sdk_resets":len(rows),
      "independent_original_sdk_witnesses":["A","B"],
      "official_native_level5_or_WIN":sum(int(r["official_level5_or_WIN"]) for r in rows),
      "official_sdk_level_histogram":dict(Counter(str(r["official_original_level"]) for r in rows)),
      "native_cases":rows,
      "finite_math_question":"Does original source same final P(board) and next ACTION5 frame response survive word order RU vs UR after identical terminal upper re-selection?",
      "scope":"Native exact finite action-word partial-commutator experiment; no F3 A/B SDK operator homomorphism, no decoded fluid model, only original SDK level>=5/WIN is progress.",
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,indent=2)+"\n",encoding="utf8")
    np.savez_compressed(args.out.with_suffix(".npz"),**raw)
    print("ARC4_NATIVE_ORDER_SUMMARY "+json.dumps({
       "original_sdk_resets":len(rows),
       "official_level5_or_WIN":out["official_native_level5_or_WIN"],
       "same_root":out["original_sdk_level4_root_blake2b16"],
       "pairs":[{"case":r["case"],"official_level":r["official_original_level"],
                 "pre_pour_hash":r["source_observed"]["original_prepour_hash"] if r["source_observed"] else None,
                 "topmiddle_max13":r["source_observed"]["topmiddle_max13"] if r["source_observed"] else None}
                 for r in rows if r["witness"]=="A"],
    },sort_keys=True),flush=True)
if __name__=="__main__":main()
