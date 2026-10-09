import numpy as np
from PIL import Image
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

PAL=np.array([
 [0,0,0],[0,116,217],[255,65,54],[46,204,64],
 [255,220,0],[170,170,170],[240,18,190],[255,133,27],
 [127,219,255],[135,12,37],[0,0,0],[255,255,255],
 [128,128,128],[128,0,128],[0,128,128],[255,165,0]
],dtype=np.uint8)

def click(env,x,y,label):
    a=GameAction.ACTION6; a.set_data({"x":x,"y":y})
    return env.step(a,data={"x":x,"y":y},reasoning={"diag":label})

def reach_l2(env):
    for sx,sy,tx,ty in [(35,58,22,29),(19,58,28,29),(43,58,34,29),(27,58,40,29)]:
        click(env,sx,sy,"l1s"); click(env,tx,ty,"l1a")
    out=env.step(GameAction.ACTION5,data={},reasoning={"diag":"l1eval"})
    assert out.levels_completed==1

def save(obs,name):
    a=np.asarray(obs.frame)
    if a.ndim==3:a=a[-1]
    a=a.reshape(64,64).astype(np.uint8)
    Image.fromarray(PAL[a]).resize((512,512),Image.Resampling.NEAREST).save("C:/Users/teepa/arc3/solve/"+name+".png")

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
# initial level2 base cannot be restored by RESET after reaching? Re-reach for each probe.
probes=[("token8",10,58),("token14",24,58),("token12",31,58)]
for name,sx,sy in probes:
    # Fresh environment instance per probe.
    env=arc.make("sb26")
    reach_l2(env)
    click(env,sx,sy,name+"_select")
    out=click(env,22,36,name+"_lower0")
    print(name,"levels",out.levels_completed,"state",out.state)
    save(out,"sb26_l2_"+name+"_lower0")
