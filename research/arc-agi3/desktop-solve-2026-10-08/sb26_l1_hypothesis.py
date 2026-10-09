import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
def click(x,y,label):
    a=GameAction.ACTION6;a.set_data({"x":x,"y":y})
    o=env.step(a,data={"x":x,"y":y},reasoning={"probe":label})
    return o

# solve level0 from visible relation
p0={14:(19,58),15:(27,58),9:(35,58),11:(43,58)}
for c,s in zip([9,14,11,15],[(22,29),(28,29),(34,29),(40,29)]):
    click(*p0[c],"l0_palette"); click(*s,"l0_slot")
env.step(GameAction.ACTION5,data={},reasoning={"probe":"l0_eval"})
print("after l0",env.observation_space.levels_completed)

# level1 visible mapping
p1={8:(10,58),15:(17,58),14:(24,58),12:(31,58),6:(38,58),9:(45,58),11:(52,58)}
refs=[12,15,8,9,14,11,6]
slots=[(22,22),(28,22),(40,22),(22,36),(28,36),(34,36),(40,36)]
for c,s in zip(refs,slots):
    click(*p1[c],"l1_palette"); click(*s,"l1_slot")
o=env.step(GameAction.ACTION5,data={},reasoning={"probe":"l1_eval"})
print("after l1 eval levels",o.levels_completed,"state",o.state,"win_levels",o.win_levels)
