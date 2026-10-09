import numpy as np
from PIL import Image
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

def click(env,x,y,label):
    a=GameAction.ACTION6
    a.set_data({"x":x,"y":y})
    return env.step(a,data={"x":x,"y":y},reasoning={"probe":label})

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
click(env,19,58,"select B14")
out=click(env,22,29,"apply M0")
a=np.asarray(out.frame)
if a.ndim==3:a=a[-1]
a=a.reshape(64,64).astype(np.uint8)
pal=np.array([
 [0,0,0],[0,116,217],[255,65,54],[46,204,64],
 [255,220,0],[170,170,170],[240,18,190],[255,133,27],
 [127,219,255],[135,12,37],[0,0,0],[255,255,255],
 [128,128,128],[128,0,128],[0,128,128],[255,165,0]
],dtype=np.uint8)
Image.fromarray(pal[a]).resize((512,512),Image.Resampling.NEAREST).save("C:/Users/teepa/arc3/solve/sb26_after_B14_M0.png")
