"""Native FT09 coordinate-action contact followed by original F3 word probes.

Native FT09 advertises ACTION6 (x,y), not two simple A/B controls. Select
spatial *measurement* sites from the untouched actual 64x64 color regions,
intervene once from independent resets, then require TWO DIFFERENT repeatable
native click effects before provisionally naming them A and B.

Selection of coordinates is a measurement plan, not an ARC solution or field
interpretation. F3 word-equality questions are taken from existing source
math, not from solved puzzle routes. All coordinates, before/after native
frames, and resulting counterexamples are retained.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path

import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
import numpy as np

from .native_f3_other_games import define_math_probe_words,frame_grid,digest,native_root
from .native_relation_scan import compact_delta


GAME = "ft09"
MAX_SITES = 12
MAX_COMPONENTS_PER_COLOR = 2
# Fixed before the second experiment: uniform neutral field coverage.
LATTICE_PIXEL_COORDS = (4, 12, 20, 28, 36, 44, 52, 60)


def native_sites(grid):
    """4-connected native color sites; no game-specific semantic labels."""
    colors,counts=np.unique(grid,return_counts=True)
    background=int(colors[np.argmax(counts)])
    seen=np.zeros((64,64),dtype=bool)
    components=defaultdict(list)
    for y in range(64):
        for x in range(64):
            if seen[y,x]:
                continue
            color=int(grid[y,x])
            seen[y,x]=True
            todo=[(x,y)]
            pix=[]
            while todo:
                xx,yy=todo.pop()
                pix.append((xx,yy))
                for nx,ny in ((xx-1,yy),(xx+1,yy),(xx,yy-1),(xx,yy+1)):
                    if (0<=nx<64 and 0<=ny<64 and not seen[ny,nx]
                            and int(grid[ny,nx])==color):
                        seen[ny,nx]=True
                        todo.append((nx,ny))
            if color==background:
                continue
            mx=sum(p[0] for p in pix)/len(pix)
            my=sum(p[1] for p in pix)/len(pix)
            px,py=min(pix,key=lambda p:((p[0]-mx)**2+(p[1]-my)**2,p[1],p[0]))
            components[color].append({
                "native_color":color,"component_cells":len(pix),
                "click":[px,py],
                "bbox":[min(z[0] for z in pix),min(z[1] for z in pix),
                        max(z[0] for z in pix),max(z[1] for z in pix)],
            })
    selected=[]
    for color in sorted(components):
        selected.extend(sorted(components[color],
                               key=lambda c:(-c["component_cells"],
                                             c["click"]))[:MAX_COMPONENTS_PER_COLOR])
    # Spread across native distinct colors, then component sizes, using only
    # source pixel measurements. No known FT09 solution or game IDs.
    selected.sort(key=lambda c:(-c["component_cells"],c["native_color"],c["click"]))
    selected=selected[:MAX_SITES]
    # Add native pixel-grid coverage, including dominant background, without
    # claiming any region is a button, target, or F3 mathematical generator.
    seen_xy={tuple(site["click"]) for site in selected}
    for y in LATTICE_PIXEL_COORDS:
        for x in LATTICE_PIXEL_COORDS:
            if (x,y) in seen_xy:
                continue
            selected.append({
                "native_color":int(grid[y,x]),"component_cells":None,
                "click":[x,y],"bbox":None,
                "site_source":"UNIFORM_NATIVE_PIXEL_LATTICE",
            })
            seen_xy.add((x,y))
    for site in selected:
        site.setdefault("site_source","NATIVE_COLOR_COMPONENT")
    return selected,background


def run_word(arcade,root,roles,word):
    env,obs,initial=native_root(arcade,GAME)
    root_matches=bool(np.array_equal(initial,root))
    frames=[initial]
    transitions=[]
    reason=None
    level=int(getattr(obs,"levels_completed",0))
    for letter in word:
        if 6 not in {int(getattr(a,"value",a))
                         for a in (getattr(obs,"available_actions",[]) or [])}:
            reason="ACTION6_NOT_ADVERTISED"
            break
        x,y=roles[0 if letter=="A" else 1]
        before=frames[-1]
        next_obs=env.step(GameAction.ACTION6,{"x":int(x),"y":int(y)})
        if next_obs is None or getattr(next_obs,"frame",None) is None:
            reason="NO_NATIVE_FRAME_AFTER_CLICK"
            break
        after=frame_grid(next_obs)
        frames.append(after)
        change=compact_delta(before,after)
        transitions.append({
            "letter":letter,"native_click":[x,y],
            "before":digest(before),"after":digest(after),
            "changed_cells":change["changed_cells"],
            "diff_bbox":change["bbox"],
            "levels_completed":int(getattr(next_obs,"levels_completed",0)),
            "state":str(getattr(next_obs,"state",None)),
        })
        obs=next_obs
        if int(getattr(obs,"levels_completed",0))!=level:
            reason="NATIVE_LEVEL_CHANGED"
            break
    return {
        "word":word,"native_actions":len(frames)-1,
        "root_matches":root_matches,
        "status":reason or "COMPLETE",
        "whole_frame":digest(frames[-1]),"transitions":transitions,
    },np.stack(frames)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path(
        "runtime/data/arc3/f3-ft09-native-clicks.json"))
    args=p.parse_args()
    arcade=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    _,first,root=native_root(arcade,GAME)
    initial_actions=[int(getattr(a,"value",a)) for a in
                     (getattr(first,"available_actions",[]) or [])]
    if 6 not in initial_actions:
        raise RuntimeError("FT09 native root no longer exposes ACTION6")
    sites,background=native_sites(root)
    contact=[]
    frames={"root":root}
    acted=0
    for i,site in enumerate(sites):
        wordrow,raw=run_word(arcade,root,(site["click"],site["click"]),"A")
        acted+=wordrow["native_actions"]
        frames[f"site_{i}"]=raw
        contact.append({
            "site_index":i,**site,
            "root_reproduced":wordrow["root_matches"],
            "native_effect":wordrow,
            "changes_visible_frame":(
                wordrow["status"]=="COMPLETE" and
                wordrow["whole_frame"]!=digest(root)),
        })
    # Admit two clicks only when independent resets reproduced their root,
    # they caused changes, and their exact resulting native frames differ.
    effective=[
        r for r in contact if r["root_reproduced"] and
        r["changes_visible_frame"] and
        r["native_effect"]["status"]=="COMPLETE"
    ]
    distinct=[]
    seen=set()
    for row in effective:
        final=row["native_effect"]["whole_frame"]
        if final not in seen:
            distinct.append(row)
            seen.add(final)
    pairs,words,math_refs,all_probes=define_math_probe_words()
    tested_words={}
    comparisons=[]
    roles=None
    if len(distinct)>=2:
        roles=[distinct[0]["click"],distinct[1]["click"]]
        for word in words:
            row,raw=run_word(arcade,root,roles,word)
            acted+=row["native_actions"]
            tested_words[word]=row
            frames["F3_word_"+(word or "EMPTY")]=raw
        for n,(left,right) in enumerate(pairs):
            a,b=tested_words[left],tested_words[right]
            comparable=(a["status"]=="COMPLETE" and b["status"]=="COMPLETE"
                        and a["root_matches"] and b["root_matches"])
            visible=(a["whole_frame"]==b["whole_frame"]) if comparable else None
            predicted=[x["word_equalities"][n] for x in math_refs]
            comparisons.append({
                "math_word_pair":[left,right],
                "provisional_native_click_roles":roles,
                "actual_full_frame_equal":visible,
                "source_original_nine_F3_equal":sum(predicted),
                "strict_direct_injective_visible_consistent_F3_indices":(
                    [i for i,m in enumerate(predicted) if visible==m]
                    if visible is not None else None),
            })
    strict_remaining=list(range(9))
    for row in comparisons:
        c=row["strict_direct_injective_visible_consistent_F3_indices"]
        if c is not None:
            strict_remaining=[i for i in strict_remaining if i in c]
    complete=bool(roles is not None and comparisons and
                  all(c["actual_full_frame_equal"] is not None for c in comparisons))
    record={
        "kind":"ARC3_FT09_NATIVE_COORDINATE_F3_CONTACT",
        "game":GAME,
        "root_full_frame_hash":digest(root),
        "root_native_available_actions":initial_actions,
        "background_native_color_by_pixel_majority":background,
        "spatial_source_sites":sites,
        "predeclared_lattice_pixel_coordinates":list(LATTICE_PIXEL_COORDS),
        "contact":contact,
        "two_distinct_native_click_effects_found":len(distinct)>=2,
        "admitted_click_A_B":roles,
        "source_F3_pairs":[list(x) for x in pairs],
        "source_F3_probe_count":all_probes,
        "native_word_traces":tested_words,
        "math_comparisons":comparisons,
        "strict_direct_injective_visible_remaining_F3_world_indices":
            strict_remaining if complete else None,
        "independent_native_actions":acted,
        "boundary":(
            "Sample coordinates are neutral root-frame measurement, NOT solved "
            "FT09 semantics. Identical frames do not establish same hidden state; "
            "different click locations do not automatically represent mathematical "
            "A/B. All F3 classifications conditional on direct injective "
            "visible-frame identification and complete native traces."
        ),
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(record,indent=2)+"\n")
    np.savez_compressed(args.out.with_suffix(".npz"),**frames)
    print("ARC3_FT09_NATIVE_CLICK_CONTACT "+json.dumps({
        "game":GAME,
        "root_actions":initial_actions,
        "native_background_color":background,
        "sites_tested":len(sites),
        "sites_from_component_colors":sum(x["site_source"]=="NATIVE_COLOR_COMPONENT" for x in sites),
        "sites_from_spatial_lattice":sum(x["site_source"]=="UNIFORM_NATIVE_PIXEL_LATTICE" for x in sites),
        "clicks_change_visible_frame":len(effective),
        "distinct_click_effects":len(distinct),
        "native_A_B_coordinates":roles,
        "observed_first_click_effects":[{
            "site_source":r["site_source"],
            "click":r["click"],
            "root_color":r["native_color"],
            "status":r["native_effect"]["status"],
            "changed_cells":r["native_effect"]["transitions"][0]["changed_cells"],
            "diff_bbox":r["native_effect"]["transitions"][0]["diff_bbox"],
            "level_after":r["native_effect"]["transitions"][0]["levels_completed"],
        } for r in contact if r["native_effect"]["transitions"] and
              r["changes_visible_frame"]],
        "F3_comparisons":[{"words":r["math_word_pair"],
                          "native_equal":r["actual_full_frame_equal"],
                          "F3_equal_worlds":r["source_original_nine_F3_equal"]}
                          for r in comparisons],
        "native_actions":acted,
        "strict_F3_direct_worlds_remaining":(
            len(strict_remaining) if complete else None),
        "raw":str(args.out.with_suffix(".npz")),
        "manifest":str(args.out),
    },sort_keys=True))


if __name__=="__main__":
    main()
