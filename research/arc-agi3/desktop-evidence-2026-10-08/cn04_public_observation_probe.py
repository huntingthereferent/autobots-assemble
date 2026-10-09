from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np, copy

a=Arcade(operation_mode=OperationMode.NORMAL)
e=a.make("cn04")

def frame(e,action=7,data=None):
 r=e.step(GameAction.from_id(action),data=data or {})
 return np.array(r.frame[0],dtype=int),r

F,r=frame(e)
print("FRAME_SH",F.shape,"UNIQ",sorted(np.unique(F).tolist()))
# Public-observation connected components, excluding background color 10.
S={(x,y) for y in range(F.shape[0]) for x in range(F.shape[1]) if int(F[y,x])!=10}
comps=[]
while S:
 p=S.pop();q=[p];c={p}
 while q:
  x,y=q.pop()
  for n in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
   if n in S:S.remove(n);c.add(n);q.append(n)
 comps.append(c)
print("COMPONENTS",len(comps))
for i,c in enumerate(sorted(comps,key=lambda c:-len(c))[:20]):
 xs=[p[0] for p in c];ys=[p[1] for p in c]
 vals=sorted({int(F[y,x]) for x,y in c})
 print(i,"N",len(c),"BOX",(min(xs),min(ys),max(xs),max(ys)),"VALS",vals)

# Fresh one-step public interventions; summarize changed pixels.
base=a.make("cn04");Fb,_=frame(base)
for z,data in [(1,{}),(2,{}),(3,{}),(4,{}),(5,{})]:
 ee=a.make("cn04")
 F0,_=frame(ee)
 F1,r1=frame(ee,z,data)
 D=np.argwhere(F0!=F1)
 if len(D):
  ys=D[:,0];xs=D[:,1]
  box=(int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max()))
 else:box=None
 print("A",z,"DIFF",len(D),"BOX",box,"COLORS_BEFORE",sorted(np.unique(F0[D[:,0],D[:,1]]).tolist()) if len(D) else [],"AFTER",sorted(np.unique(F1[D[:,0],D[:,1]]).tolist()) if len(D) else [])
