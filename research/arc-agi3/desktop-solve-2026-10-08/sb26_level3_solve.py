from __future__ import annotations
import sys
sys.path.insert(0,r"C:\Users\teepa\arc3\solve")
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
from latent_state import perceive
from program_synthesis import parse_synthesis

def click(env,xy,label):
 x,y=xy
 a=GameAction.ACTION6;a.set_data({"x":int(x),"y":int(y)})
 return env.step(a,data={"x":int(x),"y":int(y)},reasoning={"synth":label})

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26");obs=env.observation_space

# Advance first three levels using generic parser.
for _ in range(3):
 s=parse_synthesis(perceive(obs));pm={c:p for c,p in s.palette}
 for c,slot in zip(s.target,s.leaves):
  obs=click(env,pm[c],"select");obs=click(env,slot,"write")
 obs=env.step(GameAction.ACTION5,data={},reasoning={"synth":"execute"})

v=perceive(obs);s=parse_synthesis(v)
print("at",obs.levels_completed,"target",s.target,"root",s.routines[0].centers)
pm={c:p for c,p in s.palette}
root=list(s.routines[0].centers)

# Detect child routine frame: non-root frame-like component in program region,
# then collect a fixed solid symbol and placeholder leaves inside it.
target_y=s.routines[0].y0
bottom_y=max(p[1] for _,p in s.palette)
frames=[c for c in v.components if c.y0>target_y and c.y1<bottom_y and c.width>=12 and c.height>=8 and c.fill<0.5 and c.size>=20]
print("frames",[(c.color,c.size,c.box,c.fill) for c in frames])
child=max(frames,key=lambda c:c.y0)
inside=[c for c in v.components if c is not child and child.x0<=c.member_x<=child.x1 and child.y0<=c.member_y<=child.y1 and c.size<=20]
inside=sorted(inside,key=lambda c:c.member_x)
print("child",child.color,child.box,"inside",[(c.color,c.size,c.box) for c in inside])
# de-duplicate nested artifacts by x center, preferring solid non-background symbols
items=[]
for c in inside:
 if c.size not in (4,16):
  continue
 x=c.cx2//2
 if items and abs(items[-1][0]-x)<=1:
  if c.size>items[-1][1].size:items[-1]=(x,c)
 else:items.append((x,c))
items=[c for _,c in items]
print("items",[(c.color,c.size,c.box) for c in items])
placeholder=2
fixed=[c.color for c in items if c.color!=placeholder]
leaf_centers=[(c.cx2//2,c.cy2//2) for c in items if c.color==placeholder]
call_color=child.color
print("call_color",call_color,"fixed",fixed,"child_leaves",leaf_centers)

# One call is required because root 5 -> target 7 and child expansion is 3.
# Find target position matching the child's fixed first terminal.
T=list(s.target)
pos=None
for i,c in enumerate(T):
 if c==call_color and i+len(items)<=len(T):
  # Fixed positions in child must match.
  ok=True
  j=0
  for it in items:
   if it.color!=placeholder and T[i+j]!=it.color:ok=False
   j+=1
  if ok:
   pos=i;break
print("call_pos",pos)
if pos is None:raise SystemExit("no call placement")

# Program root flattened around call.
before=T[:pos]
child_target=T[pos:pos+len(items)]
after=T[pos+len(items):]
root_tokens=before+[("CALL",call_color)]+after
print("root_tokens",root_tokens,"child_target",child_target)
if len(root_tokens)!=len(root):raise SystemExit("root arity mismatch")

# Fill root and child leaves.
for tok,slot in zip(root_tokens,root):
 color=tok[1] if isinstance(tok,tuple) else tok
 obs=click(env,pm[color],f"select root {color}")
 obs=click(env,slot,"write root")
ci=0
for it,color in zip(items,child_target):
 if it.color==placeholder:
  obs=click(env,pm[color],f"select child {color}")
  obs=click(env,(it.cx2//2,it.cy2//2),"write child")
obs=env.step(GameAction.ACTION5,data={},reasoning={"synth":"execute synthesized call tree"})
print("RESULT",obs.levels_completed,obs.win_levels,obs.state)
from PIL import Image
import numpy as np
v2=perceive(obs)
print("NEXT_GROUPS")
for g in v2.horizontal_groups:
    print("G",g.y0,g.y1,g.colors,g.centers,g.member_pixels,g.component_sizes)
print("NEXT_COMPONENTS",[(c.color,c.size,c.box,(c.member_x,c.member_y),round(c.fill,2)) for c in v2.components if c.size<=600])
palimg=np.array([[0,0,0],[0,116,217],[255,65,54],[46,204,64],[255,220,0],[170,170,170],[240,18,190],[255,133,27],[127,219,255],[135,12,37],[0,0,0],[255,255,255],[128,128,128],[0,128,128],[0,128,128],[255,165,0]],dtype=np.uint8)
aa=np.asarray(obs.frame)
if aa.ndim==3:
    aa=aa[-1]
aa=aa.reshape(64,64).astype(np.uint8)
Image.fromarray(palimg[aa]).resize((512,512),Image.Resampling.NEAREST).save(r"C:\Users\teepa\arc3\solve\sb26_level4.png")
