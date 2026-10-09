from itertools import permutations
import copy
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
from reference_transfer import parse_reference_transfer

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
print("base",base.observation_space.levels_completed)
sources=[(6,58),(13,58),(20,58),(27,58),(34,58),(41,58),(48,58),(55,58)]
dests=[(19,22),(25,22),(31,22),(37,22),(43,22),(25,36),(31,36),(37,36)]
tries=0
for perm in permutations(sources):
    e=copy.deepcopy(base)
    for src,dst in zip(perm,dests):
        click(e,src,"assignment select");click(e,dst,"assignment place")
    o=e.step(GameAction.ACTION5,data={},reasoning={"probe":"assignment eval"})
    tries+=1
    if o.levels_completed>4:
        print("FOUND",perm,"tries",tries,"levels",o.levels_completed)
        break
    if tries%2000==0: print("tries",tries,flush=True)
else:
    print("NOT_FOUND",tries)
