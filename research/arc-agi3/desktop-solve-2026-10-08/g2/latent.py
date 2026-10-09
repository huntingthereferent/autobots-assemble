from __future__ import annotations

from collections import Counter
from hashlib import blake2b
from typing import Any
import numpy as np


def grid(frame) -> np.ndarray:
    a=np.asarray(frame.frame)
    if a.size == 0:
        return np.empty((0,0),dtype=np.int8)
    if a.ndim == 3:
        a=a[-1]
    return a.reshape(64,64).astype(np.int8,copy=False)


def exact_key(frame) -> bytes:
    g=grid(frame)
    return blake2b(np.ascontiguousarray(g).tobytes(),digest_size=16).digest()


def components(g: np.ndarray) -> list[dict[str,Any]]:
    if g.size == 0:
        return []
    h,w=g.shape
    seen=np.zeros((h,w),dtype=bool)
    out=[]
    for y in range(h):
        for x in range(w):
            if seen[y,x]:
                continue
            color=int(g[y,x])
            stack=[(y,x)]
            seen[y,x]=True
            pts=[]
            while stack:
                cy,cx=stack.pop()
                pts.append((cy,cx))
                for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
                    ny,nx=cy+dy,cx+dx
                    if 0<=ny<h and 0<=nx<w and not seen[ny,nx] and int(g[ny,nx])==color:
                        seen[ny,nx]=True
                        stack.append((ny,nx))
            ys=[p[0] for p in pts]; xs=[p[1] for p in pts]
            out.append({
                "color":color,"size":len(pts),
                "x0":min(xs),"x1":max(xs),"y0":min(ys),"y1":max(ys),
                "w":max(xs)-min(xs)+1,"h":max(ys)-min(ys)+1,
                "cx2":min(xs)+max(xs),"cy2":min(ys)+max(ys),
            })
    return out


def is_edge_micro(c: dict[str,Any], h: int=64, w: int=64) -> bool:
    if c["size"] > 2:
        return False
    return c["x0"] <= 1 or c["y0"] <= 1 or c["x1"] >= w-2 or c["y1"] >= h-2


def structural_components(g: np.ndarray) -> list[dict[str,Any]]:
    cs=components(g)
    if not cs:
        return []
    # Remove one dominant background region only.
    dominant=max(range(len(cs)),key=lambda i:cs[i]["size"])
    out=[]
    for i,c in enumerate(cs):
        if i == dominant:
            continue
        if is_edge_micro(c):
            continue
        out.append(c)
    return out


def latent_key(frame) -> tuple:
    g=grid(frame)
    if g.size == 0:
        return ()
    cs=structural_components(g)
    sig=[]
    for c in cs:
        sig.append((c["color"],c["size"],c["x0"],c["y0"],c["x1"],c["y1"]))
    sig.sort()
    return tuple(sig)


def shape_key(frame) -> tuple:
    g=grid(frame)
    cs=structural_components(g)
    sig=sorted((c["color"],c["size"],c["w"],c["h"]) for c in cs)
    return tuple(sig)


def delta_signature(before, after) -> dict[str,Any]:
    a,b=grid(before),grid(after)
    if a.size==0 or b.size==0:
        return {"exact_changed":0,"bbox":None,"latent_changed":False,"shape_changed":False}
    ys,xs=np.where(a!=b)
    bbox=None if len(xs)==0 else (int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max()))
    return {
        "exact_changed":int(len(xs)),
        "bbox":bbox,
        "latent_changed":latent_key(before)!=latent_key(after),
        "shape_changed":shape_key(before)!=shape_key(after),
    }


def click_candidates(frame, limit:int=48) -> list[tuple[int,int]]:
    g=grid(frame)
    cs=structural_components(g)
    if not cs:
        return []
    freq=Counter(int(v) for v in g.ravel())
    ranked=[]
    for c in cs:
        if c["size"] > 256:
            continue
        rarity=1.0/max(1,freq[c["color"]])
        compact=1.0/max(1,c["size"])
        score=30.0*rarity+3.0*compact
        pts=[(c["cx2"]//2,c["cy2"]//2)]
        if c["size"]>=12:
            pts += [(c["x0"],c["y0"]),(c["x1"],c["y0"]),(c["x0"],c["y1"]),(c["x1"],c["y1"])]
        for x,y in pts:
            ranked.append((score,max(0,min(63,x)),max(0,min(63,y))))
    ranked.sort(reverse=True)
    out=[]; seen=set()
    for _,x,y in ranked:
        p=(x,y)
        if p not in seen:
            seen.add(p); out.append(p)
    return out[:limit]
