from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
from collections import Counter
a=Arcade(operation_mode=OperationMode.NORMAL)

def dec(r):
 if not r.frame:return None
 F=np.array(r.frame[0],int)
 G=np.array([[F[2+3*y,2+3*x] for x in range(20)] for y in range(20)],int)
 bg=Counter(G.flatten().tolist()).most_common(1)[0][0]
 S={(x,y) for y in range(20) for x in range(20) if int(G[y,x])!=bg};out=[]
 while S:
  p=S.pop();q=[p];c={p}
  while q:
   x,y=q.pop()
   for n in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
    if n in S:S.remove(n);c.add(n);q.append(n)
  vals={int(G[y,x]) for x,y in c};marks={(x,y) for x,y in c if int(G[y,x])==8}
  if marks:
   out.append((vals,(min(x for x,y in c),min(y for x,y in c),max(x for x,y in c),max(y for x,y in c)),marks))
 return G,out
def sb(r):
 z=dec(r)
 if z is None:return None
 _,o=z;s=[x for x in o if 0 in x[0]]
 return s[0][1] if len(s)==1 else ("SEL?",len(s),[(x[0],x[1]) for x in o])
def click(e,x,y):
 r=e.step(GameAction.from_id(6),data={"x":2+3*x,"y":2+3*y});print(" CLICK",x,y,"->",sb(r),"LC",r.levels_completed);return r
def act(e,z):
 r=e.step(GameAction.from_id(z),data={});return r
def moves(e,z,n,label):
 r=None
 for i in range(n):
  r=act(e,z)
  if i==n-1 or r.levels_completed>1:print(" ",label,i+1,"->",sb(r),"LC",r.levels_completed)
  if r.levels_completed>1:return r
 return r

e=a.make("cn04")
click(e,13,9);r=act(e,5);r=moves(e,3,10,"L1left");r=act(e,1)
print("AT L2",sb(r),"LC",r.levels_completed)
# p0
r=moves(e,2,6,"p0down")
# p1
click(e,15,4);r=moves(e,3,4,"p1left");r=moves(e,2,8,"p1down")
# p2 no move
click(e,7,11)
# p3
click(e,17,17)
for i in range(3):
 r=act(e,5);print(" p3rot",i+1,"->",sb(r),"LC",r.levels_completed)
r=moves(e,3,4,"p3left");r=moves(e,1,2,"p3up")
print("FINAL",r.levels_completed,r.state.name,sb(r))
