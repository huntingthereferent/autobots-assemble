from arc_agi import Arcade,OperationMode
from arcengine import GameAction
a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
L3A=[5,5,4,5,7,2,5,2,2,2,2,3,5]+[1]*8+[3]*4+[5]+[1]*8
L3B=[5]+[4]*8+[2]*3+[5]+[3]*8+[2]*13
L4=[2]*6+[5]+[4]*7+[5]+[4]*7
L5=[2]*4+[5]+[4]*5+[5]+[3]*10+[1]*7
L6=[2]*11+[5,3,5]+[3]*15+[2]*4+[5]+[3]*7+[2]*12
base=SOL+L3A+L3B+L4+L5+L6
e=a.make('ar25');r=None
for z in base:r=e.step(GameAction.from_id(z),data={})
g=e._game;T={(t.x,t.y) for t in g.fswikrcrdmx};W,H=g.dqwpuqcubca,g.height
xaxes=[q for q in range(-5,W+6) if {(2*q-x,y) for x,y in T}==T]
yaxes=[q for q in range(-5,H+6) if {(x,2*q-y) for x,y in T}==T]
print("LEVEL",g.level_index,"LC",r.levels_completed,"CARR",[(s.x,s.y,sorted(s.tags)) for s in g.jtkyjqznbnp],"AX",xaxes,yaxes)
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
   for x in range(-8,W+8):
    for y in range(-8,H+8):
     m=mask(c,x,y,ax,ay)
     if m:u.setdefault(m,(x,y))
   opts.append(u)
  A,B=opts;best=(0,None,None,set())
  for ma,pa in A.items():
   for mb,pb in B.items():
    uu=set(ma)|set(mb);n=len(uu)
    if n>best[0]:best=(n,pa,pb,uu)
    if n==len(T):
     print("SOLVE_GEOM",ax,ay,pa,pb,"N",n);raise SystemExit
  print("BEST",ax,ay,best[0],best[1],best[2],"MISS",sorted(T-best[3]))
print("NO_SOLVE")
