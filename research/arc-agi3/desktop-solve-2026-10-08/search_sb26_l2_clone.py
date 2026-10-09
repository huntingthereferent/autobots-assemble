from itertools import permutations
import copy
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

def click(env,xy,why):
    a=GameAction.ACTION6;a.set_data({"x":xy[0],"y":xy[1]})
    return env.step(a,data={"x":xy[0],"y":xy[1]},reasoning={"probe":why})

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
# reach level 2
for s,t in [((35,58),(22,29)),((19,58),(28,29)),((43,58),(34,29)),((27,58),(40,29))]:
    click(env,s,"L0");click(env,t,"L0")
env.step(GameAction.ACTION5,data={},reasoning={"probe":"L0 eval"})
ref1=[12,15,8,9,14,11,6]
src1={8:(10,58),15:(17,58),14:(24,58),12:(31,58),6:(38,58),9:(45,58),11:(52,58)}
ord1=[(22,22),(28,22),(22,36),(28,36),(34,36),(40,36),(40,22)]
for c,t in zip(ref1,ord1):click(env,src1[c],"L1");click(env,t,"L1")
env.step(GameAction.ACTION5,data={},reasoning={"probe":"L1 eval"})
print("base level",env.observation_space.levels_completed)

ref=[8,14,15,11,6,9,12]
src={12:(10,58),14:(17,58),15:(24,58),11:(31,58),9:(38,58),6:(45,58),8:(52,58)}
slots=[(19,23),(31,23),(43,23),(19,35),(25,35),(37,35),(43,35)]
tries=0
for order in permutations(slots):
    cenv=copy.deepcopy(env)
    for col,t in zip(ref,order):
        click(cenv,src[col],"search select");click(cenv,t,"search place")
    o=cenv.step(GameAction.ACTION5,data={},reasoning={"probe":"search eval"})
    tries+=1
    if o.levels_completed>2:
        print("FOUND",order,"tries",tries,"levels",o.levels_completed)
        break
    if tries%500==0:print("tries",tries,flush=True)
else:
    print("NOT_FOUND",tries)
