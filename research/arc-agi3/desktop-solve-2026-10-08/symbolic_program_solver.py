"""Generic symbolic program solver over a latent ARC3 visual state.

No game ids. No banked action sequences.

Model:
- top repeated ring row = target terminal color sequence;
- bottom row = finite single-use programming resources;
  * solid token => terminal color
  * ring token => call to routine of same frame color
- framed program regions = routines;
- small red/color-2 cells = writable variables;
- solid symbols inside a routine = fixed terminals;
- ring symbols inside a routine = fixed calls.

A variable consumes exactly one palette resource when programmed.
Routine definitions are shared: multiple calls reuse the same body assignment.
The root routine is a frame whose color is not a callable palette color.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from latent_state import LatentView, Component


@dataclass(frozen=True)
class Resource:
    idx: int
    color: int
    kind: str  # terminal | call
    xy: tuple[int,int]


@dataclass(frozen=True)
class Term:
    kind: str  # var | terminal | call
    value: Any # xy for var, color otherwise


@dataclass(frozen=True)
class RoutineDef:
    color: int
    frame_box: tuple[int,int,int,int]
    terms: tuple[Term,...]


@dataclass(frozen=True)
class ProgramModel:
    target: tuple[int,...]
    resources: tuple[Resource,...]
    routines: tuple[RoutineDef,...]
    root_color: int


def _contains(outer:Component, inner:Component)->bool:
    return (outer.x0<=inner.x0 and outer.y0<=inner.y0 and
            inner.x1<=outer.x1 and inner.y1<=outer.y1)


def _component_near(v:LatentView,color:int,center:tuple[int,int],band:tuple[int,int])->Component|None:
    x,y=center
    cand=[c for c in v.components if c.color==color and c.y0>=band[0]-1 and c.y1<=band[1]+1
          and c.x0<=x<=c.x1 and c.y0<=y<=c.y1 and c.size<=32]
    if not cand:return None
    return max(cand,key=lambda c:c.size)


def parse_program(v:LatentView)->ProgramModel|None:
    groups=sorted([g for g in v.horizontal_groups if len(g.colors)>=3],key=lambda g:g.y0)
    if len(groups)<2:return None

    # Target/palette pair: same arity, widest vertical separation, palette
    # covers target alphabet.
    best=None
    for i,t in enumerate(groups):
        for j,p in enumerate(groups):
            if j<=i:continue
            # Palette need not contain every target terminal: routines can carry
            # fixed terminals internally. Identify the boundary rows structurally
            # by maximum vertical separation, preferring richer symbol rows.
            score=(min(len(t.colors),len(p.colors)),p.y0-t.y0,len(t.colors)+len(p.colors))
            if best is None or score>best[0]:best=(score,t,p)
    if best is None:return None
    _,target_g,palette_g=best

    resources=[]
    for i,(color,center,member) in enumerate(zip(palette_g.colors,palette_g.centers,palette_g.member_pixels)):
        c=_component_near(v,color,center,(palette_g.y0,palette_g.y1))
        if c is None:continue
        kind="terminal" if c.fill>=0.95 else "call"
        resources.append(Resource(i,color,kind,member))
    if len(resources)<len(palette_g.colors):
        return None
    call_colors={r.color for r in resources if r.kind=="call"}

    # Frame-like routine components in the program region.
    frames=[c for c in v.components
            if target_g.y1 < c.y0 and c.y1 < palette_g.y0
            and c.width>=12 and c.height>=8 and c.size>=20 and c.fill<0.55]
    # Remove very large wrappers if a tighter same-area routine frame exists.
    # Keep one candidate per (color,box).
    uniq={}
    for f in frames:uniq[(f.color,f.box)]=f
    frames=list(uniq.values())
    if not frames:return None

    routines=[]
    for f in frames:
        inside=[c for c in v.components if c is not f and _contains(f,c) and c.size<=24]
        # Candidate token components.
        token_comps=[]
        for c in inside:
            if c.color==2 and c.size<=9:
                token_comps.append((c,"var"))
            elif c.color in call_colors and c.fill<0.95 and c.size>=8:
                token_comps.append((c,"call"))
            elif c.fill>=0.95 and 9<=c.size<=24 and c.color not in (4,5):
                token_comps.append((c,"terminal"))
        # Suppress nested components at the same center, preferring call/terminal.
        token_comps.sort(key=lambda ck:(ck[0].cx2,ck[0].cy2,-ck[0].size))
        selected=[]
        for c,k in token_comps:
            x,y=c.cx2//2,c.cy2//2
            replaced=False
            for q,(pc,pk) in enumerate(selected):
                px,py=pc.cx2//2,pc.cy2//2
                if abs(px-x)<=1 and abs(py-y)<=1:
                    rank={"var":0,"terminal":1,"call":2}
                    if rank[k]>rank[pk] or (rank[k]==rank[pk] and c.size>pc.size):
                        selected[q]=(c,k)
                    replaced=True;break
            if not replaced:selected.append((c,k))
        selected.sort(key=lambda ck:(ck[0].cx2//2,ck[0].cy2//2))
        if not selected:continue
        terms=[]
        for c,k in selected:
            if k=="var":
                terms.append(Term("var",(c.cx2//2,c.cy2//2)))
            else:
                terms.append(Term(k,c.color))
        routines.append(RoutineDef(f.color,f.box,tuple(terms)))

    if not routines:return None

    # Target rows may wrap vertically when the flattened sequence is wider than
    # the display. All repeated-symbol rows above the first routine frame belong
    # to the target, in visual row-major order.
    first_routine_y=min(r.frame_box[1] for r in routines)
    target_rows=[g for g in groups if g.y1 < first_routine_y and g.y1 < palette_g.y0]
    target_rows=sorted(target_rows,key=lambda g:(g.y0,g.centers[0][0]))
    target_colors=tuple(c for g in target_rows for c in g.colors)
    if not target_colors:
        target_colors=target_g.colors

    # Callable routine colors should have a matching frame; normally the root is
    # the frame not exposed as a call resource. Fully recursive programs can make
    # every routine callable, in which case visual top-to-bottom order identifies
    # the entry routine.
    by_color={r.color:r for r in routines}
    callable_present={c for c in call_colors if c in by_color}
    roots=[r for r in routines if r.color not in callable_present]
    root=min(roots if roots else routines,key=lambda r:(r.frame_box[1],r.frame_box[0]))

    # Only retain routines reachable by color lookup plus root; duplicate frame
    # colors are unsupported for now.
    dedup={}
    for r in routines:
        if r.color not in dedup or r.frame_box[1]<dedup[r.color].frame_box[1]:
            dedup[r.color]=r
    dedup[root.color]=root
    return ProgramModel(target_colors,tuple(resources),tuple(dedup.values()),root.color)


def solve_program(model:ProgramModel):
    routines={r.color:r for r in model.routines}
    target=model.target
    resources={r.idx:r for r in model.resources}

    # assignment: variable coordinate -> resource idx
    def apply_term(term,pos,assign,avail,depth):
        # Execution is judged against a finite visible target. Recursive programs
        # may continue beyond it, so once the target prefix is fully matched the
        # remaining call stack is irrelevant to this witness.
        if pos==len(target):
            return [(pos,assign,avail)]
        if pos>len(target) or depth>len(target)+8:
            return []
        if term.kind=="terminal":
            return [(pos+1,assign,avail)] if pos<len(target) and target[pos]==term.value else []
        if term.kind=="call":
            if term.value not in routines:return []
            return match_routine(term.value,pos,assign,avail,depth+1)
        xy=term.value
        if xy in assign:
            res=resources[assign[xy]]
            kind="terminal" if res.kind=="terminal" else "call"
            return apply_term(Term(kind,res.color),pos,assign,avail,depth+1)

        outs=[]
        # Deterministic ordering: terminals matching current target first, then calls.
        ids=sorted(avail,key=lambda rid:(0 if resources[rid].kind=="terminal" and pos<len(target) and resources[rid].color==target[pos] else 1,
                                         0 if resources[rid].kind=="call" else 1,rid))
        for rid in ids:
            res=resources[rid]
            if res.kind=="terminal" and (pos>=len(target) or res.color!=target[pos]):
                continue
            na=dict(assign);na[xy]=rid
            nv=set(avail);nv.remove(rid)
            tk=Term("terminal" if res.kind=="terminal" else "call",res.color)
            for np,aa,vv in apply_term(tk,pos,na,nv,depth+1):
                outs.append((np,aa,vv))
        return outs

    def match_terms(terms,i,pos,assign,avail,depth):
        if pos==len(target):
            return [(pos,assign,avail)]
        if i==len(terms):
            return [(pos,assign,avail)]
        outs=[]
        for np,aa,vv in apply_term(terms[i],pos,assign,avail,depth):
            outs.extend(match_terms(terms,i+1,np,aa,vv,depth))
        return outs

    def match_routine(color,pos,assign,avail,depth):
        r=routines.get(color)
        if r is None:return []
        return match_terms(r.terms,0,pos,assign,avail,depth)

    all_ids=set(resources)
    results=match_routine(model.root_color,0,{},all_ids,0)
    all_vars={term.value for r in model.routines for term in r.terms if term.kind=="var"}
    for pos,assign,avail in results:
        if pos==len(target) and all_vars.issubset(assign.keys()):
            return assign
    return None
