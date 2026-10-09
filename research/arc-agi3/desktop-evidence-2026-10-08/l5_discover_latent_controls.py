from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy

# Proven prefix only to reach Level 5; role discovery below ignores tags.
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

def select(e,idx):
 g=e._game;cur=-1 if g.yvifanjrcyu not in g.ayyvxqrhnzw else g.ayyvxqrhnzw.index(g.yvifanjrcyu)
 for _ in range((idx-cur)%len(g.ayyvxqrhnzw)):e.step(GameAction.from_id(5),data={})

a=Arcade(operation_mode=OperationMode.NORMAL);root=a.make('ar25');r=None
for z in PRE5:r=root.step(GameAction.from_id(z),data={})
g=root._game
print("LEVEL",g.level_index+1,"OBJECTS",[(i,s.x,s.y,s.pixels.shape) for i,s in enumerate(g.ayyvxqrhnzw)])

roles=[]
for idx in range(len(g.ayyvxqrhnzw)):
 e=copy.deepcopy(root);select(e,idx)
 p0=[(s.x,s.y) for s in e._game.ayyvxqrhnzw]
 response={}
 for act in [1,2,3,4]:
  ee=copy.deepcopy(e);ee.step(GameAction.from_id(act),data={})
  p1=[(s.x,s.y) for s in ee._game.ayyvxqrhnzw]
  response[act]=(p1[idx][0]-p0[idx][0],p1[idx][1]-p0[idx][1])
 dims=set()
 for dx,dy in response.values():
  if dx:dims.add("x")
  if dy:dims.add("y")
 role="latent_1d" if len(dims)==1 else "source_2d" if len(dims)==2 else "fixed"
 roles.append((idx,role,dims,response))
 print("ROLE",idx,role,sorted(dims),response)

# Sweep the inferred 1-D controls over reachable coordinates by replaying moves
# from root, and find configurations with maximum visible support/component count.
one_d=[x for x in roles if x[1]=="latent_1d"]
assert len(one_d)==2,one_d
# identify direction axis from intervention response
xidx=next(idx for idx,role,dims,rsp in one_d if "x" in dims)
yidx=next(idx for idx,role,dims,rsp in one_d if "y" in dims)

def move_to(e,idx,target,axis):
 select(e,idx)
 while True:
  s=e._game.ayyvxqrhnzw[idx];cur=s.x if axis=="x" else s.y
  if cur==target:return True
  act=(4 if target>cur else 3) if axis=="x" else (2 if target>cur else 1)
  before=cur;e.step(GameAction.from_id(act),data={})
  s=e._game.ayyvxqrhnzw[idx];after=s.x if axis=="x" else s.y
  if after==before:return False

best=[]
for xv in range(-2,23):
 for yv in range(-2,23):
  e=copy.deepcopy(root)
  if not move_to(e,xidx,xv,"x"):continue
  if not move_to(e,yidx,yv,"y"):continue
  O=occ(e._game);C=comps(O)
  best.append((len(O),len(C),xv,yv,sorted(len(c) for c in C)))
best.sort(reverse=True)
print("TOP_VISIBILITY")
for row in best[:12]:print(" ",row)
