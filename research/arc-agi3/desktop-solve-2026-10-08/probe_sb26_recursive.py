import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

def getg(env):
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
            out.append({"c":c,"n":len(pts),"x0":min(xs),"x1":max(xs),"y0":min(ys),"y1":max(ys)})
    return out

def detect(env):
    cs=comps(getg(env))
    targets=[]
    tokens=[]
    small=[]
    for q in cs:
        w=q["x1"]-q["x0"]+1; h=q["y1"]-q["y0"]+1
        if q["n"]==20 and w==6 and h==6 and q["y0"]<=8:
            targets.append(((q["x0"]+q["x1"])//2,q["c"]))
        if q["n"]==16 and w==4 and h==4 and q["y0"]>=48:
            tokens.append((q["c"],((q["x0"]+q["x1"])//2,(q["y0"]+q["y1"])//2)))
        if q["n"]==4 and w==2 and h==2 and 15<=q["y0"]<=45:
            small.append((((q["x0"]+q["x1"])//2,(q["y0"]+q["y1"])//2),q["c"]))
    targets=sorted(targets)
    token_map={c:p for c,p in tokens}
    # candidate slot row: same y, count matches target count
    rows={}
    for p,c in small:
        rows.setdefault(p[1],[]).append((p,c))
    slotrow=None
    for y,items in rows.items():
        if len(items)==len(targets):
            slotrow=sorted(p for p,c in items)
            break
    colors=[c for x,c in targets]
    if not colors or slotrow is None or not all(c in token_map for c in colors):
        return None,{"targets":targets,"tokens":tokens,"small_rows":{y:len(v) for y,v in rows.items()}}
    return (colors,token_map,slotrow),None

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
env.step(GameAction.RESET,data={},reasoning={"test":"start"})
for attempt in range(12):
    lvl=env.observation_space.levels_completed
    if str(env.observation_space.state).endswith("WIN"):
        print("WIN at",lvl); break
    plan,why=detect(env)
    print("level",lvl,"detect",plan,"why",why)
    if plan is None:
        break
    colors,token_map,slots=plan
    for color,slot in zip(colors,slots):
        p=token_map[color]
        env.step(GameAction.ACTION6,data={"x":p[0],"y":p[1]},reasoning={"test":"select"})
        env.step(GameAction.ACTION6,data={"x":slot[0],"y":slot[1]},reasoning={"test":"assign"})
    before=env.observation_space.levels_completed
    for j in range(4):
        o=env.step(GameAction.ACTION5,data={},reasoning={"test":"advance"})
        if o.levels_completed>before or str(o.state).endswith("WIN"):
            break
    print("after",env.observation_space.levels_completed,env.observation_space.state)
    if env.observation_space.levels_completed==before:
        break
