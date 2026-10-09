from collections import defaultdict
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
from latent import effect

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
for gid in ["ls20","sb26","g50t","vc33"]:
    env=arc.make(gid)
    print("\nGAME",gid,"avail",env.observation_space.available_actions)
    for a in GameAction:
        if a is GameAction.RESET: continue
        try:
            env.step(GameAction.RESET,data={},reasoning={"probe":"reset"})
            before=env.observation_space
            if a is GameAction.ACTION6:
                # one generic central click only for signature availability
                a.set_data({"x":32,"y":32})
            after=env.step(a,data={},reasoning={"probe":"effect"})
            e=effect(before,after)
            print(a.name,e.class_name,"pixels",e.changed_pixels,"bbox",e.bbox,"moved",e.moved[:3],"color_delta",e.color_delta[:5])
        except Exception as ex:
            print(a.name,"ERR",type(ex).__name__,str(ex)[:100])
