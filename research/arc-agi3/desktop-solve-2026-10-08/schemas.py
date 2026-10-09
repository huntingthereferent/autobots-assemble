"""Generic visual schemas induced from observable ARC3 frames."""
from __future__ import annotations
from collections import defaultdict
from arcengine import GameAction
from latent import perceive

def _center(o):
    return (o.center2[0]//2,o.center2[1]//2)

def _aligned_row(objs, tol=2):
    if len(objs)<2:return False
    ys=[o.center2[1] for o in objs]
    return max(ys)-min(ys)<=2*tol

def detect_reference_palette_fill(frame):
    """Detect a visible reference→palette→slots copy task.

    Required evidence:
    - ACTION6 and ACTION5 available;
    - lower row of >=3 solid equal-shape components with distinct colors;
    - upper row containing one component of each palette color;
    - middle row of same-shape equal-color slots;
    - same cardinality across all three rows.

    Returns an action plan only when the relation is structurally unambiguous.
    """
    avail=set(getattr(frame,"available_actions",[]) or [])
    if not ({5,6} <= {a.value if hasattr(a,"value") else a for a in avail}):
        return None

    s=perceive(frame)
    objs=[o for o in s.objects if o.size<=128]
    if len(objs)<9:return None

    # Candidate rows of equal shape signature (size,width,height) and aligned y.
    groups=defaultdict(list)
    for o in objs:
        shape=(o.size,o.x1-o.x0+1,o.y1-o.y0+1)
        groups[shape].append(o)

    row_groups=[]
    for sh,items in groups.items():
        by_y=defaultdict(list)
        for o in items:
            by_y[round((o.y0+o.y1)/2)].append(o)
        for _,row in by_y.items():
            if len(row)>=3 and _aligned_row(row):
                row=sorted(row,key=lambda o:o.center2[0])
                row_groups.append((sh,row))

    # Palette row: solid compact equal-shape components, distinct colors, lower half.
    palettes=[]
    for sh,row in row_groups:
        size,w,h=sh
        if size != w*h: continue
        colors=[o.color for o in row]
        if len(set(colors))!=len(colors): continue
        y=sum(o.center2[1] for o in row)/(2*len(row))
        if y<32: continue
        palettes.append(row)

    for palette in palettes:
        n=len(palette)
        pcolors=[o.color for o in palette]
        pset=set(pcolors)

        # Reference row: exactly one component of every palette color, above palette,
        # horizontally ordered, and not the palette components themselves.
        refs=[]
        for color in pcolors:
            candidates=[
                o for o in objs if o.color==color
                and o not in palette
                and (o.center2[1]//2) < min(x.center2[1]//2 for x in palette)-8
                and o.size>=palette[0].size
            ]
            if not candidates: break
            # prefer larger hollow/frame-like same-color exemplar nearest top
            candidates.sort(key=lambda o:(o.center2[1],-o.size))
            refs.append(candidates[0])
        if len(refs)!=n or not _aligned_row(refs,tol=4):
            continue
        refs=sorted(refs,key=lambda o:o.center2[0])
        if set(o.color for o in refs)!=pset:
            continue

        # Slot row: n equal-shape, same-color compact components between reference and palette.
        ref_y=max(o.center2[1]//2 for o in refs)
        pal_y=min(o.center2[1]//2 for o in palette)
        slot_candidates=[]
        for sh2,row in row_groups:
            if len(row)!=n: continue
            if len(set(o.color for o in row))!=1: continue
            y=sum(o.center2[1] for o in row)/(2*n)
            if not (ref_y+5 < y < pal_y-5): continue
            size,w,h=sh2
            if size>16: continue
            slot_candidates.append(row)
        if not slot_candidates:
            continue
        slots=min(slot_candidates,key=lambda row:sum(o.size for o in row))
        slots=sorted(slots,key=lambda o:o.center2[0])

        # Map reference color order to palette coordinates.
        palette_by_color={o.color:_center(o) for o in palette}
        plan=[]
        for ref,slot in zip(refs,slots):
            if ref.color not in palette_by_color:
                return None
            plan.append(("ACTION6",palette_by_color[ref.color]))
            plan.append(("ACTION6",_center(slot)))
        plan.append(("ACTION5",None))
        return {
            "schema":"reference_palette_fill",
            "reference_colors":[o.color for o in refs],
            "plan":plan,
        }
    return None
