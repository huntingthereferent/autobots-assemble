import sys, numpy as np
sys.path.insert(0,r"C:\Users\teepa\arc3\solve\g2")
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
from latent import grid, components, delta_signature

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("m0r0")
o=env.observation_space
g=grid(o)
print("STATE",o.state,"LEVELS",o.levels_completed,"ACTIONS",o.available_actions)
print("COLORS",dict(zip(*[list(map(int,x)) for x in np.unique(g,return_counts=True)])))
print("COMPONENTS")
for c in sorted(components(g),key=lambda q:(q["y0"],q["x0"],q["color"],q["size"])):
    if c["size"]<400:
        print(c)
print("ONE_STEP")
for a in GameAction:
    if a is GameAction.RESET: continue
    try:
        env.step(GameAction.RESET,data={},reasoning={"probe":"reset"})
        b=env.observation_space
        if a is GameAction.ACTION6:
            continue
        z=env.step(a,data={},reasoning={"probe":"single"})
        print(a.name,delta_signature(b,z),"level",z.levels_completed,"state",z.state)
    except Exception as e:
        print(a.name,"ERR",repr(e))
