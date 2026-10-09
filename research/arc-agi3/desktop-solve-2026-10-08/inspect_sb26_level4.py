import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
from latent import objects
from reference_transfer import parse_reference_transfer

def arr(obs):
    a=np.asarray(obs.frame)
    if a.ndim==3:a=a[-1]
    return a.reshape(64,64)
def click(env,xy):
    a=GameAction.ACTION6;a.set_data({"x":xy[0],"y":xy[1]})
    return env.step(a,data={"x":xy[0],"y":xy[1]},reasoning={"probe":"advance"})

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
# first 3 via parser
for _ in range(3):
    p=parse_reference_transfer(env.observation_space)
    for c,t in zip(p["reference"],p["order"]):
        click(env,p["sources"][c]);click(env,t)
    env.step(GameAction.ACTION5,data={},reasoning={"probe":"eval"})
# level 3 witnessed
ref=[11,8,14,9,6,12,15]
src={11:(10,58),6:(17,58),12:(24,58),8:(31,58),15:(38,58),9:(45,58),14:(52,58)}
order=[(19,22),(25,22),(31,22),(31,36),(37,36),(37,22),(43,22)]
for c,t in zip(ref,order):
    click(env,src[c]);click(env,t)
o=env.step(GameAction.ACTION5,data={},reasoning={"probe":"L3 eval"})
print("LEVEL",o.levels_completed,"avail",o.available_actions)
g=arr(o)
for x in sorted(objects(g),key=lambda z:(z.y0,z.x0,z.color,z.size)):
    if x.size<=600:
        print({"color":x.color,"size":x.size,"box":(x.x0,x.y0,x.x1,x.y1),"center":(x.cx2/2,x.cy2/2)})
print("CROP")
chars="0123456789ABCDEF"
for y in range(10,50):
    print(f"{y:02d} "+"".join(chars[int(v)] if int(v)<16 else "?" for v in g[y,6:58]))
