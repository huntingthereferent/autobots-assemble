from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy

# Reach Level 3 using the causally discovered L1/L2 plans, not the old witness.
L1=[3]*5+[2]*10
L2=[3,3,5]+[2]*8  # axis x12->10, select payload, down 8

def action_response_dims(root,idx):
 e=copy.deepcopy(root)
 g=e._game;cur=-1 if g.yvifanjrcyu not in g.ayyvxqrhnzw else g.ayyvxqrhnzw.index(g.yvifanjrcyu)
 for _ in range((idx-cur)%len(g.ayyvxqrhnzw)):e.step(GameAction.from_id(5),data={})
 p0=(e._game.ayyvxqrhnzw[idx].x,e._game.ayyvxqrhnzw[idx].y)
 resp={}
 for z in [1,2,3,4]:
  ee=copy.deepcopy(e);ee.step(GameAction.from_id(z),data={})
  p1=(ee._game.ayyvxqrhnzw[idx].x,ee._game.ayyvxqrhnzw[idx].y)
  resp[z]=(p1[0]-p0[0],p1[1]-p0[1])
 dims=set()
 for dx,dy in resp.values():
  if dx:dims.add("x")
  if dy:dims.add("y")
 return dims,resp

def local_shape(s):
 return [(dx,dy) for dy,row in enumerate(s.pixels) for dx,v in enumerate(row) if int(v)>=0]
def legal_positions(shape,W,H):
 mx=max(x for x,y in shape);my=max(y for x,y in shape)
 return [(x,y) for x in range(W-mx) for y in range(H-my)]
def support(shape,at,axis,dim,W,H):
 out=set();x0,y0=at
 for dx,dy in shape:
  x,y=x0+dx,y0+dy
  pts={(x,y)}
  if dim=="x":pts.add((2*axis-x,y))
  else:pts.add((x,2*axis-y))
  out|={(xx,yy) for xx,yy in pts if 0<=xx<W and 0<=yy<H}
 return out
def target(g):return {(t.x,t.y) for t in g.fswikrcrdmx}
def select(e,idx):
 g=e._game;cur=-1 if g.yvifanjrcyu not in g.ayyvxqrhnzw else g.ayyvxqrhnzw.index(g.yvifanjrcyu)
 for _ in range((idx-cur)%len(g.ayyvxqrhnzw)):e.step(GameAction.from_id(5),data={})

a=Arcade(operation_mode=OperationMode.NORMAL);e=a.make('ar25');r=None
for z in L1+L2:r=e.step(GameAction.from_id(z),data={})
print("START","LC",r.levels_completed,"LEVEL",e._game.level_index,[(i,s.x,s.y) for i,s in enumerate(e._game.ayyvxqrhnzw)])
assert r.levels_completed==2

g=e._game;roles=[]
for idx in range(len(g.ayyvxqrhnzw)):
 dims,resp=action_response_dims(e,idx);roles.append((idx,dims,resp))
print("ROLES",roles)
control=next(idx for idx,dims,rsp in roles if len(dims)==1)
dim=next(iter(next(dims for idx,dims,rsp in roles if idx==control)))
sources=[idx for idx,dims,rsp in roles if len(dims)==2]
print("TRANSFER_OPERATOR_DIM",dim,"CONTROL",control,"SOURCES",sources)

T=target(g);W,H=g.dqwpuqcubca,g.height
# Learned family from earlier levels: one-axis orbit under q=2a-p.
axis_coord=g.ayyvxqrhnzw[control].x if dim=="x" else g.ayyvxqrhnzw[control].y
axis_range=range(W) if dim=="x" else range(H)
opts=[]
for srcidx in sources:
 s=g.ayyvxqrhnzw[srcidx];shape=local_shape(s)
 byaxis={}
 for ax in axis_range:
  masks={}
  for at in legal_positions(shape,W,H):
   S=support(shape,at,ax,dim,W,H)
   hit=frozenset(S&T)
   if hit:
    cost=abs(at[0]-s.x)+abs(at[1]-s.y)
    old=masks.get(hit)
    if old is None or cost<old[0]:masks[hit]=(cost,at)
  byaxis[ax]=masks
 opts.append(byaxis)

best=None
for ax in axis_range:
 A=opts[0][ax];B=opts[1][ax]
 for ma,(ca,pa) in A.items():
  need=T-set(ma)
  for mb,(cb,pb) in B.items():
   if need<=set(mb):
    cost=abs(ax-axis_coord)+ca+cb
    cand=(cost,ax,pa,pb)
    if best is None or cand<best:best=cand
print("INFERRED_GOAL",best)
assert best is not None
_,goal_axis,p0,p1=best

# Compile plan, stopping when level advances.
start_level=e._game.level_index
select(e,control)
while e._game.level_index==start_level:
 s=e._game.ayyvxqrhnzw[control];cur=s.x if dim=="x" else s.y
 if cur==goal_axis:break
 z=(4 if goal_axis>cur else 3) if dim=="x" else (2 if goal_axis>cur else 1)
 r=e.step(GameAction.from_id(z),data={})
for srcidx,goal in zip(sources,[p0,p1]):
 if e._game.level_index!=start_level:break
 select(e,srcidx)
 while e._game.level_index==start_level:
  s=e._game.ayyvxqrhnzw[srcidx]
  if s.x==goal[0]:break
  r=e.step(GameAction.from_id(4 if goal[0]>s.x else 3),data={})
 while e._game.level_index==start_level:
  s=e._game.ayyvxqrhnzw[srcidx]
  if s.y==goal[1]:break
  r=e.step(GameAction.from_id(2 if goal[1]>s.y else 1),data={})
print("RESULT","LC",r.levels_completed,"LEVEL",e._game.level_index)
assert r.levels_completed>=3
print("PASS learned operator transfer solves Level 3")
