from itertools import permutations
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

def click(env,xy,why):
    a=GameAction.ACTION6; a.set_data({"x":xy[0],"y":xy[1]})
    return env.step(a,data={"x":xy[0],"y":xy[1]},reasoning={"probe":why})

def solve_l0(env):
    for s,d in [((35,58),(22,29)),((19,58),(28,29)),((43,58),(34,29)),((27,58),(40,29))]:
        click(env,s,"L0");click(env,d,"L0")
    return env.step(GameAction.ACTION5,data={},reasoning={"probe":"L0 eval"})

def solve_l1(env):
    ref=[12,15,8,9,14,11,6]
    source={8:(10,58),15:(17,58),14:(24,58),12:(31,58),6:(38,58),9:(45,58),11:(52,58)}
    order=[(22,22),(28,22),(22,36),(28,36),(34,36),(40,36),(40,22)]
    for c,d in zip(ref,order):
        click(env,source[c],"L1");click(env,d,"L1")
    return env.step(GameAction.ACTION5,data={},reasoning={"probe":"L1 eval"})

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
ref=[8,14,15,11,6,9,12]
source={12:(10,58),14:(17,58),15:(24,58),11:(31,58),9:(38,58),6:(45,58),8:(52,58)}
slots=[(19,23),(31,23),(43,23),(19,35),(25,35),(37,35),(43,35)]
tries=0
for order in permutations(slots):
    env.step(GameAction.RESET,data={},reasoning={"probe":"full reset"})
    if solve_l0(env).levels_completed!=1:
        print("L0_FAIL");break
    if solve_l1(env).levels_completed!=2:
        print("L1_FAIL");break
    for c,d in zip(ref,order):
        click(env,source[c],"candidate select");click(env,d,"candidate place")
    o=env.step(GameAction.ACTION5,data={},reasoning={"probe":"candidate evaluate"})
    tries+=1
    if o.levels_completed>2:
        print("FOUND",order,"tries",tries,"levels",o.levels_completed)
        break
    if tries%250==0:
        print("tries",tries,flush=True)
else:
    print("NOT_FOUND",tries)
