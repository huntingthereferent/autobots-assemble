from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy,itertools
arc=Arcade(operation_mode=OperationMode.NORMAL); root=arc.make("cd82")
paths=[(),(1,),(5,),(6,),(3,),(4,),(1,1),(1,5),(5,1),(3,3),(4,4)]
for p in paths:
    e=copy.deepcopy(root); ok=True
    for z in p:
        try:
            if z==6:r=e.step(GameAction.ACTION6,data={"x":0,"y":0})
            else:r=e.step(GameAction.from_id(z),data={})
            if r.state.name!="NOT_FINISHED":ok=False;break
        except Exception as ex: ok=False;break
    if not ok: continue
    g=e._game
    a=[dict(x.data) for x in g.yrfgxhebei()]
    b=[dict(x.data) for x in g.bmwcxxvjum()]
    print("PATH",p,"xwm",g.xwmfgtlso,"palette",a,"special",b)
