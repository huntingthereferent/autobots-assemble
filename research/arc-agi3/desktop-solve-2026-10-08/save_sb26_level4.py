import numpy as np
from PIL import Image
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
from reference_transfer import parse_reference_transfer

PAL=np.array([
[0,0,0],[0,116,217],[255,65,54],[46,204,64],
[255,220,0],[170,170,170],[240,18,190],[255,133,27],
[127,219,255],[135,12,37],[0,0,0],[255,255,255],
[128,128,128],[128,0,128],[0,128,128],[255,165,0]],dtype=np.uint8)

def click(env,xy):
 a=GameAction.ACTION6;a.set_data({"x":xy[0],"y":xy[1]});return env.step(a,data={"x":xy[0],"y":xy[1]},reasoning={"probe":"advance"})

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
for _ in range(3):
 p=parse_reference_transfer(env.observation_space)
 for c,t in zip(p["reference"],p["order"]):
  click(env,p["sources"][c]);click(env,t)
 env.step(GameAction.ACTION5,data={},reasoning={"probe":"eval"})
ref=[11,8,14,9,6,12,15]
src={11:(10,58),6:(17,58),12:(24,58),8:(31,58),15:(38,58),9:(45,58),14:(52,58)}
order=[(19,22),(25,22),(31,22),(31,36),(37,36),(37,22),(43,22)]
for c,t in zip(ref,order):
 click(env,src[c]);click(env,t)
env.step(GameAction.ACTION5,data={},reasoning={"probe":"eval"})
a=np.asarray(env.observation_space.frame)
if a.ndim==3:a=a[-1]
g=a.reshape(64,64).astype(np.uint8)
Image.fromarray(PAL[g]).resize((512,512),Image.Resampling.NEAREST).save("C:/Users/teepa/arc3/solve/sb26_level4.png")
print(env.observation_space.levels_completed)
