"""Generic latent-state induction for ARC-AGI-3.

Derived only from observable frame transitions. Exact pixels remain the witness;
this module adds compact relational/effect variables for planning.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import blake2b
from collections import Counter
import numpy as np

@dataclass(frozen=True, order=True)
class Obj:
    color:int; size:int; x0:int; y0:int; x1:int; y1:int
    @property
    def shape(self): return (self.color,self.size,self.x1-self.x0+1,self.y1-self.y0+1)
    @property
    def center2(self): return (self.x0+self.x1,self.y0+self.y1)

@dataclass(frozen=True)
class LatentState:
    exact:bytes
    objects:tuple[Obj,...]
    object_key:tuple
    color_counts:tuple
    edge_counts:tuple

@dataclass(frozen=True)
class Effect:
    changed_pixels:int
    bbox:tuple|None
    moved:tuple
    appeared:tuple
    disappeared:tuple
    color_delta:tuple
    edge_only:bool
    class_name:str

def grid(frame):
    a=np.asarray(frame.frame)
    if a.size==0: return np.empty((0,0),dtype=np.int8)
    if a.ndim==3:a=a[-1]
    return a.reshape(64,64).astype(np.int8,copy=False)

def _objs(g):
    h,w=g.shape
    seen=np.zeros_like(g,dtype=bool)
    raw=[]
    for y in range(h):
        for x in range(w):
            if seen[y,x]: continue
            c=int(g[y,x]); stack=[(y,x)]; seen[y,x]=True; pts=[]
            while stack:
                cy,cx=stack.pop(); pts.append((cy,cx))
                for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
                    ny,nx=cy+dy,cx+dx
                    if 0<=ny<h and 0<=nx<w and not seen[ny,nx] and int(g[ny,nx])==c:
                        seen[ny,nx]=True; stack.append((ny,nx))
            ys=[p[0] for p in pts]; xs=[p[1] for p in pts]
            raw.append(Obj(c,len(pts),min(xs),min(ys),max(xs),max(ys)))
    if not raw:return ()
    # Preserve all non-dominant connected regions. Dominant component is usually background.
    dominant=max(range(len(raw)),key=lambda i:raw[i].size)
    out=[o for i,o in enumerate(raw) if i!=dominant]
    return tuple(sorted(out))

def perceive(frame):
    g=grid(frame)
    exact=blake2b(np.ascontiguousarray(g).tobytes(),digest_size=16).digest()
    objs=_objs(g)
    vals,cnts=np.unique(g,return_counts=True)
    cc=tuple(sorted((int(v),int(n)) for v,n in zip(vals,cnts)))
    if g.size:
        edge=np.concatenate((g[0,:],g[-1,:],g[1:-1,0],g[1:-1,-1]))
        ev,ec=np.unique(edge,return_counts=True)
        edges=tuple(sorted((int(v),int(n)) for v,n in zip(ev,ec)))
    else: edges=()
    # Relational key: shapes + absolute centers. Much smaller than pixels while preserving layout.
    ok=tuple((o.shape,o.center2) for o in objs)
    return LatentState(exact,objs,ok,cc,edges)

def effect(before,after):
    a,b=grid(before),grid(after)
    if a.size==0 or b.size==0:
        return Effect(0,None,(),(),(),(),False,"unknown")
    ys,xs=np.where(a!=b); n=int(len(xs))
    bbox=None if n==0 else (int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max()))
    A=perceive(before); B=perceive(after)
    byA={}; byB={}
    for o in A.objects: byA.setdefault(o.shape,[]).append(o)
    for o in B.objects: byB.setdefault(o.shape,[]).append(o)
    moved=[]; appeared=[]; disappeared=[]
    for sh in sorted(set(byA)|set(byB)):
        aa=byA.get(sh,[]); bb=byB.get(sh,[])
        # greedy nearest-center matching among same-shape objects
        used=set()
        for x in aa:
            best=None
            for j,y in enumerate(bb):
                if j in used: continue
                dx=y.center2[0]-x.center2[0]; dy=y.center2[1]-x.center2[1]
                dist=abs(dx)+abs(dy)
                if best is None or dist<best[0]: best=(dist,j,dx,dy)
            if best is None:
                disappeared.append(sh); continue
            _,j,dx,dy=best; used.add(j)
            if dx or dy: moved.append((sh,dx,dy))
        for j,y in enumerate(bb):
            if j not in used: appeared.append(sh)
    ca=Counter(dict(A.color_counts)); cb=Counter(dict(B.color_counts))
    cd=tuple(sorted((k,cb[k]-ca[k]) for k in set(ca)|set(cb) if cb[k]!=ca[k]))
    edge_only=bool(n and bbox and (bbox[0] in (0,63) or bbox[2] in (0,63) or bbox[1] in (0,63) or bbox[3] in (0,63)))
    if n==0: cls="noop"
    elif moved: cls="structural_motion"
    elif n<=4 and edge_only: cls="status_like"
    elif n<=8: cls="tiny_local"
    elif n<=64: cls="local_structural"
    else: cls="global_structural"
    return Effect(n,bbox,tuple(sorted(moved)),tuple(sorted(appeared)),tuple(sorted(disappeared)),cd,edge_only,cls)

def effect_key(e):
    return (e.class_name,e.changed_pixels,e.bbox,e.moved,e.color_delta,e.edge_only)
