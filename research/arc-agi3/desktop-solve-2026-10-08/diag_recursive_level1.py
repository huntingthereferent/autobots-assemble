import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
from recursive_program import grid,find_rectangles,detect_positions,solve_program

def click(env,xy):
 a=GameAction.ACTION6;a.set_data({"x":xy[0],"y":xy[1]});return env.step(a,data={"x":xy[0],"y":xy[1]},reasoning={"probe":"advance"})

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
sol=solve_program(env.observation_space)
for m in sol["moves"]:
 click(env,m["source"]);click(env,m["dest"])
env.step(GameAction.ACTION5,data={},reasoning={"probe":"eval"})
g=grid(env.observation_space)
print("RECTS",find_rectangles(g))
pos,bg=detect_positions(g)
print("BG",bg)
print("POS",sorted([(k,None if v is None else (v.kind,v.color)) for k,v in pos.items() if 10<k[1]<50]))
