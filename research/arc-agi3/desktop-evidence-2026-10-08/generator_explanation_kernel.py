"""Discover a minimal affine-involution generator set by explanatory coverage.

Unlike target-symmetry scoring, a generator is retained only if an orbit of
the actual payload geometry (under some translation) covers the target.
"""

from dataclasses import dataclass
from itertools import combinations
from involution_discovery_kernel import AffineMap, orbit, clipped

Point=tuple[int,int]

def lattice_involutions(width:int,height:int,margin:int=8):
    # Identity is not emitted as a generator.
    out=[]
    # x -> -x + b, y unchanged
    for b in range(-margin,2*width+margin+1):
        out.append(AffineMap(-1,0,0,1,b,0,"axis_x"))
    # y -> -y + b, x unchanged
    for b in range(-margin,2*height+margin+1):
        out.append(AffineMap(1,0,0,-1,0,b,"axis_y"))
    # swap x,y with b2=-b1
    for b in range(-2*max(width,height)-margin,2*max(width,height)+margin+1):
        out.append(AffineMap(0,1,1,0,b,-b,"diag"))
    # anti-swap with b2=b1
    for b in range(-2*max(width,height)-margin,2*max(width,height)+margin+1):
        out.append(AffineMap(0,-1,-1,0,b,b,"anti_diag"))
    # half-turn: any translation vector
    for bx in range(-margin,2*width+margin+1):
        for by in range(-margin,2*height+margin+1):
            out.append(AffineMap(-1,0,0,-1,bx,by,"half_turn"))
    return out

def translated(shape,at):
    x,y=at
    return {(x+dx,y+dy) for dx,dy in shape}

def support(shape,at,gens,width,height):
    return clipped(orbit(translated(shape,at),gens),width,height)

def one_payload_explanations(shape,target,width,height,translations,gens,max_generators=2):
    T=set(target)
    # 0 generators first
    for at in translations:
        S=support(shape,at,[],width,height)
        if T<=S:
            yield (0,(),at,len(S-T))
    if max_generators<1:return
    singles=[]
    for g in gens:
        for at in translations:
            S=support(shape,at,[g],width,height)
            if T<=S:
                yield (1,(g,),at,len(S-T))
                singles.append((g,at,S))
    if max_generators<2:return
    # Two-generator search is expensive; only pair transforms that individually
    # explain at least one target point from a candidate placement.
    useful=[]
    for g in gens:
        ok=False
        for at in translations:
            S=support(shape,at,[g],width,height)
            if S&T:
                ok=True;break
        if ok: useful.append(g)
    for g1,g2 in combinations(useful,2):
        for at in translations:
            S=support(shape,at,[g1,g2],width,height)
            if T<=S:
                yield (2,(g1,g2),at,len(S-T))
