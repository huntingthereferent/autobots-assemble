import numpy as np, json
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

def g(o):
 a=np.asarray(o.frame)
 if a.ndim==3:a=a[-1]
 return a.reshape(64,64).astype(np.int16)

def sm(a,b):
 ys,xs=np.where(a!=b)
 return {"n":int(len(xs)),"bbox":None if len(xs)==0 else [int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())],
         "pts":[[int(x),int(y),int(a[y,x]),int(b[y,x])] for y,x in zip(ys,xs)][:100]}

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
# actual colored-border pixels, not centroids in gray holes
pts=[("top9",9,(18,1)),("top14",14,(25,1)),("top11",11,(32,1)),("top15",15,(39,1))]
out=[]
for name,color,(x,y) in pts:
 env.step(GameAction.RESET,data={},reasoning={"probe":"reset"})
 base=g(env.observation_space)
 a=GameAction.ACTION6;a.set_data({"x":x,"y":y})
 z=env.step(a,data={"x":x,"y":y},reasoning={"probe":"ring-member","name":name})
 out.append({"name":name,"xy":[x,y],"after_click":sm(base,g(z)),"levels":int(z.levels_completed),"state":str(z.state)})
print(json.dumps(out,indent=2))
