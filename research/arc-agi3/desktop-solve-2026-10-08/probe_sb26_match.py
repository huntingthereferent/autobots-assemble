import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")

def frame():
    a=np.asarray(env.observation_space.frame)
    if a.ndim==3:a=a[-1]
    return a.reshape(64,64)

def comps(g):
    h,w=g.shape; seen=np.zeros_like(g,dtype=bool); out=[]
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
            out.append((c,len(pts),min(xs),min(ys),max(xs),max(ys)))
    return out

g=frame(); cs=comps(g)
targets=[]
tokens=[]
slots=[]
for c,n,x0,y0,x1,y1 in cs:
    if n==20 and y0<=2 and (x1-x0+1)==6 and (y1-y0+1)==6:
        targets.append((x0,c))
    if n==16 and y0>=56 and (x1-x0+1)==4 and (y1-y0+1)==4:
        tokens.append((c,((x0+x1)//2,(y0+y1)//2)))
    if c==2 and n==4 and 25<=y0<=32:
        slots.append(((x0+x1)//2,(y0+y1)//2))
targets=[c for _,c in sorted(targets)]
slots=sorted(slots)
token_map={c:p for c,p in tokens}
print("targets",targets)
print("tokens",token_map)
print("slots",slots)

env.step(GameAction.RESET,data={},reasoning={"probe":"reset"})
for color,slot in zip(targets,slots):
    p=token_map[color]
    env.step(GameAction.ACTION6,data={"x":p[0],"y":p[1]},reasoning={"probe":"select_visible_color"})
    o=env.step(GameAction.ACTION6,data={"x":slot[0],"y":slot[1]},reasoning={"probe":"assign_visible_slot"})
    print("assigned",color,"slot",slot,"levels",o.levels_completed,"state",o.state)

print("after assignments",env.observation_space.levels_completed,env.observation_space.state)
for i in range(8):
    if env.observation_space.levels_completed>0 or str(env.observation_space.state).endswith("WIN"):
        break
    o=env.step(GameAction.ACTION5,data={},reasoning={"probe":"advance"})
    print("advance",i+1,"levels",o.levels_completed,"state",o.state)
print("final",env.observation_space.levels_completed,env.observation_space.state)
