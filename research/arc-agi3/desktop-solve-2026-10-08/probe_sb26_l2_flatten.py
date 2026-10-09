import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

def click(env,x,y,label):
    a=GameAction.ACTION6; a.set_data({"x":x,"y":y})
    out=env.step(a,data={"x":x,"y":y},reasoning={"diag":label})
    print(label,"level",out.levels_completed)
    return out

def reach_l2(env):
    for sx,sy,tx,ty in [(35,58,22,29),(19,58,28,29),(43,58,34,29),(27,58,40,29)]:
        click(env,sx,sy,"l1s"); click(env,tx,ty,"l1a")
    out=env.step(GameAction.ACTION5,data={},reasoning={"diag":"l1eval"})
    assert out.levels_completed==1

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
reach_l2(env)

# Visible level-2 flatten order:
# upper slots 0,1 ; fixed call to lower box ; upper slot3
# lower slots 0..3
placements=[
    (31,58,22,22,"upper0=12"),
    (17,58,28,22,"upper1=15"),
    (38,58,40,22,"upper3=6"),
    (10,58,22,36,"lower0=8"),
    (45,58,28,36,"lower1=9"),
    (24,58,34,36,"lower2=14"),
    (52,58,40,36,"lower3=11"),
]
for sx,sy,tx,ty,label in placements:
    click(env,sx,sy,label+" select")
    click(env,tx,ty,label+" apply")
out=env.step(GameAction.ACTION5,data={},reasoning={"diag":"eval_flattened_visible_call_graph"})
print("FINAL","levels",out.levels_completed,"state",out.state)
