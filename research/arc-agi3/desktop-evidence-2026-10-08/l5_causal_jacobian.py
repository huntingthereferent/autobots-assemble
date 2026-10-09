from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy

PRE5=[3,3,3,3,3,2,2,2,2,2,2,2,2,2,2,3,3,5,2,2,2,2,2,2,2,2,1,1,1,1,1,1,1,5,4,4,4,4,4,4,4,2,2,2,2,2,2,2,5,3,3,3,3,3,3,3,3,3,3,3,3,2,2,2,2,2,2,2,2,2,2,2,5,4,4,4,4,4,4,4,5,4,4,4,4,4,4,4]

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

def centroid(c):
 return (sum(x for x,y in c)/len(c),sum(y for x,y in c)/len(c))

def cs(g):
 return sorted([centroid(c) for c in comps(occ(g))])

def select(e,idx):
 g=e._game;cur=-1 if g.yvifanjrcyu not in g.ayyvxqrhnzw else g.ayyvxqrhnzw.index(g.yvifanjrcyu)
 for _ in range((idx-cur)%len(g.ayyvxqrhnzw)):e.step(GameAction.from_id(5),data={})

def move_to(e,idx,target,axis):
 select(e,idx)
 while True:
  s=e._game.ayyvxqrhnzw[idx];cur=s.x if axis=="x" else s.y
  if cur==target:return
  act=(4 if target>cur else 3) if axis=="x" else (2 if target>cur else 1)
  e.step(GameAction.from_id(act),data={})

a=Arcade(operation_mode=OperationMode.NORMAL);root=a.make('ar25')
for z in PRE5:root.step(GameAction.from_id(z),data={})
# Roles were discovered from action-response dimensions: y-control=0, x-control=1, source=2.
move_to(root,1,11,"x")
move_to(root,0,8,"y")
print("IDENT_STATE",[(i,s.x,s.y) for i,s in enumerate(root._game.ayyvxqrhnzw)])
print("BASE",cs(root._game))

for idx,acts in [(1,[3,4]),(0,[1,2]),(2,[3,4,1,2])]:
 e=copy.deepcopy(root);select(e,idx)
 print("\nOBJECT",idx)
 for act in acts:
  ee=copy.deepcopy(e)
  p0=[(s.x,s.y) for s in ee._game.ayyvxqrhnzw]
  before=cs(ee._game)
  ee.step(GameAction.from_id(act),data={})
  p1=[(s.x,s.y) for s in ee._game.ayyvxqrhnzw]
  after=cs(ee._game)
  print(" ACT",act,"DIRECT",(p1[idx][0]-p0[idx][0],p1[idx][1]-p0[idx][1]))
  print("  BEFORE",before)
  print("  AFTER ",after)
