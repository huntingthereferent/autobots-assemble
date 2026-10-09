from __future__ import annotations

from dataclasses import dataclass
from itertools import permutations
from typing import Optional
import numpy as np
from latent import objects


@dataclass(frozen=True)
class Token:
    kind: str          # "leaf" or "ref"
    color: int

@dataclass
class Position:
    x: int
    y: int
    token: Optional[Token]  # None = empty slot

@dataclass
class Container:
    color: int
    rect: tuple[int,int,int,int]
    positions: list[Position]


def grid(obs):
    a=np.asarray(obs.frame)
    if a.ndim==3:a=a[-1]
    return a.reshape(64,64).astype(np.int16,copy=False)


def _runs(row):
    out=[]
    x=0
    n=len(row)
    while x<n:
        c=int(row[x]); j=x+1
        while j<n and int(row[j])==c:j+=1
        if j-x>=8:
            out.append((c,x,j-1))
        x=j
    return out


def find_rectangles(g):
    # Colored rectangular frames in the central playfield.
    bg=int(np.bincount(g.ravel().astype(np.int64)).argmax())
    hs=[]
    for y in range(10,50):
        for c,x0,x1 in _runs(g[y]):
            if c!=bg and x1-x0+1>=8:
                hs.append((c,y,x0,x1))
    rects=set()
    for i,(c,y0,x0,x1) in enumerate(hs):
        for c2,y1,a,b in hs[i+1:]:
            if c2!=c or a!=x0 or b!=x1:
                continue
            if not (5<=y1-y0<=30):
                continue
            left=np.mean(g[y0:y1+1,x0]==c)
            right=np.mean(g[y0:y1+1,x1]==c)
            if left>=0.70 and right>=0.70:
                rects.add((c,x0,y0,x1,y1))
    # Remove duplicate larger vertical pairings for same exact frame edges when a
    # tighter rectangle with same color/x-span is available.
    rr=sorted(rects,key=lambda r:((r[3]-r[1])*(r[4]-r[2]),r[2]))
    keep=[]
    for r in rr:
        c,x0,y0,x1,y1=r
        # exact border should have substantial colored perimeter
        per=[]
        per.extend(g[y0,x0:x1+1].tolist())
        per.extend(g[y1,x0:x1+1].tolist())
        per.extend(g[y0:y1+1,x0].tolist())
        per.extend(g[y0:y1+1,x1].tolist())
        score=sum(int(v)==c for v in per)/max(1,len(per))
        if score<0.78:
            continue
        keep.append(r)
    return keep


def _pointer_from_inner(g,o,bg):
    # isolated 2x2 background center surrounded by a non-background 4x4 ring
    if not (o.size==4 and o.w==2 and o.h==2 and int(o.color)==int(bg)):
        return None
    if o.x0<1 or o.y0<1 or o.x1>=63 or o.y1>=63:
        return None
    patch=g[o.y0-1:o.y1+2,o.x0-1:o.x1+2]
    if patch.shape!=(4,4):
        return None
    border=np.concatenate([patch[0,:],patch[-1,:],patch[1:-1,0],patch[1:-1,-1]])
    vals,counts=np.unique(border,return_counts=True)
    c=int(vals[np.argmax(counts)])
    if int(np.max(counts))<12:
        return None
    if c==int(bg):
        return None
    return Token("ref",c)


def detect_positions(g):
    bg=int(np.bincount(g.ravel().astype(np.int64)).argmax())
    os=list(objects(g))
    pos={}
    # Pointer detection first, using isolated 2x2 inner cells.
    for o in os:
        t=_pointer_from_inner(g,o,bg)
        if t is not None:
            pos[(int(round(o.cx2/2)),int(round(o.cy2/2)))]=t
    # Empty slots and fixed filled leaves.
    for o in os:
        cx=int(round(o.cx2/2)); cy=int(round(o.cy2/2))
        k=(cx,cy)
        if k in pos:
            continue
        if o.size==4 and o.w==2 and o.h==2 and o.color!=bg:
            pos[k]=None
        elif o.size==16 and o.w==4 and o.h==4 and o.color!=bg:
            pos[k]=Token("leaf",int(o.color))
    return pos,bg


