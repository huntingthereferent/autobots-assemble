from itertools import product
import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

controls=[(19,58),(27,58),(35,58),(43,58)]
arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
tries=0
for L in range(1,6):
    for seq in product(range(len(controls)), repeat=L):
        env.step(GameAction.RESET,data={},reasoning={"probe":"latent_reset"})
        for idx in seq:
            x,y=controls[idx]
            a=GameAction.ACTION6
            a.set_data({"x":x,"y":y})
            o=env.step(a,data={"x":x,"y":y},reasoning={"probe":"latent_structural_control"})
            if o.levels_completed>0:
                print("FOUND_BY_CLICK",seq,"len",L,"tries",tries)
                raise SystemExit
        o=env.step(GameAction.ACTION5,data={},reasoning={"probe":"latent_evaluate"})
        tries+=1
        if o.levels_completed>0:
            print("FOUND",seq,"len",L,"tries",tries,"state",o.state)
            raise SystemExit
    print("done length",L,"tries",tries)
print("NOT_FOUND","tries",tries)
