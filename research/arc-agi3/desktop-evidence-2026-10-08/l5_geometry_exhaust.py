from arc_agi import Arcade,OperationMode
from arcengine import GameAction
a=Arcade(operation_mode=OperationMode.NORMAL)
PRE3=[3,3,3,3,3,2,2,2,2,2,2,2,2,2,2,7,5,2,2,2,2,2,5,3,5,2,2,2,5,3,5,5,4,5,7,2,5,2,2,2,2,3,5,1,1,1,1,1,1,1,1,3,3,3,3,5,1,1,1,1,1,1,1,1,5,4,4,4,4,4,4,4,4,2,2,2,5,3,3,3,3,3,3,3,3,2,2,2,2,2,2,2,2,2,2,2,2,2]
L4=[2]*6+[5]+[4]*7+[5]+[4]*7
e=a.make('ar25');r=None
for z in PRE3+L4:r=e.step(GameAction.from_id(z),data={})
g=e._game;T={(t.x,t.y) for t in g.fswikrcrdmx};W,H=g.dqwpuqcubca,g.height
print("LEVEL",g.level_index,"LC",r.levels_completed)
print("CARRIERS",[(s.x,s.y,s.pixels.shape,sorted(s.tags)) for s in g.jtkyjqznbnp])
s=g.ouurgkpbbjj[0]
cells=[(dx,dy) for dy,row in enumerate(s.pixels) for dx,v in enumerate(row) if int(v)>=0]
print("PAYLOAD",(s.x,s.y),s.pixels.tolist(),cells)
print("TARGETS",len(T),sorted(T))
def footprint(x,y,ax,ay):
 out=set()
 for dx,dy in cells:
  px,py=x+dx,y+dy
  xs={px,2*ax-px};ys={py,2*ay-py}
  for xx in xs:
   for yy in ys:
    if 0<=xx<W and 0<=yy<H:out.add((xx,yy))
 return out&T
best=(0,None)
for ax in range(-10,W+11):
 for ay in range(-10,H+11):
  for x in range(-6,W+6):
   for y in range(-6,H+6):
    u=footprint(x,y,ax,ay);n=len(u)
    if n>best[0]:
      best=(n,(ax,ay,x,y,T-u))
      if n>=18: print("BEST",n,"AX",ax,ay,"P",x,y,"MISS",sorted(T-u))
    if n==len(T):
      print("SOLVE_GEOM","AX",ax,ay,"P",x,y);raise SystemExit
print("NO_SOLVE",best)
