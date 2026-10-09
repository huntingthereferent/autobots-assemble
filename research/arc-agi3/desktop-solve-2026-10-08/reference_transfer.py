from __future__ import annotations
import numpy as np
from latent import objects

def grid(obs):
    a=np.asarray(obs.frame)
    if a.ndim==3:a=a[-1]
    return a.reshape(64,64)

def parse_reference_transfer(obs):
    os=list(objects(grid(obs)))

    # Movable source set: dominant same-size distinct-color row in lower quarter.
    low=[o for o in os if o.cy2/2>48 and 4<=o.size<=64]
    bysize={}
    for o in low:
        bysize.setdefault(o.size,[]).append(o)
    if not bysize:
        return None
    source_group=max(bysize.values(),key=lambda xs:len({o.color for o in xs}))
    source_by={}
    for o in source_group:
        source_by[o.color]=o
    colors=set(source_by)
    n=len(colors)
    if n<2:
        return None

    # Reference sequence: same color set in upper strip, one largest object per color.
    rb={}
    for o in os:
        if o.cy2/2<12 and o.color in colors:
            if o.color not in rb or o.size>rb[o.color].size:
                rb[o.color]=o
    refs=sorted(rb.values(),key=lambda o:o.x0)
    if {o.color for o in refs}!=colors:
        return None
    reference=[o.color for o in refs]
    sources={c:(o.cx2//2,o.cy2//2) for c,o in source_by.items()}

    # Position cells are tiny objects in the central playfield.
    cells=[o for o in os if 12<o.cy2/2<48 and 1<=o.size<=8]
    if not cells:
        return None
    # Placeholder leaf color = most common color among the smallest central cells.
    minsz=min(o.size for o in cells)
    tiny=[o for o in cells if o.size==minsz]
    counts={}
    for o in tiny: counts[o.color]=counts.get(o.color,0)+1
    placeholder=max(counts,key=counts.get)

    # Use only minimum-size cells; marker interiors and leaf placeholders share this size.
    cells=tiny

    def center(o): return (o.cx2/2,o.cy2/2)

    def marker_color(cell):
        cx,cy=center(cell)
        candidates=[]
        for o in os:
            if o is cell or o.color==cell.color:
                continue
            if not (12<o.cy2/2<48):
                continue
            if o.x0<=cx<=o.x1 and o.y0<=cy<=o.y1 and o.size>cell.size:
                # A branch color must have a same-color region (possibly this
                # component itself) that contains lower position cells.
                has_children=False
                for comp in os:
                    if comp.color!=o.color:
                        continue
                    for c in cells:
                        if c.cy2/2<=cell.cy2/2+1:
                            continue
                        ccx,ccy=center(c)
                        if comp.x0<=ccx<=comp.x1 and comp.y0<=ccy<=comp.y1:
                            has_children=True
                            break
                    if has_children:
                        break
                area=o.w*o.h
                candidates.append((0 if has_children else 1,area,o.size,o.color,o))
        if not candidates:
            return None
        best=min(candidates,key=lambda t:(t[0],t[1],t[2]))
        return best[3] if best[0]==0 else None

    # Organize cells into approximate horizontal rows.
    ys=sorted({round(o.cy2/2,1) for o in cells})
    if not ys: return None
    top_y=min(ys)

    def row_cells(y, within=None):
        out=[]
        for o in cells:
            if abs(o.cy2/2-y)>0.6: continue
            if within is not None:
                x0,y0,x1,y1=within
                cx,cy=center(o)
                if not (x0<=cx<=x1 and y0<=cy<=y1): continue
            out.append(o)
        return sorted(out,key=lambda o:o.x0)

    seen_branches=set()
    def expand_row(row, depth=0):
        if depth>8:
            raise RuntimeError("branch recursion too deep")
        out=[]
        for cell in row:
            if cell.color==placeholder:
                out.append((cell.cx2//2,cell.cy2//2))
                continue
            bcolor=marker_color(cell)
            if bcolor is None:
                # Non-placeholder tiny cell without a surround is blocked.
                continue
            branch_key=(bcolor,cell.x0,cell.y0)
            if branch_key in seen_branches:
                continue
            seen_branches.add(branch_key)

            # Find a same-color component that contains lower child position cells.
            candidates=[]
            for comp in os:
                if comp.color!=bcolor: continue
                child_cells=[
                    c for c in cells
                    if c.cy2/2>cell.cy2/2+1
                    and comp.x0<=c.cx2/2<=comp.x1
                    and comp.y0<=c.cy2/2<=comp.y1
                ]
                if child_cells:
                    miny=min(c.cy2/2 for c in child_cells)
                    firstrow=sorted([c for c in child_cells if abs(c.cy2/2-miny)<0.6],key=lambda c:c.x0)
                    candidates.append((miny,comp.w*comp.h,firstrow))
            if not candidates:
                continue
            _,_,childrow=min(candidates,key=lambda t:(t[0],t[1]))
            out.extend(expand_row(childrow,depth+1))
        return out

    root=row_cells(top_y)
    order=expand_row(root)
    if len(order)!=n:
        return {
            "reference":reference,"sources":sources,"order":order,
            "placeholder":placeholder,"expected":n,"status":"partial"
        }
    return {
        "reference":reference,"sources":sources,"order":order,
        "placeholder":placeholder,"expected":n,"status":"ok"
    }
