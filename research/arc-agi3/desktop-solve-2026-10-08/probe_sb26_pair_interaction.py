import numpy as np, json
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

def grid(o):
    a=np.asarray(o.frame)
    if a.ndim==3:a=a[-1]
    return a.reshape(64,64).astype(int)

def click(env,p,label):
    a=GameAction.ACTION6; a.set_data({"x":p[0],"y":p[1]})
    return env.step(a,data=a.action_data.model_dump(),reasoning={"probe":label})

def color_centers(g,region):
    y0,y1=region
    rows=[]
    for color in [9,11,14,15]:
        ys,xs=np.where(g==color)
        mask=(ys>=y0)&(ys<=y1)
        if mask.any():
            rows.append((color,round(float(xs[mask].mean()),1),round(float(ys[mask].mean()),1),int(mask.sum())))
    return rows

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
top=[(20,3),(27,3),(34,3),(41,3)]
bot=[(19,58),(27,58),(35,58),(43,58)]
cases=[
 ("bot9_to_top9",bot[2],top[0]),
 ("bot9_to_top14",bot[2],top[1]),
 ("top9_to_top14",top[0],top[1]),
 ("top9_to_bot14",top[0],bot[0]),
]
for name,p,q in cases:
    env=arc.make("sb26")
    g0=grid(env.observation_space)
    o1=click(env,p,name+"_select")
    g1=grid(o1)
    o2=click(env,q,name+"_second")
    g2=grid(o2)
    ys,xs=np.where(g1!=g2)
    print("\n",name,p,q,"second_delta",len(xs),"bbox",None if len(xs)==0 else (int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())))
    print("top before",color_centers(g0,(0,8)),"after",color_centers(g2,(0,8)))
    print("bot before",color_centers(g0,(55,63)),"after",color_centers(g2,(55,63)))
