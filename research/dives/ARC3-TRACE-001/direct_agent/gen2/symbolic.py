from __future__ import annotations
from dataclasses import dataclass
from typing import Any
import numpy as np

@dataclass(frozen=True)
class Item:
    kind: str              # "slot" or "call"
    x: int
    y: int
    color: int | None
    click: tuple[int,int]

@dataclass
class Row:
    y: int
    items: list[Item]

def connected_components(g: np.ndarray) -> list[dict[str,Any]]:
    h,w=g.shape
    seen=np.zeros((h,w),dtype=bool)
    out=[]
    for y in range(h):
        for x in range(w):
            if seen[y,x]: continue
            c=int(g[y,x]); st=[(y,x)]; seen[y,x]=True; pts=[]
            while st:
                cy,cx=st.pop(); pts.append((cy,cx))
                for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
                    ny,nx=cy+dy,cx+dx
                    if 0<=ny<h and 0<=nx<w and not seen[ny,nx] and int(g[ny,nx])==c:
                        seen[ny,nx]=True; st.append((ny,nx))
            ys=[p[0] for p in pts]; xs=[p[1] for p in pts]
            out.append({"color":c,"size":len(pts),"x0":min(xs),"x1":max(xs),"y0":min(ys),"y1":max(ys)})
    return out

def find_hollow4(g:np.ndarray,ylo:int=10,yhi:int=50)->list[Item]:
    h,w=g.shape; out=[]; seen=set()
    for y in range(max(0,ylo),min(h-3,yhi)):
        for x in range(0,w-3):
            border=[g[y,x],g[y,x+1],g[y,x+2],g[y,x+3],
                    g[y+3,x],g[y+3,x+1],g[y+3,x+2],g[y+3,x+3],
                    g[y+1,x],g[y+2,x],g[y+1,x+3],g[y+2,x+3]]
            c=int(border[0])
            if all(int(v)==c for v in border) and c!=4:
                # Interior must not be the same color or this is a solid block.
                if all(int(g[y+dy,x+dx])!=c for dy in (1,2) for dx in (1,2)):
                    k=(x,y,c)
                    if k not in seen:
                        seen.add(k)
                        out.append(Item("call",2*x+3,2*y+3,c,(x+1,y+1)))
    return out

def find_solid2(g:np.ndarray,ylo:int=10,yhi:int=50)->list[Item]:
    h,w=g.shape; out=[]; seen=set()
    for y in range(max(0,ylo),min(h-1,yhi)):
        for x in range(0,w-1):
            c=int(g[y,x])
            if c==4: continue
            if all(int(g[y+dy,x+dx])==c for dy in (0,1) for dx in (0,1)):
                # Require immediate cardinal surroundings to differ when present,
                # so larger solid regions do not explode into 2x2 windows.
                ok=True
                for xx,yy in ((x-1,y),(x+2,y),(x,y-1),(x,y+2)):
                    if 0<=xx<w and 0<=yy<h and int(g[yy,xx])==c:
                        ok=False; break
                if ok:
                    k=(x,y,c)
                    if k not in seen:
                        seen.add(k)
                        out.append(Item("slot",2*x+1,2*y+1,None,(x,y)))
    return out

def split_rows(items:list[Item])->list[Row]:
    byy={}
    for it in items:
        byy.setdefault(it.y,[]).append(it)
    rows=[]
    for y,group in sorted(byy.items()):
        group=sorted(group,key=lambda i:i.x)
        if not group: continue
        # infer normal spacing from smallest positive separation.
        ds=[group[i+1].x-group[i].x for i in range(len(group)-1)]
        base=min(ds) if ds else 12
        chunk=[group[0]]
        for prev,cur in zip(group,group[1:]):
            if cur.x-prev.x > max(base+4,int(base*1.6)):
                rows.append(Row(y,chunk)); chunk=[cur]
            else:
                chunk.append(cur)
        rows.append(Row(y,chunk))
    return rows

def top_targets_and_tokens(g:np.ndarray):
    cs=connected_components(g)
    targets=[]
    tokens=[]
    for q in cs:
        w=q["x1"]-q["x0"]+1; h=q["y1"]-q["y0"]+1
        if q["size"]==20 and w==6 and h==6 and q["y0"]<=8:
            targets.append((q["x0"],q["color"]))
        if q["size"]==16 and w==4 and h==4 and q["y0"]>=48:
            tokens.append((q["color"],((q["x0"]+q["x1"])//2,(q["y0"]+q["y1"])//2)))
    return [c for _,c in sorted(targets)],{c:p for c,p in tokens},cs

def child_for_call(call:Item,parent:Row,rows:list[Row],cs:list[dict[str,Any]])->Row|None:
    candidates=[]
    for row in rows:
        if row.y<=parent.y: continue
        xs=[it.x/2 for it in row.items]
        for q in cs:
            if q["color"]!=call.color: continue
            if q["x1"]-q["x0"]+1 <=4 or q["y1"]-q["y0"]+1 <=4: continue
            ry=row.y/2
            if q["y0"]<=ry<=q["y1"] and min(xs)>=q["x0"]-1 and max(xs)<=q["x1"]+1:
                candidates.append((row.y-parent.y,abs(sum(xs)/len(xs)-call.x/2),row))
                break
    if not candidates:
        return None
    candidates.sort(key=lambda z:(z[0],z[1]))
    return candidates[0][2]

def flatten(root:Row,rows:list[Row],cs:list[dict[str,Any]],seen=None)->list[tuple[int,int]]|None:
    seen=set() if seen is None else seen
    rid=(root.y,tuple((i.kind,i.x,i.color) for i in root.items))
    if rid in seen: return None
    seen.add(rid)
    out=[]
    for it in sorted(root.items,key=lambda i:i.x):
        if it.kind=="slot":
            out.append(it.click)
        else:
            child=child_for_call(it,root,rows,cs)
            if child is None:
                return None
            sub=flatten(child,rows,cs,seen)
            if sub is None:
                return None
            out.extend(sub)
    return out

def detect_program(g:np.ndarray):
    targets,tokens,cs=top_targets_and_tokens(g)
    calls=find_hollow4(g)
    slots=find_solid2(g)
    # Program placeholders in observed games use a repeated small color; filter
    # solid2 candidates to colors that occur in at least two middle positions.
    # Re-read their actual colors from their click coordinate.
    colored=[]
    counts={}
    for it in slots:
        x,y=it.click; c=int(g[y,x]); counts[c]=counts.get(c,0)+1
        colored.append((it,c))
    allowed={c for c,n in counts.items() if n>=2}
    slots=[it for it,c in colored if c in allowed]
    rows=split_rows(slots+calls)
    if not targets or not rows or not all(c in tokens for c in targets):
        return None,{"targets":targets,"rows":[[(i.kind,i.x,i.y,i.color) for i in r.items] for r in rows]}
    root=min(rows,key=lambda r:r.y)
    order=flatten(root,rows,cs)
    if order is None or len(order)!=len(targets):
        return None,{"targets":targets,"order":order,"rows":[[(i.kind,i.x,i.y,i.color) for i in r.items] for r in rows]}
    return {"targets":targets,"tokens":tokens,"order":order},None
