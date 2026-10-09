import sys,numpy as np
from PIL import Image
sys.path.insert(0,"C:/Users/teepa/arc3/solve")
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
from latent_state import perceive
from program_synthesis import parse_synthesis

P=np.array([[0,0,0],[0,116,217],[255,65,54],[46,204,64],[255,220,0],[170,170,170],[240,18,190],[255,133,27],[127,219,255],[135,12,37],[0,0,0],[255,255,255],[128,128,128],[0,128,128],[0,128,128],[255,165,0]],dtype=np.uint8)

def ck(e,p):
 a=GameAction.ACTION6
 a.set_data({"x":int(p[0]),"y":int(p[1])})
 return e.step(a,data={"x":int(p[0]),"y":int(p[1])},reasoning={"x":"x"})

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
e=arc.make("sb26");o=e.observation_space
for q in range(3):
 s=parse_synthesis(perceive(o))
 pm={c:p for c,p in s.palette}
 for c,p in zip(s.target,s.leaves):
  o=ck(e,pm[c]);o=ck(e,p)
 o=e.step(GameAction.ACTION5,data={},reasoning={"x":"x"})
print("L",o.levels_completed,o.state)
v=perceive(o)
for g in v.horizontal_groups:
 print("G",g.y0,g.y1,g.colors,g.centers,g.member_pixels,g.component_sizes)
for c in v.components:
 if c.size<=500:
  print("C",c.color,c.size,c.box,c.member_x,c.member_y,round(c.fill,2))
a=np.asarray(o.frame)
if a.ndim==3:a=a[-1]
a=a.reshape(64,64).astype(np.uint8)
Image.fromarray(P[a]).resize((512,512),Image.Resampling.NEAREST).save("C:/Users/teepa/arc3/solve/l3.png")
