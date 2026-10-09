import json
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
from typed_program_schema import induce_typed_program

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")

def act(aname,data):
    a=getattr(GameAction,aname)
    if a is GameAction.ACTION6:
        x,y=data;a.set_data({"x":x,"y":y})
        return env.step(a,data={"x":x,"y":y},reasoning={"probe":"typed_schema"})
    return env.step(a,data={},reasoning={"probe":"typed_schema"})

for _ in range(8):
    obs=env.observation_space
    lvl=int(obs.levels_completed)
    meta=induce_typed_program(obs)
    print("\nLEVEL",lvl)
    if not meta:
        print("NO_META");break
    print("ROOT",meta["root"],"TARGET",meta["target"])
    print("CALLS",meta["call_palette"],"LITERALS",meta["literal_palette"])
    print("ASSIGN",meta["assignments"])
    print("PLANLEN",len(meta["plan"]))
    for aname,data in meta["plan"]:
        obs=act(aname,data)
    print("AFTER",obs.levels_completed,obs.state)
    if int(obs.levels_completed)<=lvl:
        print("DID_NOT_ADVANCE");break
