import copy
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

def click(env,xy):
    a=GameAction.ACTION6;a.set_data({"x":xy[0],"y":xy[1]})
    return env.step(a,data={"x":xy[0],"y":xy[1]},reasoning={"probe":"clone"})

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
# L0
for s,t in [((35,58),(22,29)),((19,58),(28,29)),((43,58),(34,29)),((27,58),(40,29))]:
    click(env,s);click(env,t)
env.step(GameAction.ACTION5,data={},reasoning={"probe":"eval"})
# L1
ref=[12,15,8,9,14,11,6]
source={8:(10,58),15:(17,58),14:(24,58),12:(31,58),6:(38,58),9:(45,58),11:(52,58)}
order=[(22,22),(28,22),(22,36),(28,36),(34,36),(40,36),(40,22)]
for c,t in zip(ref,order):click(env,source[c]);click(env,t)
env.step(GameAction.ACTION5,data={},reasoning={"probe":"eval"})
print("original before clone",env.observation_space.levels_completed)
try:
    c=copy.deepcopy(env)
    print("clone made",c.observation_space.levels_completed)
    click(c,(52,58));click(c,(19,23))
    print("clone after two",c.observation_space.levels_completed)
    print("original after clone actions",env.observation_space.levels_completed)
except Exception as e:
    print("DEEP_COPY_ERR",type(e).__name__,repr(e))
