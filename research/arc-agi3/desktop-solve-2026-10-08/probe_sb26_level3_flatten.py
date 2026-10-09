import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
env.step(GameAction.RESET,data={},reasoning={"p":"r"})

# L0
for color,slot in zip([9,14,11,15],[(22,29),(28,29),(34,29),(40,29)]):
    p={14:(19,58),15:(27,58),9:(35,58),11:(43,58)}[color]
    env.step(GameAction.ACTION6,data={"x":p[0],"y":p[1]},reasoning={"p":"s0"})
    env.step(GameAction.ACTION6,data={"x":slot[0],"y":slot[1]},reasoning={"p":"a0"})
env.step(GameAction.ACTION5,data={},reasoning={"p":"g0"})

# L1
for color,slot in zip([12,15,8,9,14,11,6],[(22,22),(28,22),(22,36),(28,36),(34,36),(40,36),(40,22)]):
    p={8:(10,58),15:(17,58),14:(24,58),12:(31,58),6:(38,58),9:(45,58),11:(52,58)}[color]
    env.step(GameAction.ACTION6,data={"x":p[0],"y":p[1]},reasoning={"p":"s1"})
    env.step(GameAction.ACTION6,data={"x":slot[0],"y":slot[1]},reasoning={"p":"a1"})
env.step(GameAction.ACTION5,data={},reasoning={"p":"g1"})

print("level",env.observation_space.levels_completed)
target=[8,14,15,11,6,9,12]
tokens={12:(10,58),14:(17,58),15:(24,58),11:(31,58),9:(38,58),6:(45,58),8:(52,58)}
order=[(19,23),(19,35),(25,35),(31,23),(37,35),(43,35),(43,23)]
for color,slot in zip(target,order):
    p=tokens[color]
    env.step(GameAction.ACTION6,data={"x":p[0],"y":p[1]},reasoning={"p":"s2"})
    o=env.step(GameAction.ACTION6,data={"x":slot[0],"y":slot[1]},reasoning={"p":"a2"})
    print("assign",color,slot,"lvl",o.levels_completed)
print("before",env.observation_space.levels_completed)
for i in range(3):
    o=env.step(GameAction.ACTION5,data={},reasoning={"p":"g2"})
    print("go",i+1,o.levels_completed,o.state)
    if o.levels_completed>=3: break
