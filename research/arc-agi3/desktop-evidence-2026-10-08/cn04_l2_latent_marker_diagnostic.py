from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np

a=Arcade(operation_mode=OperationMode.NORMAL)
e=a.make("cn04");r=None
for z,data in [(6,{"x":41,"y":31}),(5,{})]+[(3,{})]*10+[(1,{})]:
 r=e.step(GameAction.from_id(z),data=data)

def latent_markers(game,s):
 A=game.hlxyvcmpk[s.name]
 pts=[]
 for y in range(A.shape[0]):
  for x in range(A.shape[1]):
   if int(A[y,x]) not in (8,13):continue
   rot=s.rotation%360
   if rot==0:xx,yy=x,y
   elif rot==90:xx,yy=y,A.shape[0]-1-x
   elif rot==180:xx,yy=A.shape[1]-1-x,A.shape[0]-1-y
   elif rot==270:xx,yy=A.shape[1]-1-y,x
   pts.append((s.x+xx,s.y+yy,int(A[y,x]),(x,y)))
 return sorted(pts)

sp=list(e._game.current_level.get_sprites())
print("INITIAL")
for i,s in enumerate(sp):
 print(i,"POS",s.x,s.y,"ROT",s.rotation,"RAW_SH",e._game.hlxyvcmpk[s.name].shape,"LM",latent_markers(e._game,s))

# reproduce final candidate using direct public moves from previous script
# use internal current selection switching only for compact diagnostic, not solving
# object1
e._game.swfljqaiqu(sp[1])
for _ in range(4):r=e.step(GameAction.from_id(3),data={})
for _ in range(8):r=e.step(GameAction.from_id(2),data={})
# object2
sp=list(e._game.current_level.get_sprites());e._game.swfljqaiqu(sp[2])
for _ in range(6):r=e.step(GameAction.from_id(2),data={})
# object3
sp=list(e._game.current_level.get_sprites());e._game.swfljqaiqu(sp[3])
r=e.step(GameAction.from_id(5),data={})
for _ in range(6):r=e.step(GameAction.from_id(3),data={})
for _ in range(2):r=e.step(GameAction.from_id(1),data={})

print("FINAL")
sp=list(e._game.current_level.get_sprites())
for i,s in enumerate(sp):
 print(i,"POS",s.x,s.y,"ROT",s.rotation,"LM",latent_markers(e._game,s),"MATCHED",sorted(e._game.iahpylgry.get(s.name,set())))
print("CHECK",e._game.sjwqloivve())
