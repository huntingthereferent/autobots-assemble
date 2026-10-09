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
def solve_one(env):
    p=parse_reference_transfer(env.observation_space)
    if not p or p.get("status")!="ok": return False
    for c,d in zip(p["reference"],p["order"]):
        click(env,p["sources"][c]);click(env,d)
    o=env.step(GameAction.ACTION5,data={},reasoning={"probe":"eval"})
    return o.levels_completed>0

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
for _ in range(3):
    p=parse_reference_transfer(env.observation_space)
    print("advance parse",p)
    before=env.observation_space.levels_completed
    for c,t in zip(p["reference"],p["order"]):
        click(env,p["sources"][c]);click(env,t)
    env.step(GameAction.ACTION5,data={},reasoning={"probe":"eval"})
    print("now",env.observation_space.levels_completed)
obs=env.observation_space
print("LEVEL",obs.levels_completed,"parse",parse_reference_transfer(obs))
g=arr(obs)
for x in sorted(objects(g),key=lambda z:(z.y0,z.x0,z.color,z.size)):
    if x.size<=500:
        print({"color":x.color,"size":x.size,"box":(x.x0,x.y0,x.x1,x.y1),"center":(x.cx2/2,x.cy2/2)})
print("CROP")
chars="0123456789ABCDEF"
for y in range(12,48):
    print(f"{y:02d} "+"".join(chars[int(v)] if int(v)<16 else "?" for v in g[y,8:56]))
