"""Typed visible-program synthesis for ARC-like interactive frames.

Induces, from pixels only:
- colored rectangular routines;
- tiny unfilled variable slots;
- solid palette tokens as literals;
- hollow palette tokens matching routine colors as calls;
- pre-filled solid literals and hollow calls inside routines;
- a top target color sequence.

Then solves slot assignments so recursively expanded program output equals target.
No game IDs, fixed coordinates, or banked solution paths.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from copy import deepcopy
import numpy as np
from latent import grid, perceive
from program_schema import _frame_candidates, _clusters_inside, _bg

def _is_solid_cluster(c):
    area=(c["x1"]-c["x0"]+1)*(c["y1"]-c["y0"]+1)
    return c["size"]==area

def _clean_frames(frame):
    g=grid(frame); bg=_bg(g)
    raw=[r for r in _frame_candidates(frame)
         if r[0]!=bg and 8<=r[2] and r[4]<=52]
    # Remove near-duplicate same-geometry frames by preferring the outer/higher coverage;
    # distinct colors with nested borders are kept only if each encloses meaningful syntax later.
    return raw

def _palette(frame, routine_colors):
    s=perceive(frame); bg=_bg(grid(frame))
    literal=defaultdict(list)
    calls=defaultdict(list)
    tokens=[]
    for o in s.objects:
        w=o.x1-o.x0+1; h=o.y1-o.y0+1
        if o.y0<54 or not (3<=w<=7 and 3<=h<=7) or o.size<8 or o.color==bg:
            continue
        solid=(o.size==w*h)
        xy=(o.center2[0]//2,o.center2[1]//2)
        tok={"color":o.color,"xy":xy,"solid":solid,"size":o.size,"bbox":(o.x0,o.y0,o.x1,o.y1)}
        tokens.append(tok)
        if solid:
            literal[o.color].append(xy)
        elif o.color in routine_colors:
            calls[o.color].append(xy)
    for pool in (literal,calls):
        for color in pool:
            pool[color].sort()
    return dict(literal),dict(calls),sorted(tokens,key=lambda t:t["xy"][0])

def _target_rows(frame):
    s=perceive(frame)
    bg=_bg(grid(frame))
    refs=[]
    for o in s.objects:
        w=o.x1-o.x0+1;h=o.y1-o.y0+1
        if o.color==bg: continue
        # Target exemplars are compact outer frames in the top band.
        if o.y1>15 or not (5<=w<=7 and 5<=h<=7) or o.size<12: continue
        refs.append(o)
    by_y=defaultdict(list)
    for o in refs:
        by_y[o.center2[1]//2].append(o)
    rows=[]
    for y in sorted(by_y):
        row=sorted(by_y[y],key=lambda o:o.center2[0])
        if len(row)>=2:
            rows.append([o.color for o in row])
    return rows

def _target(frame, token_colors=None):
    rows=_target_rows(frame)
    return [c for row in rows for c in row]

def _parse_routines(frame, frames):
    g=grid(frame)
    # Infer variable-slot color from repeated smallest compact components inside routine frames.
    tiny=Counter()
    frame_colors={r[0] for r in frames}
    all_clusters={}
    for r in frames:
        cs=_clusters_inside(g,r); all_clusters[id(r)]=cs
        for c in cs:
            w=c["x1"]-c["x0"]+1;h=c["y1"]-c["y0"]+1
            if c["color"] not in frame_colors and w<=3 and h<=3 and c["size"]<=9:
                tiny[(c["color"],c["size"],w,h)]+=1
    if not tiny:return None,None
    # Most repeated tiny syntax token; break ties toward smaller area.
    terminal_sig=max(tiny,key=lambda k:(tiny[k],-k[1]))
    terminal_color=terminal_sig[0]

    routines={}
    for r in frames:
        rc=r[0]
        elems=[]
        cs=all_clusters[id(r)]
        for c in cs:
            w=c["x1"]-c["x0"]+1;h=c["y1"]-c["y0"]+1
            xy=(c["cx"],c["cy"])
            if c["color"]==terminal_color and w<=3 and h<=3 and c["size"]<=9:
                elems.append({"kind":"var","slot":(rc,xy[0],xy[1]),"xy":xy})
                continue
            if w<=6 and h<=6 and c["size"]>=8:
                solid=_is_solid_cluster(c)
                if (not solid) and c["color"] in frame_colors:
                    elems.append({"kind":"call","color":c["color"],"xy":xy})
                elif solid:
                    elems.append({"kind":"literal","color":c["color"],"xy":xy})
        # Program order is visual left-to-right within a routine.
        elems.sort(key=lambda e:(e["xy"][0],e["xy"][1]))
        if elems:
            # Deduplicate frame variants that describe identical routine syntax.
            signature=tuple((e["kind"],e.get("color"),e["xy"]) for e in elems)
            prev=routines.get(rc)
            candidate={"color":rc,"rect":r,"elems":elems,"signature":signature}
            if prev is None:
                routines[rc]=candidate
            else:
                # Prefer tighter frame around syntax.
                pa=(prev["rect"][3]-prev["rect"][1]+1)*(prev["rect"][4]-prev["rect"][2]+1)
                ca=(r[3]-r[1]+1)*(r[4]-r[2]+1)
                if ca<pa:routines[rc]=candidate
    return terminal_color,routines

def _synthesize(routines, root, target, literal_palette, call_palette, *, allow_cycle_prefix=False):
    """Backtracking grammar match with globally shared variable assignments.

    Recursive calls are allowed when they consume target symbols. Re-entering the
    same routine at the same target position is rejected as a zero-progress cycle.
    """
    assignments={}

    def match_routine(rc,pos,assign,stack):
        if rc not in routines:
            return []
        if pos>len(target):
            return []
        key=(rc,pos)
        if key in stack:
            return []
        stack=stack | {key}
        states=[(pos,assign)]
        for elem in routines[rc]["elems"]:
            nxt=[]
            for p,a in states:
                if p==len(target) and allow_cycle_prefix:
                    nxt.append((p,a))
                    continue
                if elem["kind"]=="literal":
                    if p<len(target) and target[p]==elem["color"]:
                        nxt.append((p+1,a))
                elif elem["kind"]=="call":
                    for q,b in match_routine(elem["color"],p,a,stack):
                        nxt.append((q,b))
                else:
                    sid=elem["slot"]
                    if sid in a:
                        typ,col=a[sid]
                        if typ=="literal":
                            if p<len(target) and target[p]==col:
                                nxt.append((p+1,a))
                        else:
                            for q,b in match_routine(col,p,a,stack):
                                nxt.append((q,b))
                    else:
                        if p<len(target):
                            col=target[p]
                            if col in literal_palette:
                                b=dict(a);b[sid]=("literal",col)
                                nxt.append((p+1,b))
                        for col in call_palette:
                            b=dict(a);b[sid]=("call",col)
                            for q,c in match_routine(col,p,b,stack):
                                nxt.append((q,c))
            ded={}
            for q,a in nxt:
                k=(q,tuple(sorted(a.items())))
                ded[k]=(q,a)
            states=list(ded.values())
            if not states:
                break
        return states

    sols=[]
    for pos,a in match_routine(root,0,assignments,set()):
        if pos==len(target):
            sols.append(a)
    return sols

def induce_typed_program(frame):
    frames=_clean_frames(frame)
    if not frames:return None
    terminal_color,routines=_parse_routines(frame,frames)
    if not routines:return None
    routine_colors=set(routines)
    literals,calls,palette_tokens=_palette(frame,routine_colors)
    if not literals and not calls:return None
    target_rows=_target_rows(frame)
    target=[c for row in target_rows for c in row]
    if not target:return None
    periodic_witness=(
        len(target_rows)>=2
        and all(row==target_rows[0] for row in target_rows[1:])
    )

    # Fixed calls establish some non-root routines. Synthesized calls may establish more,
    # so try plausible roots in visual order and require exact target consumption.
    fixed_invoked=set()
    for r in routines.values():
        for e in r["elems"]:
            if e["kind"]=="call":fixed_invoked.add(e["color"])
    roots=[c for c in routines if c not in fixed_invoked]
    roots.sort(key=lambda c:(routines[c]["rect"][2],routines[c]["rect"][1]))

    solutions=[]
    for root in roots:
        for assn in _synthesize(
            routines,root,target,literals,calls,
            allow_cycle_prefix=periodic_witness,
        ):
            need=Counter(assn.values())
            capacity_ok=True
            for (typ,col),n in need.items():
                pool=literals.get(col,[]) if typ=="literal" else calls.get(col,[])
                if n>len(pool):
                    capacity_ok=False
                    break
            if capacity_ok:
                solutions.append((root,assn))
    if not solutions:return None

    # Prefer fewer dynamic calls, then fewer assignments.
    solutions.sort(key=lambda ra:(
        sum(1 for v in ra[1].values() if v[0]=="call"),
        len(ra[1]),
        routines[ra[0]]["rect"][2]
    ))
    root,assn=solutions[0]

    # Emit fill actions in stable routine/slot visual order.
    slots=[]
    for rc,r in sorted(routines.items(),key=lambda kv:(kv[1]["rect"][2],kv[1]["rect"][1],kv[0])):
        for e in r["elems"]:
            if e["kind"]=="var":
                slots.append((rc,e["xy"],e["slot"]))
    plan=[]
    literal_pool={c:list(xs) for c,xs in literals.items()}
    call_pool={c:list(xs) for c,xs in calls.items()}
    for rc,xy,sid in slots:
        if sid not in assn:continue
        typ,col=assn[sid]
        pool=literal_pool.get(col,[]) if typ=="literal" else call_pool.get(col,[])
        if not pool:return None
        pxy=pool.pop(0)
        plan.append(("ACTION6",pxy))
        plan.append(("ACTION6",xy))
    plan.append(("ACTION5",None))

    return {
      "schema":"typed_recursive_program",
      "terminal_color":terminal_color,
      "root":root,
      "target":target,
      "target_rows":target_rows,
      "periodic_witness":periodic_witness,
      "literal_palette":literals,
      "call_palette":calls,
      "routines":{c:{
          "rect":r["rect"],
          "elems":[{k:v for k,v in e.items() if k!="slot"} | ({"slot":e["slot"]} if "slot" in e else {}) for e in r["elems"]]
      } for c,r in routines.items()},
      "assignments":{str(k):v for k,v in assn.items()},
      "plan":plan,
    }
