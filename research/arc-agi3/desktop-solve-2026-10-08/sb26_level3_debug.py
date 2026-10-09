import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
from program_schema import induce_program,_frame_candidates,_clusters_inside,_bg
from latent import grid,perceive

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
def do_plan(meta):
    for aname,data in meta["plan"]:
        a=getattr(GameAction,aname)
        if a is GameAction.ACTION6:
            a.set_data({"x":data[0],"y":data[1]})
            env.step(a,data={"x":data[0],"y":data[1]},reasoning={"probe":"advance"})
        else:
            env.step(a,data={},reasoning={"probe":"advance"})
for _ in range(3):
    m=induce_program(env.observation_space)
    print("advance meta?",bool(m),"level",env.observation_space.levels_completed)
    do_plan(m)
obs=env.observation_space
g=grid(obs)
print("LEVEL",obs.levels_completed,"BG",_bg(g))
frames=_frame_candidates(obs)
print("FRAMES")
for r in frames:
    print(r,"clusters",_clusters_inside(g,r))
print("OBJECTS")
for i,o in enumerate(perceive(obs).objects):
    if o.size<=256:
        print(i,"c",o.color,"n",o.size,"box",(o.x0,o.y0,o.x1,o.y1),"center",o.center2)
print("INDUCE",induce_program(obs))