def parse_target(g):
    # Top target = ordered 6x6 colored rings with 4x4 common centers.
    toks=[]
    for o in objects(g):
        if o.y1<=8 and o.w==6 and o.h==6 and o.size==20:
            toks.append((o.x0,int(o.color)))
    toks.sort()
    return [c for _,c in toks]


def parse_program(obs):
    g=grid(obs)
    allpos,bg=detect_positions(g)
    rects=find_rectangles(g)

    containers=[]
    for c,x0,y0,x1,y1 in rects:
        if y1<12 or y0>48:
            continue
        ps=[]
        for (x,y),tok in allpos.items():
            if x0<x<x1 and y0<y<y1:
                ps.append(Position(x,y,tok))
        if not ps:
            continue
        # Keep positions on the dominant horizontal row inside this frame.
        rows={}
        for p in ps: rows.setdefault(p.y,[]).append(p)
        row=max(rows.values(),key=len)
        row=sorted(row,key=lambda p:p.x)
        containers.append(Container(int(c),(x0,y0,x1,y1),row))

    # Deduplicate same frame/position signature; choose one per rectangle.
    uniq={}
    for c in containers:
        sig=(c.rect,tuple((p.x,p.y) for p in c.positions))
        uniq[sig]=c
    containers=list(uniq.values())
    containers.sort(key=lambda c:(c.rect[1],c.rect[0],(c.rect[2]-c.rect[0])*(c.rect[3]-c.rect[1])))

    # Some outer-color components may form spurious rectangles; root is topmost
    # container with the largest position row at the minimum y.
    if not containers:
        return None
    miny=min(c.rect[1] for c in containers)
    roots=[c for c in containers if c.rect[1]==miny]
    root=max(roots,key=lambda c:len(c.positions))

    # One program container per color; prefer non-root lower frame for child colors.
    bycolor={}
    for c in containers:
        if c is root:
            continue
        old=bycolor.get(c.color)
        if old is None or c.rect[1]<old.rect[1]:
            bycolor[c.color]=c
    bycolor[root.color]=root

    # Bottom movable sources.
    src=[]
    for (x,y),tok in allpos.items():
        if y>52 and tok is not None:
            src.append((x,y,tok))
    src.sort(key=lambda z:z[0])

    target=parse_target(g)
    empties=[]
    for c in containers:
        for i,p in enumerate(c.positions):
            if p.token is None:
                empties.append((c,i))

    return {
        "grid":g,
        "target":target,
        "root":root,
        "containers":containers,
        "bycolor":bycolor,
        "sources":src,
        "empties":empties,
    }


def solve_program(obs):
    p=parse_program(obs)
    if not p:
        return None
    target=p["target"]
    containers=p["containers"]
    bycolor=p["bycolor"]
    root=p["root"]
    sources=p["sources"]
    empties=p["empties"]

    if len(sources)!=len(empties):
        return {"status":"count_mismatch","target":target,"sources":sources,"empties":empties,"containers":containers}

    # Mutable assignment token/source coordinate per empty position.
    def expand(container, amap, stack=()):
        if container.color in stack:
            raise ValueError("cycle")
        out=[]
        for i,pos in enumerate(container.positions):
            tok=pos.token
            if tok is None:
                tok=amap[(id(container),i)][2]
            if tok.kind=="leaf":
                out.append(tok.color)
            else:
                child=bycolor.get(tok.color)
                if child is None or child is container:
                    raise ValueError("missing/cyclic ref")
                out.extend(expand(child,amap,stack+(container.color,)))
        return out

    # Unique permutations aren't essential at ARC sizes; preserve concrete source
    # instances so execution coordinates are immediately available.
    for perm in permutations(sources):
        amap={}
        for (container,i),src in zip(empties,perm):
            amap[(id(container),i)]=src
        try:
            flat=expand(root,amap)
        except ValueError:
            continue
        if flat==target:
            moves=[]
            for (container,i),src in zip(empties,perm):
                pos=container.positions[i]
                moves.append({
                    "source":(src[0],src[1]),
                    "dest":(pos.x,pos.y),
                    "token":src[2],
                    "container_color":container.color,
                })
            return {
                "status":"solved",
                "target":target,
                "flat":flat,
                "moves":moves,
                "root_color":root.color,
                "containers":containers,
            }
    return {
        "status":"no_assignment",
        "target":target,
        "sources":sources,
        "empties":empties,
        "containers":containers,
    }
