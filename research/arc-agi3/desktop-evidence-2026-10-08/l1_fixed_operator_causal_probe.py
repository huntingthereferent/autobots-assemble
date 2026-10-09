from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy

def occ(g):
 b=g.naxbskjmlg()
 return {(x,y) for y in range(g.height) for x in range(g.dqwpuqcubca) if int(b[y,x])>=0}
def comps(S):
 S=set(S);out=[]
 while S:
  q=[S.pop()];c=set(q)
  while q:
   x,y=q.pop()
   for n in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
    if n in S:S.remove(n);c.add(n);q.append(n)
  out.append(c)
 return out
def centers(g):
 return sorted((sum(x for x,y in c)/len(c),sum(y for x,y in c)/len(c),len(c)) for c in comps(occ(g)))

a=Arcade(operation_mode=OperationMode.NORMAL);root=a.make('ar25')
print("BASE_POS",[(s.x,s.y) for s in root._game.ayyvxqrhnzw],"CENTERS",centers(root._game))
for act in [3,4]:
 e=copy.deepcopy(root)
 p0=(e._game.ayyvxqrhnzw[0].x,e._game.ayyvxqrhnzw[0].y)
 e.step(GameAction.from_id(act),data={})
 p1=(e._game.ayyvxqrhnzw[0].x,e._game.ayyvxqrhnzw[0].y)
 print("ACT",act,"DIRECT",(p1[0]-p0[0],p1[1]-p0[1]),"CENTERS",centers(e._game))
