import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
from reference_transfer import parse_reference_transfer

def click(env,xy):
    a=GameAction.ACTION6;a.set_data({"x":xy[0],"y":xy[1]})
    return env.step(a,data={"x":xy[0],"y":xy[1]},reasoning={"probe":"parser test"})

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
print("L0",parse_reference_transfer(env.observation_space))
# known L0
for s,t in [((35,58),(22,29)),((19,58),(28,29)),((43,58),(34,29)),((27,58),(40,29))]:
    click(env,s);click(env,t)
env.step(GameAction.ACTION5,data={},reasoning={"probe":"eval"})
print("L1",parse_reference_transfer(env.observation_space))
# known L1
ref=[12,15,8,9,14,11,6]
src={8:(10,58),15:(17,58),14:(24,58),12:(31,58),6:(38,58),9:(45,58),11:(52,58)}
ord=[(22,22),(28,22),(22,36),(28,36),(34,36),(40,36),(40,22)]
for c,t in zip(ref,ord):click(env,src[c]);click(env,t)
env.step(GameAction.ACTION5,data={},reasoning={"probe":"eval"})
print("L2",parse_reference_transfer(env.observation_space))
