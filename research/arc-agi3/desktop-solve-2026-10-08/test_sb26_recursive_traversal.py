import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")

def click(p,label):
    a=GameAction.ACTION6;a.set_data({"x":p[0],"y":p[1]})
    return env.step(a,data=a.action_data.model_dump(),reasoning={"probe":label})

def settle(n=7):
    o=None
    for i in range(n): o=click((63,63),f"settle_{i}")
    return o

# solve public level 0 using previously source-free inferred relation
for src,dst in [((35,58),(22,29)),((19,58),(28,29)),((43,58),(34,29)),((27,58),(40,29))]:
    click(src,"l0_select"); click(dst,"l0_place"); settle()
o=env.step(GameAction.ACTION5,data={},reasoning={"probe":"l0_eval"})
print("after l0",o.levels_completed,o.state)

# Level 1 visible reference order: [12,15,8,9,14,11,6]
# Visible bottom palette centers by color:
src={8:(11,58),15:(18,58),14:(25,58),12:(32,58),6:(39,58),9:(46,58),11:(53,58)}
# Visible frame traversal inferred from geometry:
# upper: slot x22, x28, link(color14 child), x40
# child/lower: x22,x28,x34,x40
path=[
 (12,(22,22)),
 (15,(28,22)),
 (8,(22,36)),
 (9,(28,36)),
 (14,(34,36)),
 (11,(40,36)),
 (6,(40,22)),
]
for i,(c,dst) in enumerate(path,1):
    o=click(src[c],f"l1_select_{c}")
    o=click(dst,f"l1_place_{c}")
    o=settle()
    print("place",i,c,"levels",o.levels_completed,"state",o.state)
    if "GAME_OVER" in str(o.state): break

if "GAME_OVER" not in str(env.observation_space.state):
    o=env.step(GameAction.ACTION5,data={},reasoning={"probe":"l1_eval"})
    print("evaluate","levels",o.levels_completed,"state",o.state,"win_levels",o.win_levels)
