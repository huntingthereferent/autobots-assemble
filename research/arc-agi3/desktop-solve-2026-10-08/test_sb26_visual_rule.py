import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
# Visual inference:
# reference colors left->right: 9,14,11,15
# bottom source positions: 14@19, 15@27, 9@35, 11@43
# middle destinations: 22,28,34,40
moves=[((35,58),(22,29)),((19,58),(28,29)),((43,58),(34,29)),((27,58),(40,29))]
for i,(src,dst) in enumerate(moves,1):
    for xy,label in [(src,"select"),(dst,"place")]:
        a=GameAction.ACTION6
        a.set_data({"x":xy[0],"y":xy[1]})
        o=env.step(a,data={"x":xy[0],"y":xy[1]},reasoning={"probe":label})
        print(i,label,xy,"levels",o.levels_completed,"state",o.state)
o=env.step(GameAction.ACTION5,data={},reasoning={"probe":"evaluate visible reference match"})
print("EVAL levels",o.levels_completed,"state",o.state,"win_levels",o.win_levels)
