from __future__ import annotations
from collections import Counter, defaultdict
import json
import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

GAMES=["ls20","sb26","vc33","g50t"]

def grid(obs):
    a=np.asarray(obs.frame)
    if a.ndim==3: a=a[-1]
    return a.reshape(64,64).astype(np.int16)

def comps(g):
    h,w=g.shape
    seen=np.zeros((h,w),bool)
    out=[]
    for y in range(h):
        for x in range(w):
            if seen[y,x]: continue
            c=int(g[y,x]); stack=[(y,x)]; seen[y,x]=1; pts=[]
            while stack:
                cy,cx=stack.pop(); pts.append((cy,cx))
                for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
                    ny,nx=cy+dy,cx+dx
                    if 0<=ny<h and 0<=nx<w and not seen[ny,nx] and int(g[ny,nx])==c:
                        seen[ny,nx]=1; stack.append((ny,nx))
            ys=[p[0] for p in pts]; xs=[p[1] for p in pts]
            out.append({"color":c,"size":len(pts),"x0":min(xs),"y0":min(ys),"x1":max(xs),"y1":max(ys),
                        "cx2":min(xs)+max(xs),"cy2":min(ys)+max(ys)})
    out.sort(key=lambda z:(z["color"],z["size"],z["x0"],z["y0"]))
    return out

def changed_stats(a,b):
    ys,xs=np.where(a!=b)
    if len(xs)==0:
        return {"n":0,"bbox":None,"pairs":{}}
    pairs=Counter((int(a[y,x]),int(b[y,x])) for y,x in zip(ys,xs))
    return {"n":int(len(xs)),
            "bbox":[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())],
            "pairs":{f"{u}->{v}":n for (u,v),n in sorted(pairs.items())}}

def comp_motion(a,b):
    ca,cb=comps(a),comps(b)
    bysig=defaultdict(list)
    for j,c in enumerate(cb):
        bysig[(c["color"],c["size"],c["x1"]-c["x0"]+1,c["y1"]-c["y0"]+1)].append((j,c))
    moved=[]
    used=set()
    for x in ca:
        sig=(x["color"],x["size"],x["x1"]-x["x0"]+1,x["y1"]-x["y0"]+1)
        opts=[]
        for j,y in bysig.get(sig,[]):
            if j in used: continue
            d=abs(y["cx2"]-x["cx2"])+abs(y["cy2"]-x["cy2"])
            opts.append((d,j,y))
        if not opts: continue
        d,j,y=min(opts,key=lambda q:q[0]); used.add(j)
        dx2=y["cx2"]-x["cx2"]; dy2=y["cy2"]-x["cy2"]
        if dx2 or dy2:
            moved.append({"sig":sig,"dx2":dx2,"dy2":dy2,"from":[x["x0"],x["y0"],x["x1"],x["y1"]],
                          "to":[y["x0"],y["y0"],y["x1"],y["y1"]]})
    return moved

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
report={}
for gid in GAMES:
    env=arc.make(gid)
    base=grid(env.observation_space)
    legal_raw=list(env.observation_space.available_actions or [])
    rows=[]
    for a in GameAction:
        if a is GameAction.RESET: continue
        # only call simple actions here; complex clicks need coordinates
        if a.is_complex(): continue
        try:
            env.step(GameAction.RESET,data={},reasoning={"latent_probe":"reset"})
            before=grid(env.observation_space)
            out=env.step(a,data={},reasoning={"latent_probe":"one_step"})
            after=grid(out)
            st=changed_stats(before,after)
            st.update({
                "action":a.name,
                "legal": (not legal_raw) or a.value in legal_raw or a in legal_raw,
                "levels":int(out.levels_completed),
                "state":str(out.state),
                "motions":comp_motion(before,after)[:12],
                "color_delta":{str(k):v for k,v in (Counter(map(int,after.ravel()))-Counter(map(int,before.ravel()))).items() if v},
            })
            rows.append(st)
        except Exception as e:
            rows.append({"action":a.name,"error":repr(e)})
    report[gid]={"available_actions":legal_raw,"base_components":comps(base)[:80],"simple_actions":rows}

path=r"C:\Users\teepa\arc3\solve\latent_probe.json"
open(path,"w",encoding="utf-8").write(json.dumps(report,indent=2))
print(path)
