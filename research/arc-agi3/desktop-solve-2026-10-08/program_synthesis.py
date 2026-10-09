"""Generic visual program-synthesis parser for ARC3-like interfaces.

Consumes latent_state.LatentView. No game IDs or banked paths.

Recognizes:
- target symbol row above a program region;
- palette row below containing target alphabet;
- small repeated program slots between them;
- call slots as non-placeholder slot values;
- child routines split by large horizontal gaps;
- call -> child mapping in visual left-to-right order.

The output is an ordered list of writable leaf coordinates corresponding to
the flattened call tree.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Sequence

from latent_state import LatentView, SymbolGroup


@dataclass(frozen=True)
class Routine:
    y0: int
    y1: int
    colors: tuple[int,...]
    centers: tuple[tuple[int,int],...]


@dataclass(frozen=True)
class SynthesisView:
    target: tuple[int,...]
    palette: tuple[tuple[int,tuple[int,int]],...]
    placeholder: int
    routines: tuple[Routine,...]
    leaves: tuple[tuple[int,int],...]


def _split_group(g:SymbolGroup)->list[Routine]:
    xs=[p[0] for p in g.centers]
    if len(xs)<=2:
        return [Routine(g.y0,g.y1,g.colors,g.centers)]
    gaps=[xs[i+1]-xs[i] for i in range(len(xs)-1)]
    positive=[z for z in gaps if z>0]
    if not positive:
        return [Routine(g.y0,g.y1,g.colors,g.centers)]
    base=min(positive)
    # Standard within-routine spacing is very regular. A gap at least ~1.7x
    # the smallest spacing separates sibling routine boxes.
    cuts={i for i,z in enumerate(gaps) if z>=max(base+3,int(round(base*1.7)))}
    if not cuts:
        return [Routine(g.y0,g.y1,g.colors,g.centers)]
    out=[];start=0
    for i in range(len(xs)-1):
        if i in cuts:
            out.append(Routine(g.y0,g.y1,g.colors[start:i+1],g.centers[start:i+1]))
            start=i+1
    out.append(Routine(g.y0,g.y1,g.colors[start:],g.centers[start:]))
    return out


def parse_synthesis(v:LatentView)->SynthesisView|None:
    groups=[g for g in v.horizontal_groups if len(g.colors)>=3]
    if len(groups)<3:
        return None
    groups=sorted(groups,key=lambda g:(g.y0,g.centers[0][0]))

    # Candidate target/palette pair: widest vertical separation, same alphabet
    # coverage, same symbol count. This avoids relying on absolute coordinates.
    pair=None
    for i,t in enumerate(groups):
        for j,b in enumerate(groups):
            if j<=i: continue
            if len(t.colors)!=len(b.colors): continue
            if not set(t.colors).issubset(set(b.colors)): continue
            score=(b.y0-t.y0,len(t.colors))
            if pair is None or score>pair[0]:
                pair=(score,t,b)
    if pair is None:
        return None
    _,target_g,palette_g=pair

    middle=[g for g in groups if target_g.y1 < g.y0 and g.y1 < palette_g.y0]
    # Program slots are the smallest repeated components in the middle.
    if not middle:
        return None
    min_size=min(min(g.component_sizes) for g in middle)
    slot_groups=[g for g in middle if min(g.component_sizes)<=max(9,min_size*2)]
    if not slot_groups:
        return None

    routines=[]
    for g in slot_groups:
        routines.extend(_split_group(g))
    routines=sorted(routines,key=lambda r:(r.y0,r.centers[0][0]))
    if not routines:
        return None

    all_colors=[c for r in routines for c in r.colors]
    placeholder=Counter(all_colors).most_common(1)[0][0]

    # Build visual call tree by levels. Root is the top-most routine. Calls in
    # a routine consume child routines from the next lower y-band left->right.
    bands=[]
    for r in routines:
        if not bands or abs(r.y0-bands[-1][0].y0)>2:
            bands.append([r])
        else:
            bands[-1].append(r)
    for band in bands:
        band.sort(key=lambda r:r.centers[0][0])

    child_cursor=[0 for _ in bands]
    def walk(band_i:int,routine_i:int):
        r=bands[band_i][routine_i]
        leaves=[]
        for color,center in zip(r.colors,r.centers):
            if color==placeholder:
                leaves.append(center)
            else:
                nb=band_i+1
                if nb>=len(bands):
                    return None
                ci=child_cursor[nb]
                if ci>=len(bands[nb]):
                    return None
                child_cursor[nb]+=1
                sub=walk(nb,ci)
                if sub is None:return None
                leaves.extend(sub)
        return leaves

    leaves=walk(0,0)
    if leaves is None:
        return None
    pal=[]
    for c,p in zip(palette_g.colors,palette_g.member_pixels):
        pal.append((c,p))
    return SynthesisView(
        target=target_g.colors,
        palette=tuple(pal),
        placeholder=placeholder,
        routines=tuple(routines),
        leaves=tuple(leaves),
    )
