from arc_agi import Arcade,OperationMode
from arcengine import GameAction
a=Arcade(operation_mode=OperationMode.NORMAL)
PRE3=[3,3,3,3,3,2,2,2,2,2,2,2,2,2,2,7,5,2,2,2,2,2,5,3,5,2,2,2,5,3,5,5,4,5,7,2,5,2,2,2,2,3,5,1,1,1,1,1,1,1,1,3,3,3,3,5,1,1,1,1,1,1,1,1,5,4,4,4,4,4,4,4,4,2,2,2,5,3,3,3,3,3,3,3,3,2,2,2,2,2,2,2,2,2,2,2,2,2]
L4=[2]*6+[5]+[4]*7+[5]+[4]*7
L5=[2]*4+[5]+[4]*5+[5]+[3]*10+[1]*7
e=a.make('ar25');r=None
for z in PRE3+L4+L5:r=e.step(GameAction.from_id(z),data={})
g=e._game;T={(t.x,t.y) for t in g.fswikrcrdmx};W,H=g.dqwpuqcubca,g.height
print("LEVEL",g.level_index,"LC",r.levels_completed,"CARRIERS",[(s.x,s.y,sorted(s.tags)) for s in g.jtkyjqznbnp])
# exact symmetry axes (integer reflection coordinate)
xaxes=[a for a in range(-5,W+6) if {(2*a-x,y) for x,y in T}==T]
yaxes=[a for a in range(-5,H+6) if {(x,2*a-y) for x,y in T}==T]
print("SYMMETRY_AXES",xaxes,yaxes)
shapes=[]
for s in g.ouurgkpbbjj:
 c=[(dx,dy) for dy,row in enumerate(s.pixels) for dx,v in enumerate(row) if int(v)>=0]
 shapes.append(c);print("SHAPE",(s.x,s.y),s.pixels.tolist(),c)
def mask(c,x,y,ax,ay):
 out=set()
 for dx,dy in c:
  px,py=x+dx,y+dy
  for xx in {px,2*ax-px}:
   for yy in {py,2*ay-py}:
    if 0<=xx<W and 0<=yy<H:out.add((xx,yy))
 return frozenset(out&T)
for ax in xaxes:
 for ay in yaxes:
  opts=[]
  for c in shapes:
   u={}
   for x in range(-6,W+6):
    for y in range(-6,H+6):
     m=mask(c,x,y,ax,ay)
     if m:u.setdefault(m,(x,y))
   opts.append(u)
  print("OPTS",ax,ay,*[len(o) for o in opts])
  # two payloads in this level
  A,B=opts
  best=(0,None,None,set())
  for ma,pa in A.items():
   for mb,pb in B.items():
    uu=set(ma)|set(mb);n=len(uu)
    if n>best[0]:best=(n,pa,pb,uu)
    if n==len(T):
     print("SOLVE_GEOM",ax,ay,pa,pb);raise SystemExit
  print("BEST",best[0],best[1],best[2],"MISS",sorted(T-best[3]))
print("NO_SOLVE")
