import numpy as np
from PIL import Image
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
from latent import grid,effect

PAL=np.array([
[0,0,0],[0,116,217],[255,65,54],[46,204,64],[255,220,0],[170,170,170],[240,18,190],[255,133,27],
[127,219,255],[135,12,37],[0,0,0],[255,255,255],[128,128,128],[128,0,128],[0,128,128],[255,165,0]
],dtype=np.uint8)

def save(obs,name):
    a=grid(obs).astype(np.uint8)
    Image.fromarray(PAL[a]).resize((512,512),Image.Resampling.NEAREST).save("C:/Users/teepa/arc3/solve/"+name+".png")

def click(env,x,y,label):
    a=GameAction.ACTION6;a.set_data({"x":x,"y":y})
    before=env.observation_space
    out=env.step(a,data={"x":x,"y":y},reasoning={"probe":label})
    print(label,effect(before,out),"levels",out.levels_completed,"state",out.state)
    return out

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("vc33")
save(env.observation_space,"vc33_initial")
click(env,61,25,"upper")
save(env.observation_space,"vc33_after_upper")
env.step(GameAction.RESET,data={},reasoning={"probe":"reset"})
click(env,61,33,"lower")
save(env.observation_space,"vc33_after_lower")
