"""Generic latent-state extraction for ARC3 visual interfaces.

No game ids. No banked solution paths.

The extractor keeps:
- exact pixel witness;
- connected components with an actual member pixel (not centroid-only);
- horizontal repeated-symbol groups;
- palette-like rows;
- framed target regions;
- monotone counter strips;
- action-delta signatures.

It is intentionally descriptive: planning must consume relations that are
supported by observed pixels/actions rather than invent task semantics.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import blake2b
from typing import Iterable, Any

import numpy as np


@dataclass(frozen=True)
class Component:
    color: int
    size: int
    x0: int
    y0: int
    x1: int
    y1: int
    member_x: int
    member_y: int

    @property
    def width(self): return self.x1-self.x0+1
    @property
    def height(self): return self.y1-self.y0+1
    @property
    def cx2(self): return self.x0+self.x1
    @property
    def cy2(self): return self.y0+self.y1
    @property
    def fill(self): return self.size/max(1,self.width*self.height)
    @property
    def box(self): return (self.x0,self.y0,self.x1,self.y1)


@dataclass(frozen=True)
class SymbolGroup:
    y0: int
    y1: int
    colors: tuple[int,...]
    centers: tuple[tuple[int,int],...]
    member_pixels: tuple[tuple[int,int],...]
    component_sizes: tuple[int,...]


@dataclass(frozen=True)
class CounterStrip:
    y: int
    base_color: int
    active_color: int
    active_positions: tuple[int,...]


@dataclass(frozen=True)
class LatentView:
    exact_key: bytes
    components: tuple[Component,...]
    horizontal_groups: tuple[SymbolGroup,...]
    counter_strips: tuple[CounterStrip,...]
    color_counts: tuple[tuple[int,int],...]


def frame_grid(frame)->np.ndarray:
    a=np.asarray(frame.frame)
    if a.size==0:
        return np.empty((0,0),dtype=np.int16)
    if a.ndim==3: a=a[-1]
    return a.reshape(64,64).astype(np.int16,copy=False)


def _nbrs(y,x,h,w):
    if y: yield y-1,x
    if y+1<h: yield y+1,x
    if x: yield y,x-1
    if x+1<w: yield y,x+1


def extract_components(g:np.ndarray)->tuple[Component,...]:
    if g.size==0: return ()
    h,w=g.shape
    seen=np.zeros((h,w),dtype=bool)
    out=[]
    for y in range(h):
        for x in range(w):
            if seen[y,x]: continue
            c=int(g[y,x]); stack=[(y,x)]; seen[y,x]=1; pts=[]
            while stack:
                cy,cx=stack.pop(); pts.append((cy,cx))
                for ny,nx in _nbrs(cy,cx,h,w):
                    if not seen[ny,nx] and int(g[ny,nx])==c:
                        seen[ny,nx]=1; stack.append((ny,nx))
            ys=[p[0] for p in pts]; xs=[p[1] for p in pts]
            # Use a real member pixel nearest the bbox center. This avoids the
            # centroid-in-a-hole bug for rings/frames.
            tx=(min(xs)+max(xs))/2; ty=(min(ys)+max(ys))/2
            my,mx=min(pts,key=lambda p:(p[1]-tx)**2+(p[0]-ty)**2)
            out.append(Component(c,len(pts),min(xs),min(ys),max(xs),max(ys),mx,my))
    out.sort(key=lambda z:(z.y0,z.x0,z.color,z.size))
    return tuple(out)


def horizontal_symbol_groups(cs:tuple[Component,...], g:np.ndarray)->tuple[SymbolGroup,...]:
    # Candidate repeated object rows: >=3 similarly-sized compact components,
    # distinct x positions, common vertical band, excluding huge backgrounds.
    small=[c for c in cs if 3<=c.size<=128 and c.width<=12 and c.height<=12]
    bands=[]
    used=set()
    for i,c in enumerate(small):
        if i in used: continue
        peers=[(j,d) for j,d in enumerate(small)
               if abs(d.y0-c.y0)<=2 and abs(d.y1-c.y1)<=2
               and 0.45 <= d.size/max(1,c.size) <= 2.2]
        if len(peers)<3: continue
        peers=sorted(peers,key=lambda jd:jd[1].x0)
        # Collapse nested components sharing almost same center/box: keep the
        # outer/larger one as the symbol carrier.
        chosen=[]
        for j,d in peers:
            if chosen and abs((chosen[-1][1].cx2-d.cx2))<=2 and abs((chosen[-1][1].cy2-d.cy2))<=2:
                if d.size>chosen[-1][1].size: chosen[-1]=(j,d)
            else:
                chosen.append((j,d))
        if len(chosen)<3: continue
        xs=[d.x0 for _,d in chosen]
        if len(set(xs))<3: continue
        for j,_ in chosen: used.add(j)
        bands.append(SymbolGroup(
            min(d.y0 for _,d in chosen),max(d.y1 for _,d in chosen),
            tuple(d.color for _,d in chosen),
            tuple((d.cx2//2,d.cy2//2) for _,d in chosen),
            tuple((d.member_x,d.member_y) for _,d in chosen),
            tuple(d.size for _,d in chosen),
        ))
    # Deduplicate by vertical band + centers.
    uniq={}
    for b in bands:
        k=(b.y0,b.y1,b.centers)
        uniq[k]=b
    return tuple(sorted(uniq.values(),key=lambda b:(b.y0,b.centers)))


def counter_strips(g:np.ndarray)->tuple[CounterStrip,...]:
    # Long nearly-uniform horizontal rows with a small suffix/prefix of a
    # second color are useful latent counters/timers.
    out=[]
    if g.size==0:return ()
    h,w=g.shape
    for y in range(h):
        vals,counts=np.unique(g[y],return_counts=True)
        if len(vals)<2: continue
        order=np.argsort(counts)[::-1]
        base=int(vals[order[0]]); nbase=int(counts[order[0]])
        if nbase < int(.75*w): continue
        for idx in order[1:]:
            active=int(vals[idx]); pos=tuple(int(x) for x in np.where(g[y]==active)[0])
            if 1<=len(pos)<=int(.25*w):
                # contiguous run only
                if max(pos)-min(pos)+1==len(pos):
                    out.append(CounterStrip(y,base,active,pos))
    return tuple(out)


def perceive(frame)->LatentView:
    g=frame_grid(frame)
    if g.size==0:
        return LatentView(b"",(),(),(),())
    cs=extract_components(g)
    vals,counts=np.unique(g,return_counts=True)
    return LatentView(
        blake2b(np.ascontiguousarray(g).tobytes(),digest_size=16).digest(),
        cs,
        horizontal_symbol_groups(cs,g),
        counter_strips(g),
        tuple(sorted((int(v),int(n)) for v,n in zip(vals,counts))),
    )


def delta_signature(before,after)->dict[str,Any]:
    a,b=frame_grid(before),frame_grid(after)
    if a.size==0 or b.size==0:return {"changed":0,"bbox":None}
    ys,xs=np.where(a!=b)
    if len(xs)==0:return {"changed":0,"bbox":None,"colors":()}
    ca={int(v):int(n) for v,n in zip(*np.unique(a,return_counts=True))}
    cb={int(v):int(n) for v,n in zip(*np.unique(b,return_counts=True))}
    colors=tuple(sorted((k,cb.get(k,0)-ca.get(k,0)) for k in set(ca)|set(cb) if cb.get(k,0)!=ca.get(k,0)))
    return {
        "changed":int(len(xs)),
        "bbox":(int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())),
        "colors":colors,
    }
