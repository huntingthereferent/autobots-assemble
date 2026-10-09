from __future__ import annotations

from dataclasses import dataclass
from hashlib import blake2b
from typing import Iterable
import numpy as np


@dataclass(frozen=True, order=True)
class Obj:
    color: int
    size: int
    x0: int
    y0: int
    x1: int
    y1: int

    @property
    def w(self): return self.x1-self.x0+1
    @property
    def h(self): return self.y1-self.y0+1
    @property
    def cx2(self): return self.x0+self.x1
    @property
    def cy2(self): return self.y0+self.y1
    @property
    def shape(self): return (self.color,self.size,self.w,self.h)
    @property
    def border(self): return self.x0==0 or self.y0==0 or self.x1==63 or self.y1==63


@dataclass(frozen=True)
class LatentView:
    exact: bytes
    structural: tuple[tuple[int,int,int,int,int,int], ...]
    status: tuple[tuple[int,int,int,int,int,int], ...]
    colors: tuple[tuple[int,int], ...]


@dataclass(frozen=True)
class Effect:
    changed_pixels: int
    bbox: tuple[int,int,int,int] | None
    delta_components: int
    class_name: str
    moved: tuple[tuple[int,int,int,int], ...]
    added_shapes: tuple[tuple[int,int,int,int], ...]
    removed_shapes: tuple[tuple[int,int,int,int], ...]


def _neighbors(y,x,h,w):
    if y: yield y-1,x
    if y+1<h: yield y+1,x
    if x: yield y,x-1
    if x+1<w: yield y,x+1


def objects(g: np.ndarray) -> tuple[Obj,...]:
    g=np.asarray(g,dtype=np.int16)
    h,w=g.shape
    seen=np.zeros((h,w),bool)
    raw=[]
    for y in range(h):
        for x in range(w):
            if seen[y,x]: continue
            c=int(g[y,x]); stack=[(y,x)]; seen[y,x]=1; pts=[]
            while stack:
                cy,cx=stack.pop(); pts.append((cy,cx))
                for ny,nx in _neighbors(cy,cx,h,w):
                    if not seen[ny,nx] and int(g[ny,nx])==c:
                        seen[ny,nx]=1; stack.append((ny,nx))
            ys=[p[0] for p in pts]; xs=[p[1] for p in pts]
            raw.append(Obj(c,len(pts),min(xs),min(ys),max(xs),max(ys)))
    # remove only single largest component as background witness candidate
    if raw:
        i=max(range(len(raw)),key=lambda j:raw[j].size)
        raw=[o for j,o in enumerate(raw) if j!=i]
    return tuple(sorted(raw))


def view(g: np.ndarray) -> LatentView:
    g=np.asarray(g,dtype=np.int16)
    ex=blake2b(np.ascontiguousarray(g).tobytes(),digest_size=16).digest()
    vals,counts=np.unique(g,return_counts=True)
    cc=tuple(sorted((int(v),int(n)) for v,n in zip(vals,counts)))
    structural=[]; status=[]
    for o in objects(g):
        sig=(o.color,o.size,o.x0,o.y0,o.x1,o.y1)
        # tiny edge indicators are status candidates, not discarded.
        if o.size<=4 and o.border:
            status.append(sig)
        else:
            structural.append(sig)
    return LatentView(ex,tuple(structural),tuple(status),cc)


def _match_moves(a: tuple[Obj,...], b: tuple[Obj,...]):
    by_a={}; by_b={}
    for o in a: by_a.setdefault(o.shape,[]).append(o)
    for o in b: by_b.setdefault(o.shape,[]).append(o)
    moved=[]
    used_a=set(); used_b=set()
    for sh in set(by_a)&set(by_b):
        aa=by_a[sh]; bb=by_b[sh]
        # greedy nearest-center matching
        pairs=[]
        for i,x in enumerate(aa):
            for j,y in enumerate(bb):
                d=abs(x.cx2-y.cx2)+abs(x.cy2-y.cy2)
                pairs.append((d,i,j))
        for _,i,j in sorted(pairs):
            ka=(sh,i); kb=(sh,j)
            if ka in used_a or kb in used_b: continue
            used_a.add(ka); used_b.add(kb)
            x,y=aa[i],bb[j]
            dx2=y.cx2-x.cx2; dy2=y.cy2-x.cy2
            if dx2 or dy2:
                moved.append((x.color,x.size,dx2,dy2))
    return tuple(sorted(moved))


def effect(before: np.ndarray, after: np.ndarray) -> Effect:
    a=np.asarray(before); b=np.asarray(after)
    mask=a!=b
    ys,xs=np.where(mask)
    n=int(mask.sum())
    bbox=None if n==0 else (int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max()))

    if n==0:
        return Effect(0,None,0,"noop",(),(),())

    # delta connected components irrespective of changed color
    h,w=mask.shape; seen=np.zeros_like(mask,bool); dc=0
    for y,x in zip(ys,xs):
        if seen[y,x]: continue
        dc+=1; stack=[(int(y),int(x))]; seen[y,x]=1
        while stack:
            cy,cx=stack.pop()
            for ny,nx in _neighbors(cy,cx,h,w):
                if mask[ny,nx] and not seen[ny,nx]:
                    seen[ny,nx]=1; stack.append((ny,nx))

    oa,ob=objects(a),objects(b)
    moved=_match_moves(oa,ob)
    ca={o.shape for o in oa}; cb={o.shape for o in ob}
    added=tuple(sorted(cb-ca)); removed=tuple(sorted(ca-cb))

    edge = bbox is not None and (bbox[0]==0 or bbox[1]==0 or bbox[2]==63 or bbox[3]==63)
    if n<=4 and edge:
        cls="status"
    elif moved:
        cls="motion"
    elif n<=16:
        cls="local_edit"
    elif dc==1:
        cls="structural_edit"
    else:
        cls="distributed_edit"
    return Effect(n,bbox,dc,cls,moved,added,removed)
