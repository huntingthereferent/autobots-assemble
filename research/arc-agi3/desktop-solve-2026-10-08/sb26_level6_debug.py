import numpy as np, json
from PIL import Image
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
from typed_program_schema import induce_typed_program,_clean_frames,_palette,_parse_routines,_target
from program_schema import _clusters_inside
from latent import grid,perceive

PAL=np.array([
[0,0,0],[0,116,217],[255,65,54],[46,204,64],[255,220,0],[170,170,170],[240,18,190],[255,133,27],
[127,219,255],[135,12,37],[0,0,0],[255,255,255],[128,128,128],[128,0,128],[0,128,128],[255,165,0]
],dtype=np.uint8)

def act(env,aname,data):
    a=getattr(GameAction,aname)
    if a is GameAction.ACTION6:
        x,y=data;a.set_data({"x":x,"y":y})
        return env.step(a,data={"x":x,"y":y},reasoning={"probe":"advance"})
    return env.step(a,data={},reasoning={"probe":"advance"})

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
for _ in range(6):
    m=induce_typed_program(env.observation_space)
    assert m, ("failed before l6",env.observation_space.levels_completed)
    for aname,data in m["plan"]: act(env,aname,data)
obs=env.observation_space
print("LEVEL",obs.levels_completed)
g=grid(obs)
Image.fromarray(PAL[g.astype(np.uint8)]).resize((512,512),Image.Resampling.NEAREST).save("C:/Users/teepa/arc3/solve/sb26_level6.png")
frames=_clean_frames(obs)
print("FRAMES",frames)
term,routines=_parse_routines(obs,frames)
print("TERM",term)
print("ROUTINES",routines)
if routines:
    lit,calls,toks=_palette(obs,set(routines))
    print("PALETTE LIT",lit,"CALL",calls,"TOKENS",toks)
    print("TARGET",_target(obs,set(lit)|set(calls)))
print("META",induce_typed_program(obs))
print("OBJECTS")
for o in perceive(obs).objects:
    if o.size<=300:
        w=o.x1-o.x0+1;h=o.y1-o.y0+1
        print("c",o.color,"n",o.size,"box",(o.x0,o.y0,o.x1,o.y1),"wh",(w,h),"solid",o.size==w*h,"center",(o.center2[0]//2,o.center2[1]//2))
