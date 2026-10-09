from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np, copy

a=Arcade(operation_mode=OperationMode.NORMAL)

def public_grid(e):
 r=e.step(GameAction.from_id(7),data={})
 F=np.array(r.frame[0],dtype=int)
 return np.array([[F[2+3*y,2+3*x] for x in range(20)] for y in range(20)],dtype=int),r

def components(G):
 S={(x,y) for y in range(20) for x in range(20) if int(G[y,x])!=10}
 out=[]
 while S:
  p=S.pop();q=[p];c={p}
  while q:
   x,y=q.pop()
   for n in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
    if n in S:S.remove(n);c.add(n);q.append(n)
  out.append(c)
 return [c for c in out if not any(int(G[y,x])==4 for x,y in c)]

def objs(G):
 out=[]
 for c in components(G):
  vals={int(G[y,x]) for x,y in c}
  if not (vals&{0,14,8,3}):continue
  box=(min(x for x,y in c),min(y for x,y in c),max(x for x,y in c),max(y for x,y in c))
  marks={(x,y) for x,y in c if int(G[y,x])==8}
  matched={(x,y) for x,y in c if int(G[y,x])==3}
  kind="selected" if 0 in vals else "other"
  out.append((kind,box,marks,matched,vals))
 return out

def click_grid(e,x,y):
 return e.step(GameAction.from_id(6),data={"x":2+3*x,"y":2+3*y})

def move(e,dx,dy):
 for _ in range(abs(dx)):e.step(GameAction.from_id(4 if dx>0 else 3),data={})
 for _ in range(abs(dy)):e.step(GameAction.from_id(2 if dy>0 else 1),data={})

# Discover B orientations publicly.
root=a.make("cn04")
G,_=public_grid(root)
O=objs(G)
A=next(o for o in O if o[0]=="selected");B=next(o for o in O if o[0]=="other")
Amarks=sorted(A[2]);Bbox=B[1]
print("A_MARKS",Amarks,"B0",Bbox,sorted(B[2]))

# select B by a known occupied public grid cell from its component
e=copy.deepcopy(root);click_grid(e,13,9)
states=[]
for k in range(4):
 G,_=public_grid(e);os=objs(G);S=next(o for o in os if o[0]=="selected")
 x0,y0,x1,y1=S[1]
 offsets=sorted((x-x0,y-y0) for x,y in S[2])
 states.append((k,(x0,y0,x1,y1),offsets))
 print("STATE",k,"BOX",S[1],"OFFSETS",offsets)
 e.step(GameAction.from_id(5),data={})

# For each orientation/marker pair, make exactly one marker coincide with one A marker.
trials=[]
for k,box,offs in states:
 w=box[2]-box[0]+1;h=box[3]-box[1]+1
 for bi,bo in enumerate(offs):
  for ai,am in enumerate(Amarks):
   gx=am[0]-bo[0];gy=am[1]-bo[1]
   if gx<0 or gy<0 or gx+w>20 or gy+h>20:continue
   placed={(gx+ox,gy+oy) for ox,oy in offs}
   if len(placed & set(Amarks))!=1:continue
   trials.append((k,bi,ai,(gx,gy),placed))

print("TRIALS",trials)
for k,bi,ai,(gx,gy),placed in trials:
 e=a.make("cn04")
 click_grid(e,13,9)
 for _ in range(k):e.step(GameAction.from_id(5),data={})
 G,_=public_grid(e);S=next(o for o in objs(G) if o[0]=="selected")
 x0,y0,_,_=S[1]
 move(e,gx-x0,gy-y0)
 G,r=public_grid(e)
 n3=int((G==3).sum())
 n8=int((G==8).sum())
 print("RESULT","k",k,"b",bi,"a",ai,"goal",(gx,gy),"placed",sorted(placed),"N3",n3,"N8",n8,"LC",r.levels_completed,"STATE",r.state.name)
 # local print around overlap
 ax,ay=Amarks[ai]
 print(" CELL",ax,ay,"VALUE",int(G[ay,ax]))
