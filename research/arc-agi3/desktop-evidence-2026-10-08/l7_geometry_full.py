from arc_agi import Arcade,OperationMode
from arcengine import GameAction
a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
L3A=[5,5,4,5,7,2,5,2,2,2,2,3,5]+[1]*8+[3]*4+[5]+[1]*8
L3B=[5]+[4]*8+[2]*3+[5]+[3]*8+[2]*13
L4=[2]*6+[5]+[4]*7+[5]+[4]*7
L5=[2]*4+[5]+[4]*5+[5]+[3]*10+[1]*7
L6=[2]*11+[5,3,5]+[3]*15+[2]*4+[5]+[3]*7+[2]*12
e=a.make('ar25');r=None
for z in SOL+L3A+L3B+L4+L5+L6:r=e.step(GameAction.from_id(z),data={})
g=e._game;T=sorted({(t.x,t.y) for t in g.fswikrcrdmx});TI={p:i for i,p in enumerate(T)};FULL=(1<<len(T))-1;W,H=g.dqwpuqcubca,g.height
shapes=[]
for s in g.ouurgkpbbjj:
 shapes.append([(dx,dy) for dy,row in enumerate(s.pixels) for dx,v in enumerate(row) if int(v)>=0])
def bits(c,x,y,ax,ay):
 m=0
 for dx,dy in c:
  px,py=x+dx,y+dy
  for xx in {px,2*ax-px}:
   for yy in {py,2*ay-py}:
    i=TI.get((xx,yy))
    if i is not None:m|=1<<i
 return m
best=(0,None)
for ax in range(-2,W+3):
 for ay in range(-2,H+3):
  O=[]
  for c in shapes:
   u={}
   for x in range(-8,W+8):
    for y in range(-8,H+8):
     m=bits(c,x,y,ax,ay)
     if m:u.setdefault(m,(x,y))
   O.append(u)
  A,B=O
  # highest individual masks first
  aa=sorted(A.items(),key=lambda kv:kv[0].bit_count(),reverse=True)
  bb=sorted(B.items(),key=lambda kv:kv[0].bit_count(),reverse=True)
  maxb=bb[0][0].bit_count() if bb else 0
  for ma,pa in aa:
   if ma.bit_count()+maxb<best[0]:break
   need=FULL & ~ma
   for mb,pb in bb:
    n=(ma|mb).bit_count()
    if n>best[0]:
     best=(n,(ax,ay,pa,pb,ma|mb))
     if n>=35:print("BEST",n,"AX",ax,ay,"P",pa,pb,flush=True)
    if (mb & need)==need:
     print("SOLVE_GEOM",ax,ay,pa,pb,"N",len(T),flush=True);raise SystemExit
print("NO_SOLVE","BEST",best[0],best[1][:4] if best[1] else None)
if best[1]:
 m=best[1][4];print("MISS",[T[i] for i in range(len(T)) if not (m>>i)&1])
