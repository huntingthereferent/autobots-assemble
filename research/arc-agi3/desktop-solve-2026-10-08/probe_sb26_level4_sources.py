import copy, numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
from reference_transfer import parse_reference_transfer
from latent import effect

def arr(obs):
    a=np.asarray(obs.frame)
    if a.ndim==3:a=a[-1]
    return a.reshape(64,64)
def click(env,xy,why):
    a=GameAction.ACTION6;a.set_data({"x":xy[0],"y":xy[1]})
    return env.step(a,data={"x":xy[0],"y":xy[1]},reasoning={"probe":why})
def advance4(env):
    for _ in range(3):
        p=parse_reference_transfer(env.observation_space)
        for c,t in zip(p["reference"],p["order"]):
            click(env,p["sources"][c],"advance");click(env,t,"advance")
        env.step(GameAction.ACTION5,data={},reasoning={"probe":"eval"})
    ref=[11,8,14,9,6,12,15]
    src={11:(10,58),6:(17,58),12:(24,58),8:(31,58),15:(38,58),9:(45,58),14:(52,58)}
    order=[(19,22),(25,22),(31,22),(31,36),(37,36),(37,22),(43,22)]
    for c,t in zip(ref,order):
        click(env,src[c],"advance");click(env,t,"advance")
    env.step(GameAction.ACTION5,data={},reasoning={"probe":"eval"})
    return env

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
base=advance4(arc.make("sb26"))
print("level",base.observation_space.levels_completed)
tests=[("normal15",(6,58)),("normal14",(41,58)),("marker9a",(48,58)),("marker9b",(55,58))]
for name,src in tests:
    e=copy.deepcopy(base)
    b=arr(e.observation_space)
    o1=click(e,src,name+" select")
    e1=effect(b,arr(o1))
    b2=arr(o1)
    o2=click(e,(19,22),name+" place")
    e2=effect(b2,arr(o2))
    print(name,"select",e1,"place",e2,"levels",o2.levels_completed)
