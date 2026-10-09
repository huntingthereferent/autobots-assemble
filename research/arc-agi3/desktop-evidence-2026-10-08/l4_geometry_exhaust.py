from arc_agi import Arcade,OperationMode
from arcengine import GameAction
a=Arcade(operation_mode=OperationMode.NORMAL)
PRE=[3,3,3,3,3,2,2,2,2,2,2,2,2,2,2,7,5,2,2,2,2,2,5,3,5,2,2,2,5,3,5,5,4,5,7,2,5,2,2,2,2,3,5,1,1,1,1,1,1,1,1,3,3,3,3,5,1,1,1,1,1,1,1,1,5,4,4,4,4,4,4,4,4,2,2,2,5,3,3,3,3,3,3,3,3,2,2,2,2,2,2,2,2,2,2,2,2,2]
e=a.make('ar25');r=None
for z in PRE:r=e.step(GameAction.from_id(z),data={})
g=e._game;T={(t.x,t.y) for t in g.fswikrcrdmx};W,H=g.dqwpuqcubca,g.height
print("LEVEL",g.level_index,"LC",r.levels_completed,"CARRIER",(g.lakiokfgmlc.x,g.lakiokfgmlc.y))
shapes=[]
for s in g.ouurgkpbbjj:
 cells=[(dx,dy) for dy,row in enumerate(s.pixels) for dx,v in enumerate(row) if int(v)>=0]
 shapes.append(cells);print("SHAPE",(s.x,s.y),s.pixels.tolist(),cells)
print("TARGETS",len(T),sorted(T))
def mk(cells,x,y,axis):
 pts=set()
 for dx,dy in cells:
  px,py=x+dx,y+dy
  if 0<=px<W and 0<=py<H:pts.add((px,py))
  ry=2*axis-py
  if 0<=px<W and 0<=ry<H:pts.add((px,ry))
 return frozenset(pts&T)
opts=[]
for cells in shapes:
 by={}
 for axis in range(-10,H+11):
  u={}
  for x in range(-6,W+6):
   for y in range(-6,H+6):
    m=mk(cells,x,y,axis)
    if m:u.setdefault(m,(x,y))
  by[axis]=u
 opts.append(by)
for axis in range(-10,H+11):
 A=opts[0][axis];B=opts[1][axis];best=(0,None,None,set())
 for ma,pa in A.items():
  for mb,pb in B.items():
   u=set(ma)|set(mb);n=len(u)
   if n>best[0]:best=(n,pa,pb,u)
   if n==len(T):
    print("SOLVE_GEOM",axis,pa,pb);raise SystemExit
 if best[0]>=18:print("BEST",axis,best[0],best[1],best[2],"MISS",sorted(T-best[3]))
print("NO_SOLVE")
