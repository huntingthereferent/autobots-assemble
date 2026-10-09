from collections import Counter
import numpy as np
from PIL import Image
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

def click(env,x,y):
    a=GameAction.ACTION6; a.set_data({"x":x,"y":y})
    return env.step(a,data={"x":x,"y":y},reasoning={"diag":"reach"})

def reach_l2(env):
    for sx,sy,tx,ty in [(35,58,22,29),(19,58,28,29),(43,58,34,29),(27,58,40,29)]:
        click(env,sx,sy); click(env,tx,ty)
    out=env.step(GameAction.ACTION5,data={},reasoning={"diag":"eval"})
    return out

def comps(g):
    h,w=g.shape; seen=np.zeros((h,w),bool); out=[]
    for y in range(h):
        for x in range(w):
            if seen[y,x]: continue
            c=int(g[y,x]); st=[(y,x)]; seen[y,x]=1; pts=[]
            while st:
                cy,cx=st.pop(); pts.append((cy,cx))
                for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
                    ny,nx=cy+dy,cx+dx
                    if 0<=ny<h and 0<=nx<w and not seen[ny,nx] and int(g[ny,nx])==c:
                        seen[ny,nx]=1; st.append((ny,nx))
            ys=[p[0] for p in pts]; xs=[p[1] for p in pts]
            out.append((len(pts),c,min(xs),min(ys),max(xs),max(ys)))
    return sorted(out,reverse=True)

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
out=reach_l2(env)
a=np.asarray(out.frame)
if a.ndim==3:a=a[-1]
g=a.reshape(64,64)
for rec in comps(g):
    size,c,x0,y0,x1,y1=rec
    if size>=8:
        print(rec)
