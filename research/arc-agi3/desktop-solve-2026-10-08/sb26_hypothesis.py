import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")

def click(x,y,label):
    a=GameAction.ACTION6
    a.set_data({"x":x,"y":y})
    o=env.step(a,data={"x":x,"y":y},reasoning={"probe":label})
    print(label,"levels",o.levels_completed,"state",o.state)

# visible reference order: maroon, teal, white, orange
palette={
 "teal":(19,58),
 "orange":(27,58),
 "maroon":(35,58),
 "white":(43,58),
}
slots=[(22,29),(28,29),(34,29),(40,29)]
for color,slot in zip(["maroon","teal","white","orange"],slots):
    click(*palette[color],"select_"+color)
    click(*slot,"write_"+color)
o=env.step(GameAction.ACTION5,data={},reasoning={"probe":"evaluate_reference_copy"})
print("EVAL levels",o.levels_completed,"state",o.state,"win_levels",o.win_levels)
