from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np

def graph(M):
 h,w=M.shape
 nodes=[(r,c) for r in range(h) for c in range(w)]
 adj={}
 for r,c in nodes:
  adj[(r,c)]={(rr,cc) for rr,cc in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)) if 0<=rr<h and 0<=cc<w}
 val={(r,c):int(M[r,c]) for r,c in nodes}
 return nodes,adj,val

def isos(A,B,limit=8):
 NA,AA,VA=graph(A);NB,AB,VB=graph(B)
 cand={u:[v for v in NB if VA[u]==VB[v] and len(AA[u])==len(AB[v])] for u in NA}
 order=sorted(NA,key=lambda u:(len(cand[u]),-len(AA[u])))
 sol=[]
 def rec(i,m,used):
  if len(sol)>=limit:return
  if i==len(order):sol.append(dict(m));return
  u=order[i]
  for v in cand[u]:
   if v in used:continue
   if any(((u2 in AA[u])!=(v2 in AB[v])) for u2,v2 in m.items()):continue
   m[u]=v;used.add(v);rec(i+1,m,used);used.remove(v);del m[u]
 rec(0,{},set())
 out=[]
 for m in sol:
  pts=[(r,c,*m[(r,c)]) for r,c in NA]
  X=np.array([[r,c,1] for r,c,rr,cc in pts],float)
  yr=np.array([rr for r,c,rr,cc in pts],float);yc=np.array([cc for r,c,rr,cc in pts],float)
  br=np.linalg.lstsq(X,yr,rcond=None)[0];bc=np.linalg.lstsq(X,yc,rcond=None)[0]
  er=max(abs(X@br-yr));ec=max(abs(X@bc-yc))
  if er<1e-9 and ec<1e-9:
   lin=(round(br[0]),round(br[1]),round(bc[0]),round(bc[1]))
   con=(round(br[2]),round(bc[2]))
   out.append((lin,con,m))
 return out

a=Arcade(operation_mode=OperationMode.NORMAL);e=a.make("cn04")
states=[np.array(e._game.xseexqzst.render(),dtype=int)]
for _ in range(4):
 e.step(GameAction.from_id(5),data={})
 states.append(np.array(e._game.xseexqzst.render(),dtype=int))

for i in range(4):
 A,B=states[i],states[i+1]
 z=isos(A,B)
 print("STEP",i+1,"SHAPES",A.shape,B.shape,"N",len(z))
 for lin,con,m in z:print(" ",lin,con)

# Find linear part common to all four transitions.
sets=[{lin for lin,con,m in isos(states[i],states[i+1])} for i in range(4)]
common=set.intersection(*sets)
print("COMMON_LINEAR",common)
assert common
for lin in sorted(common):
 print("CONSISTENT",lin)
 for i in range(4):
  matches=[(con,m) for l,con,m in isos(states[i],states[i+1]) if l==lin]
  print(" STEP",i+1,"CONST",[x[0] for x in matches])
