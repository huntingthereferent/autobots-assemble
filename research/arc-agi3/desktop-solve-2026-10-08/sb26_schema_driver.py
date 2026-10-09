import json, numpy as np
from PIL import Image
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
from program_schema import induce_program

PAL=np.array([
[0,0,0],[0,116,217],[255,65,54],[46,204,64],[255,220,0],[170,170,170],[240,18,190],[255,133,27],
[127,219,255],[135,12,37],[0,0,0],[255,255,255],[128,128,128],[128,0,128],[0,128,128],[255,165,0]
],dtype=np.uint8)

def save(obs,name):
    a=np.asarray(obs.frame)
    if a.ndim==3:a=a[-1]
    a=a.reshape(64,64).astype(np.uint8)
    Image.fromarray(PAL[a]).resize((512,512),Image.Resampling.NEAREST).save("C:/Users/teepa/arc3/solve/"+name+".png")

def do(env,aname,data):
    a=getattr(GameAction,aname)
    if a is GameAction.ACTION6 and data is not None:
        a.set_data({"x":int(data[0]),"y":int(data[1])})
        return env.step(a,data={"x":int(data[0]),"y":int(data[1])},reasoning={"probe":"schema_driver"})
    return env.step(a,data={},reasoning={"probe":"schema_driver"})

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
for expected in range(8):
    obs=env.observation_space
    lvl=int(obs.levels_completed)
    meta=induce_program(obs)
    print("LEVEL",lvl,"META",json.dumps(meta,default=str)[:12000] if meta else None)
    save(obs,f"sb26_driver_level{lvl}")
    if not meta:
        print("FAIL_AT",lvl)
        break
    for aname,data in meta["plan"]:
        obs=do(env,aname,data)
    print("AFTER_PLAN",obs.levels_completed,obs.state)
    if int(obs.levels_completed)<=lvl:
        print("PLAN_DID_NOT_ADVANCE",lvl)
        break
