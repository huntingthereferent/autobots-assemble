from __future__ import annotations
from collections import deque
from dataclasses import dataclass
from typing import Any
import numpy as np

DIR_PAIR = {
    "ACTION1": ((0,-1),(0,-1)),
    "ACTION2": ((0, 1),(0, 1)),
    "ACTION3": ((-1,0),( 1,0)),
    "ACTION4": (( 1,0),(-1,0)),
}
DIR_SINGLE = {
    "ACTION1": (0,-1),
    "ACTION2": (0, 1),
    "ACTION3": (-1,0),
    "ACTION4": (1,0),
}

@dataclass(frozen=True)
class MirrorState:
    a: tuple[int,int]
    b: tuple[int,int]
    nodes: tuple[tuple[int,int], ...]
    mode: int  # -1 = pair active; >=0 node index active

def _grid(frame):
    a=np.asarray(frame.frame)
    if a.ndim==3:a=a[-1]
    return a.reshape(64,64).astype(np.int8,copy=False)

def _components_of(g,color):
    seen=np.zeros_like(g,dtype=bool); out=[]
    for y in range(64):
        for x in range(64):
            if seen[y,x] or int(g[y,x])!=color: continue
            st=[(y,x)];seen[y,x]=1;pts=[]
            while st:
                cy,cx=st.pop();pts.append((cy,cx))
                for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
                    ny,nx=cy+dy,cx+dx
                    if 0<=ny<64 and 0<=nx<64 and not seen[ny,nx] and int(g[ny,nx])==color:
                        seen[ny,nx]=1;st.append((ny,nx))
            ys=[p[0] for p in pts];xs=[p[1] for p in pts]
            out.append({"x0":min(xs),"y0":min(ys),"x1":max(xs),"y1":max(ys),"size":len(pts)})
    return out

def detect(frame):
    g=_grid(frame)
    pcs=_components_of(g,10)
    # Initial active pair must be two separate equal rectangles.
    if len(pcs)!=2:
        return None
    pcs=sorted(pcs,key=lambda c:(c["x0"],c["y0"]))
    w=pcs[0]["x1"]-pcs[0]["x0"]+1
    h=pcs[0]["y1"]-pcs[0]["y0"]+1
    if w!=h or any((c["x1"]-c["x0"]+1)!=w or (c["y1"]-c["y0"]+1)!=h for c in pcs):
        return None
    q=w
    node_cs=_components_of(g,9)
    nodes=[]
    node_size=None
    for c in node_cs:
        nw=c["x1"]-c["x0"]+1; nh=c["y1"]-c["y0"]+1
        if nw==nh and nw<q and c["size"]==nw*nh:
            nodes.append((c["x0"],c["y0"]))
            node_size=nw if node_size is None else node_size
    # Dynamic objects occupy corridor cells underneath.
    base=g.copy()
    for color in (1,9,10,11):
        base[base==color]=5
    s=MirrorState((pcs[0]["x0"],pcs[0]["y0"]),(pcs[1]["x0"],pcs[1]["y0"]),tuple(sorted(nodes)),-1)
    return {"base":base,"q":q,"node_size":node_size or max(1,(q+1)//2),"state":s}

def _rect_ok(base,x,y,size,occupied):
    if x<0 or y<0 or x+size>64 or y+size>64:
        return False
    if not np.all(base[y:y+size,x:x+size]==5):
        return False
    for ox,oy,osz in occupied:
        if x < ox+osz and ox < x+size and y < oy+osz and oy < y+size:
            return False
    return True

def pair_step(model,s,action):
    q=model["q"]; base=model["base"]; ns=model["node_size"]
    (dax,day),(dbx,dby)=DIR_PAIR[action]
    na=(s.a[0]+dax*q,s.a[1]+day*q)
    nb=(s.b[0]+dbx*q,s.b[1]+dby*q)
    blockers=[(x,y,ns) for i,(x,y) in enumerate(s.nodes)]
    # Goal overlap is explicitly allowed.
    if na==nb:
        if _rect_ok(base,na[0],na[1],q,blockers):
            return MirrorState(na,nb,s.nodes,s.mode)
        return s
    if not _rect_ok(base,na[0],na[1],q,blockers):
        return s
    if not _rect_ok(base,nb[0],nb[1],q,blockers):
        return s
    # Pair members cannot overlap except exact merge.
    if na[0]<nb[0]+q and nb[0]<na[0]+q and na[1]<nb[1]+q and nb[1]<na[1]+q:
        return s
    return MirrorState(na,nb,s.nodes,s.mode)

def node_step(model,s,action):
    q=model["q"]; base=model["base"]; ns=model["node_size"]
    i=s.mode
    x,y=s.nodes[i]
    dx,dy=DIR_SINGLE[action]
    nn=(x+dx*q,y+dy*q)
    occupied=[(s.a[0],s.a[1],q),(s.b[0],s.b[1],q)]
    occupied += [(ox,oy,ns) for j,(ox,oy) in enumerate(s.nodes) if j!=i]
    if not _rect_ok(base,nn[0],nn[1],ns,occupied):
        return s
    nodes=list(s.nodes);nodes[i]=nn
    return MirrorState(s.a,s.b,tuple(nodes),i)

def successors(model,s):
    for a in DIR_PAIR:
        ns=pair_step(model,s,a) if s.mode==-1 else node_step(model,s,a)
        if ns!=s:
            yield (a,None),ns
    if s.mode==-1:
        for i,p in enumerate(s.nodes):
            yield ("CLICK_NODE",i),MirrorState(s.a,s.b,s.nodes,i)
    else:
        for i,p in enumerate(s.nodes):
            if i!=s.mode:
                yield ("CLICK_NODE",i),MirrorState(s.a,s.b,s.nodes,i)
        yield ("CLICK_PAIR",None),MirrorState(s.a,s.b,s.nodes,-1)

def plan(model,max_states=200000):
    start=model["state"]
    q=deque([start]); prev={start:None}; edge={}
    while q and len(prev)<max_states:
        s=q.popleft()
        if s.a==s.b:
            path=[]
            while prev[s] is not None:
                path.append(edge[s]);s=prev[s]
            return list(reversed(path)),len(prev)
        for act,nxt in successors(model,s):
            if nxt not in prev:
                prev[nxt]=s;edge[nxt]=act;q.append(nxt)
    return None,len(prev)
