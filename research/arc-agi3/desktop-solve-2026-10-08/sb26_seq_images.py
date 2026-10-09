import numpy as np
from PIL import Image
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

pal=np.array([
[0,0,0],[0,116,217],[255,65,54],[46,204,64],[255,220,0],[170,170,170],[240,18,190],[255,133,27],
[127,219,255],[135,12,37],[0,0,0],[255,255,255],[128,128,128],[128,0,128],[0,128,128],[255,165,0]
],dtype=np.uint8)

def save(obs,name):
    a=np.asarray(obs.frame)
    if a.ndim==3:a=a[-1]
    a=a.reshape(64,64).astype(np.uint8)
    Image.fromarray(pal[a]).resize((512,512),Image.Resampling.NEAREST).save("C:/Users/teepa/arc3/solve/"+name+".png")

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
save(env.observation_space,"sb26_seq0")
a=GameAction.ACTION6;a.set_data({"x":19,"y":58})
env.step(a,data={"x":19,"y":58},reasoning={"probe":"palette"})
save(env.observation_space,"sb26_seq1_teal")
a=GameAction.ACTION6;a.set_data({"x":22,"y":29})
env.step(a,data={"x":22,"y":29},reasoning={"probe":"slot"})
save(env.observation_space,"sb26_seq2_slot")
env.step(GameAction.ACTION5,data={},reasoning={"probe":"evaluate"})
save(env.observation_space,"sb26_seq3_eval")
print("levels",env.observation_space.levels_completed,"state",env.observation_space.state)
