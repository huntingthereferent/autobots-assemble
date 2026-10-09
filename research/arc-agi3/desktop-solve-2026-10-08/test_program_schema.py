import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
from program_schema import induce_program

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
print("L0",induce_program(env.observation_space))

def click(x,y):
    a=GameAction.ACTION6;a.set_data({"x":x,"y":y})
    env.step(a,data={"x":x,"y":y},reasoning={"probe":"advance"})
p0={14:(19,58),15:(27,58),9:(35,58),11:(43,58)}
for c,s in zip([9,14,11,15],[(22,29),(28,29),(34,29),(40,29)]):
    click(*p0[c]);click(*s)
env.step(GameAction.ACTION5,data={},reasoning={"probe":"eval"})
print("LEVEL",env.observation_space.levels_completed)
print("L1",induce_program(env.observation_space))
