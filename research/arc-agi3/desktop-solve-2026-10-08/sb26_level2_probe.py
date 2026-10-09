import sys, numpy as np
from PIL import Image
sys.path.insert(0,r"C:\Users\teepa\arc3\solve")
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
from latent_state import perceive

pal=np.array([[0,0,0],[0,116,217],[255,65,54],[46,204,64],[255,220,0],[170,170,170],[240,18,190],[255,133,27],[127,219,255],[135,12,37],[0,0,0],[255,255,255],[128,128,128],[0,128,128],[0,128,128],[255,165,0]],dtype=np.uint8)

def click(env,x,y):
 a=GameAction.ACTION6;a.set_data({"x":x,"y":y})
 return env.step(a,data={"x":x,"y":y},reasoning={"p":"advance"})

def solve_level0(env,obs):
 palxy={14:(20,58),15:(28,58),9:(36,58),11:(44,58)}
 for color,slot in zip([9,14,11,15],[(22,29),(28,29),(34,29),(40,29)]):
  obs=click(env,*palxy[color]);obs=click(env,*slot)
 return env.step(GameAction.ACTION5,data={},reasoning={"p":"exec"})

def solve_level1(env,obs):
 # discovered generically from previous frame: target and flattened leaves
 v=perceive(obs);gs=sorted([g for g in v.horizontal_groups if len(g.colors)>=3],key=lambda g:g.y0)
 top=gs[0];bottom=gs[-1];rows=[g for g in gs[1:-1] if len(g.colors)==4]
 palette={c:p for c,p in zip(bottom.colors,bottom.member_pixels)}
 leaves=[rows[0].centers[0],rows[0].centers[1],*rows[1].centers,rows[0].centers[3]]
 for c,slot in zip(top.colors,leaves):
  obs=click(env,*palette[c]);obs=click(env,*slot)
 return env.step(GameAction.ACTION5,data={},reasoning={"p":"exec"})

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26");obs=env.observation_space
obs=solve_level0(env,obs);obs=solve_level1(env,obs)
print("levels",obs.levels_completed,"state",obs.state)
v=perceive(obs)
print("groups")
for g in v.horizontal_groups:
 print({"band":[g.y0,g.y1],"colors":g.colors,"centers":g.centers,"members":g.member_pixels,"sizes":g.component_sizes})
print("components",[(c.color,c.size,c.box,(c.member_x,c.member_y),round(c.fill,2)) for c in v.components if c.size<=300][:180])
a=np.asarray(obs.frame)
if a.ndim==3:a=a[-1]
a=a.reshape(64,64).astype(np.uint8)
Image.fromarray(pal[a]).resize((512,512),Image.Resampling.NEAREST).save("C:/Users/teepa/arc3/solve/sb26_level2.png")
