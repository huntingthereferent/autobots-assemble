import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")

def click(p,label):
    a=GameAction.ACTION6
    a.set_data({"x":p[0],"y":p[1]})
    return env.step(a,data=a.action_data.model_dump(),reasoning={"probe":label})

def tick(n,label):
    out=None
    for i in range(n):
        out=click((63,63),f"{label}_tick_{i}")
    return out

# Reference row visible order: 9,14,11,15
# Bottom piece centers by color: 9@35, 14@19, 11@43, 15@27
# Middle empty slots left->right: x22,28,34,40 y29
moves=[
 ((35,58),(22,29),9),
 ((19,58),(28,29),14),
 ((43,58),(34,29),11),
 ((27,58),(40,29),15),
]
for i,(src,dst,c) in enumerate(moves,1):
    o=click(src,f"select_color_{c}")
    print("move",i,"select",c,"levels",o.levels_completed,"state",o.state)
    o=click(dst,f"place_color_{c}")
    print("move",i,"place","levels",o.levels_completed,"state",o.state)
    o=tick(7,f"settle_{i}")
    print("move",i,"settled","levels",o.levels_completed,"state",o.state)
    if "GAME_OVER" in str(o.state) or o.levels_completed>0: break

if env.observation_space.levels_completed==0 and "GAME_OVER" not in str(env.observation_space.state):
    o=env.step(GameAction.ACTION5,data={},reasoning={"probe":"evaluate_constructed_relation"})
    print("evaluate start","levels",o.levels_completed,"state",o.state)
    for i in range(60):
        o=click((63,63),f"eval_tick_{i}")
        if i%5==0 or o.levels_completed>0 or "GAME_OVER" in str(o.state):
            print("eval tick",i,"levels",o.levels_completed,"state",o.state)
        if o.levels_completed>0 or "GAME_OVER" in str(o.state) or "WIN" in str(o.state):
            break
