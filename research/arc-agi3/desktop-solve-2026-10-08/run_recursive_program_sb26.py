import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
from recursive_program import solve_program

def click(env,xy,why):
    a=GameAction.ACTION6
    a.set_data({"x":int(xy[0]),"y":int(xy[1])})
    return env.step(a,data={"x":int(xy[0]),"y":int(xy[1])},reasoning={"rule":"recursive-program","why":why})

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
total=0
for k in range(12):
    obs=env.observation_space
    print("\nLEVEL",obs.levels_completed,"/",obs.win_levels)
    if obs.levels_completed>=obs.win_levels:
        print("SOLVED_ALL",total)
        break
    sol=solve_program(obs)
    print("STATUS",sol["status"] if sol else None)
    if sol:
        print("TARGET",sol.get("target"))
        print("FLAT",sol.get("flat"))
        print("MOVES",[(m["source"],m["dest"],(m["token"].kind,m["token"].color),m["container_color"]) for m in sol.get("moves",[])])
        print("CONTAINERS",[(c.color,c.rect,[(p.x,p.y,None if p.token is None else (p.token.kind,p.token.color)) for p in c.positions]) for c in sol.get("containers",[])])
    if not sol or sol.get("status")!="solved":
        break
    before=obs.levels_completed
    for m in sol["moves"]:
        click(env,m["source"],"select inferred token")
        click(env,m["dest"],"place token in inferred program slot")
        total+=2
    obs=env.step(GameAction.ACTION5,data={},reasoning={"rule":"recursive-program","why":"evaluate program whose expansion matches visible target"})
    total+=1
    print("EVAL",obs.levels_completed,obs.state,"total",total)
    if obs.levels_completed<=before:
        print("NO_PROGRESS")
        break
