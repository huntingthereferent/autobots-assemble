from itertools import permutations
import copy
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
from reference_transfer import parse_reference_transfer

def click(env,xy,why):
    a=GameAction.ACTION6;a.set_data({"x":xy[0],"y":xy[1]})
    return env.step(a,data={"x":xy[0],"y":xy[1]},reasoning={"probe":why})

def solve_three(env):
    for _ in range(3):
        p=parse_reference_transfer(env.observation_space)
        if not p or p.get("status")!="ok":
            return False
        for c,t in zip(p["reference"],p["order"]):
            click(env,p["sources"][c],"advance");click(env,t,"advance")
        o=env.step(GameAction.ACTION5,data={},reasoning={"probe":"advance eval"})
    return env.observation_space.levels_completed==3

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
if not solve_three(env):
    print("ADVANCE_FAIL");raise SystemExit
print("base",env.observation_space.levels_completed)
ref=[11,8,14,9,6,12,15]
src={11:(10,58),6:(17,58),12:(24,58),8:(31,58),15:(38,58),9:(45,58),14:(52,58)}
slots=[(19,22),(25,22),(31,22),(37,22),(43,22),(31,36),(37,36)]
tries=0
for order in permutations(slots):
    cenv=copy.deepcopy(env)
    for col,t in zip(ref,order):
        click(cenv,src[col],"search select");click(cenv,t,"search place")
    o=cenv.step(GameAction.ACTION5,data={},reasoning={"probe":"search eval"})
    tries+=1
    if o.levels_completed>3:
        print("FOUND",order,"tries",tries,"levels",o.levels_completed)
        break
    if tries%500==0: print("tries",tries,flush=True)
else:
    print("NOT_FOUND",tries)
