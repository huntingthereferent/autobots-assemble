from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np

a=Arcade(operation_mode=OperationMode.NORMAL)

def grid(e):
 r=e.step(GameAction.from_id(7),data={})
 F=np.array(r.frame[0],int)
 G=np.array([[F[2+3*y,2+3*x] for x in range(20)] for y in range(20)],int)
 return G,r

def comps(G):
 S={(x,y) for y in range(20) for x in range(20) if int(G[y,x])!=10}
 out=[]
 while S:
  p=S.pop();q=[p];c={p}
  while q:
   x,y=q.pop()
   for n in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
    if n in S:S.remove(n);c.add(n);q.append(n)
  vals={int(G[y,x]) for x,y in c}
  if 4 not in vals:out.append(c)
 return out

def objects(G):
 out=[]
 for c in comps(G):
  vals={int(G[y,x]) for x,y in c}
  box=(min(x for x,y in c),min(y for x,y in c),max(x for x,y in c),max(y for x,y in c))
  marks={(x,y) for x,y in c if int(G[y,x])==8}
  kind="sel" if 0 in vals else "other"
  out.append((kind,box,marks))
 return out

def click(e,x,y):
 return e.step(GameAction.from_id(6),data={"x":2+3*x,"y":2+3*y})
def move(e,dx,dy):
 r=None
 for _ in range(abs(dx)):r=e.step(GameAction.from_id(4 if dx>0 else 3),data={})
 for _ in range(abs(dy)):r=e.step(GameAction.from_id(2 if dy>0 else 1),data={})
 return r

root=a.make("cn04");G,_=grid(root);os=objects(G)
A=next(o for o in os if o[0]=="sel");B=next(o for o in os if o[0]=="other")
Amarks=set(A[2])
print("A",sorted(Amarks))

# learn B state offsets from public observation
e=a.make("cn04");click(e,13,9)
states=[]
for k in range(4):
 G,_=grid(e);S=next(o for o in objects(G) if o[0]=="sel")
 x0,y0,x1,y1=S[1];offs={(x-x0,y-y0) for x,y in S[2]}
 states.append((k,(x0,y0),offs,(x1-x0+1,y1-y0+1)))
 print("STATE",k,"OFF",sorted(offs),"SIZE",states[-1][3])
 e.step(GameAction.from_id(5),data={})

align=[]
for k,(bx,by),offs,(w,h) in states:
 for ox,oy in offs:
  for ax,ay in Amarks:
   gx=ax-ox;gy=ay-oy
   if gx<0 or gy<0 or gx+w>20 or gy+h>20:continue
   P={(gx+x,gy+y) for x,y in offs}
   if P==Amarks:
    key=(k,gx,gy)
    if key not in align:align.append(key)
print("FULL_ALIGNMENTS",align)

for k,gx,gy in align:
 e=a.make("cn04");click(e,13,9)
 for _ in range(k):e.step(GameAction.from_id(5),data={})
 G,_=grid(e);S=next(o for o in objects(G) if o[0]=="sel")
 x0,y0,_,_=S[1]
 r=move(e,gx-x0,gy-y0)
 if r is None:G,r=grid(e)
 # if completion may trigger on final move, inspect returned result directly
 print("TEST",k,(gx,gy),"LC",r.levels_completed,"STATE",r.state.name,"LEVEL?",getattr(r,"level_index",None))
 if r.levels_completed==0:
  G2,_=grid(e)
  print(" N3",int((G2==3).sum()),"N8",int((G2==8).sum()))
