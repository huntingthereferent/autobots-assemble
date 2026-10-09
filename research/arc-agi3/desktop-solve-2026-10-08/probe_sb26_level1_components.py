import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

def g(env):
    a=np.asarray(env.observation_space.frame)
    if a.ndim==3:a=a[-1]
    return a.reshape(64,64)

def comps(a):
    h,w=a.shape; seen=np.zeros_like(a,dtype=bool); out=[]
    for y in range(h):
        for x in range(w):
            if seen[y,x]: continue
            c=int(a[y,x]); st=[(y,x)]; seen[y,x]=1; pts=[]
            while st:
                cy,cx=st.pop(); pts.append((cy,cx))
                for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
                    ny,nx=cy+dy,cx+dx
                    if 0<=ny<h and 0<=nx<w and not seen[ny,nx] and int(a[ny,nx])==c:
                        seen[ny,nx]=1; st.append((ny,nx))
            ys=[p[0] for p in pts]; xs=[p[1] for p in pts]
            out.append((c,len(pts),min(xs),min(ys),max(xs),max(ys)))
    return sorted(out,key=lambda q:(q[3],q[2],q[0],q[1]))

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
env.step(GameAction.RESET,data={},reasoning={"probe":"r"})
# solve visible level 0
targets=[9,14,11,15]
tok={14:(19,58),15:(27,58),9:(35,58),11:(43,58)}
slots=[(22,29),(28,29),(34,29),(40,29)]
for color,slot in zip(targets,slots):
    p=tok[color]
    env.step(GameAction.ACTION6,data={"x":p[0],"y":p[1]},reasoning={"probe":"select"})
    env.step(GameAction.ACTION6,data={"x":slot[0],"y":slot[1]},reasoning={"probe":"assign"})
env.step(GameAction.ACTION5,data={},reasoning={"probe":"advance"})
print("LEVEL",env.observation_space.levels_completed)
for q in comps(g(env)):
    c,n,x0,y0,x1,y1=q
    if 1<n<260:
        print(q)
