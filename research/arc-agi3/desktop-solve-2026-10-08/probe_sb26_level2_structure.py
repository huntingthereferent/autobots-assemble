import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

def arr(env):
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
env.step(GameAction.RESET,data={},reasoning={"p":"r"})
# solve L0
for color,slot in zip([9,14,11,15],[(22,29),(28,29),(34,29),(40,29)]):
    p={14:(19,58),15:(27,58),9:(35,58),11:(43,58)}[color]
    env.step(GameAction.ACTION6,data={"x":p[0],"y":p[1]},reasoning={"p":"s0"})
    env.step(GameAction.ACTION6,data={"x":slot[0],"y":slot[1]},reasoning={"p":"a0"})
env.step(GameAction.ACTION5,data={},reasoning={"p":"g0"})
# solve L1
target=[12,15,8,9,14,11,6]
tokens={8:(10,58),15:(17,58),14:(24,58),12:(31,58),6:(38,58),9:(45,58),11:(52,58)}
order=[(22,22),(28,22),(22,36),(28,36),(34,36),(40,36),(40,22)]
for color,slot in zip(target,order):
    p=tokens[color]
    env.step(GameAction.ACTION6,data={"x":p[0],"y":p[1]},reasoning={"p":"s1"})
    env.step(GameAction.ACTION6,data={"x":slot[0],"y":slot[1]},reasoning={"p":"a1"})
env.step(GameAction.ACTION5,data={},reasoning={"p":"g1"})
print("LEVEL",env.observation_space.levels_completed)
g=arr(env)
for q in comps(g):
    c,n,x0,y0,x1,y1=q
    if 1<n<320:
        print(q)
print("MID")
for y in range(10,50):
    print(f"{y:02d}","".join(format(int(v),"x") for v in g[y,8:56]))
