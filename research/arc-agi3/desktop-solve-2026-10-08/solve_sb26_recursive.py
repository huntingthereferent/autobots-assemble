import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
from reference_transfer import parse_reference_transfer

def click(env,xy,why):
    a=GameAction.ACTION6
    a.set_data({"x":int(xy[0]),"y":int(xy[1])})
    return env.step(a,data={"x":int(xy[0]),"y":int(xy[1])},reasoning={"rule":"recursive-reference-transfer","why":why})

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
actions=0
for step in range(12):
    obs=env.observation_space
    print("LEVEL",obs.levels_completed,"/",obs.win_levels,"state",obs.state)
    if obs.levels_completed>=obs.win_levels:
        print("SOLVED",actions)
        break
    p=parse_reference_transfer(obs)
    print("PARSE",p)
    if not p or p.get("status")!="ok":
        print("PARSE_FAIL")
        break
    before=obs.levels_completed
    for color,dst in zip(p["reference"],p["order"]):
        src=p["sources"][color]
        obs=click(env,src,f"select source color {color}")
        actions+=1
        obs=click(env,dst,f"place color {color} at recursively ordered destination")
        actions+=1
    obs=env.step(GameAction.ACTION5,data={},reasoning={"rule":"recursive-reference-transfer","why":"evaluate completed reference transfer"})
    actions+=1
    print("EVAL",obs.levels_completed,obs.state,"actions",actions)
    if obs.levels_completed<=before:
        print("NO_PROGRESS")
        break
