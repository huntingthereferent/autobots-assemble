import numpy as np, json
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

def g(o):
 a=np.asarray(o.frame)
 if a.ndim==3:a=a[-1]
 return a.reshape(64,64).astype(np.int16)

def diff(a,b):
 ys,xs=np.where(a!=b)
 pts=[(int(x),int(y),int(a[y,x]),int(b[y,x])) for y,x in zip(ys,xs)]
 return {"n":len(pts),"bbox":None if not pts else [min(p[0] for p in pts),min(p[1] for p in pts),max(p[0] for p in pts),max(p[1] for p in pts)],"pts":pts}

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
choices=[(14,(20,58)),(15,(28,58)),(9,(36,58)),(11,(44,58))]
out=[]
for color,(x,y) in choices:
 env.step(GameAction.RESET,data={},reasoning={"probe":"reset"})
 base=g(env.observation_space)
 a=GameAction.ACTION6; a.set_data({"x":x,"y":y})
 s=env.step(a,data={"x":x,"y":y},reasoning={"probe":"select","color":color})
 after_select=g(s)
 c=GameAction.ACTION5
 z=env.step(c,data={},reasoning={"probe":"commit","color":color})
 after_commit=g(z)
 out.append({
  "color":color,
  "select":diff(base,after_select),
  "commit_vs_select":diff(after_select,after_commit),
  "pair_vs_base":diff(base,after_commit),
  "levels":int(z.levels_completed),"state":str(z.state)
 })
print(json.dumps(out,indent=2))
