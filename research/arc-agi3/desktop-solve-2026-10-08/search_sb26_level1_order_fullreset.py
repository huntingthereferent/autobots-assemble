from itertools import permutations
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

def click(env,xy,why):
    a=GameAction.ACTION6; a.set_data({"x":xy[0],"y":xy[1]})
    return env.step(a,data={"x":xy[0],"y":xy[1]},reasoning={"probe":why})

def advance_level0(env):
    for s,d in [((35,58),(22,29)),((19,58),(28,29)),((43,58),(34,29)),((27,58),(40,29))]:
        click(env,s,"replay visible rule"); click(env,d,"replay visible rule")
    return env.step(GameAction.ACTION5,data={},reasoning={"probe":"replay eval"})

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
ref=[12,15,8,9,14,11,6]
source={8:(10,58),15:(17,58),14:(24,58),12:(31,58),6:(38,58),9:(45,58),11:(52,58)}
slots=[(22,22),(28,22),(40,22),(22,36),(28,36),(34,36),(40,36)]
tries=0
for order in permutations(slots):
    env.step(GameAction.RESET,data={},reasoning={"probe":"full reset"})
    o=advance_level0(env)
    if o.levels_completed!=1:
        print("ADVANCE_FAIL",tries,o.levels_completed); break
    for color,dst in zip(ref,order):
        click(env,source[color],"candidate select")
        o=click(env,dst,"candidate place")
    o=env.step(GameAction.ACTION5,data={},reasoning={"probe":"candidate evaluate"})
    tries+=1
    if o.levels_completed>1:
        print("FOUND",order,"tries",tries,"levels",o.levels_completed)
        break
    if tries%250==0:
        print("tries",tries,flush=True)
else:
    print("NOT_FOUND",tries)
