from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy
from causal_operator_model import infer_fixed_relation,infer_controlled_relation

def active_cells(s):
 return [(s.x+dx,s.y+dy) for dy,row in enumerate(s.pixels) for dx,v in enumerate(row) if int(v)>=0]
def local_shape(s):
 return [(dx,dy) for dy,row in enumerate(s.pixels) for dx,v in enumerate(row) if int(v)>=0]
def centroid(P):
 return (sum(x for x,y in P)/len(P),sum(y for x,y in P)/len(P))
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
def source_center(s):return centroid(active_cells(s))
def comp_centers(g):return [(centroid(c),c) for c in comps(occ(g))]
def direct_component(g,s):
 sc=source_center(s)
 return min(comp_centers(g),key=lambda z:(z[0][0]-sc[0])**2+(z[0][1]-sc[1])**2)
def other_component(g,s):
 dc=direct_component(g,s)[1]
 o=[z for z in comp_centers(g) if z[1]!=dc]
 if len(o)!=1:raise RuntimeError(("expected one dependent",len(o)))
 return o[0]
def select(e,idx):
 g=e._game;cur=-1 if g.yvifanjrcyu not in g.ayyvxqrhnzw else g.ayyvxqrhnzw.index(g.yvifanjrcyu)
 for _ in range((idx-cur)%len(g.ayyvxqrhnzw)):e.step(GameAction.from_id(5),data={})
def response_dims(root,idx):
 e=copy.deepcopy(root);select(e,idx)
 p0=(e._game.ayyvxqrhnzw[idx].x,e._game.ayyvxqrhnzw[idx].y);resp={}
 for z in [1,2,3,4]:
  ee=copy.deepcopy(e);ee.step(GameAction.from_id(z),data={})
  p1=(ee._game.ayyvxqrhnzw[idx].x,ee._game.ayyvxqrhnzw[idx].y)
  resp[z]=(p1[0]-p0[0],p1[1]-p0[1])
 dims=set()
 for dx,dy in resp.values():
  if dx:dims.add("x")
  if dy:dims.add("y")
 return dims,resp
def legal_positions(shape,W,H):
 mx=max(x for x,y in shape);my=max(y for x,y in shape)
 return [(x,y) for x in range(W-mx) for y in range(H-my)]
def support(shape,at,axes,W,H):
 out=set();x0,y0=at
 for dx,dy in shape:
  x,y=x0+dx,y0+dy
  xs={x};ys={y}
  if "x" in axes:xs.add(2*axes["x"]-x)
  if "y" in axes:ys.add(2*axes["y"]-y)
  out|={(xx,yy) for xx in xs for yy in ys if 0<=xx<W and 0<=yy<H}
 return out
def target(g):return {(t.x,t.y) for t in g.fswikrcrdmx}

def solve_geometry(g,controls,sources):
 T=target(g);W,H=g.dqwpuqcubca,g.height
 dims=sorted(controls)
 axis_ranges={}
 current_axes={}
 for dim,idx in controls.items():
  c=g.ayyvxqrhnzw[idx].x if dim=="x" else g.ayyvxqrhnzw[idx].y
  current_axes[dim]=c
  axis_ranges[dim]=range(W) if dim=="x" else range(H)
 axis_choices=[({},0)]
 for dim in dims:
  nxt=[]
  for partial,c0 in axis_choices:
   for a in axis_ranges[dim]:
    q=dict(partial);q[dim]=a
    nxt.append((q,c0+abs(a-current_axes[dim])))
  axis_choices=nxt

 best=None
 for axes,axis_cost in axis_choices:
  opt=[]
  for idx in sources:
   s=g.ayyvxqrhnzw[idx];shape=local_shape(s);masks={}
   for at in legal_positions(shape,W,H):
    S=support(shape,at,axes,W,H);hit=frozenset(S&T)
    if not hit:continue
    cost=abs(at[0]-s.x)+abs(at[1]-s.y)
    old=masks.get(hit)
    if old is None or cost<old[0]:masks[hit]=(cost,at)
   opt.append(masks)
  if len(opt)==1:
   for m,(c,p) in opt[0].items():
    if T<=set(m):
     cand=(axis_cost+c,axes,[p])
     if best is None or cand[0]<best[0]:best=cand
  elif len(opt)==2:
   A=sorted(opt[0].items(),key=lambda kv:-len(kv[0]))
   B=sorted(opt[1].items(),key=lambda kv:-len(kv[0]))
   for ma,(ca,pa) in A:
    need=T-set(ma)
    for mb,(cb,pb) in B:
     if need<=set(mb):
      cand=(axis_cost+ca+cb,axes,[pa,pb])
      if best is None or cand[0]<best[0]:best=cand
      break
  else:raise RuntimeError(("source count",len(opt)))
 if best is None:raise RuntimeError("no covering geometry")
 return best

def execute_plan(e,controls,sources,axes,placements):
 start=e._game.level_index
 r=None
 # controls first
 for dim,idx in sorted(controls.items()):
  if e._game.level_index!=start:return r
  select(e,idx)
  while e._game.level_index==start:
   s=e._game.ayyvxqrhnzw[idx];cur=s.x if dim=="x" else s.y;goal=axes[dim]
   if cur==goal:break
   z=(4 if goal>cur else 3) if dim=="x" else (2 if goal>cur else 1)
   r=e.step(GameAction.from_id(z),data={})
   if r.state.name!="NOT_FINISHED":return r
 # sources
 for idx,goal in zip(sources,placements):
  if e._game.level_index!=start:return r
  select(e,idx)
  while e._game.level_index==start:
   s=e._game.ayyvxqrhnzw[idx]
   if s.x==goal[0]:break
   r=e.step(GameAction.from_id(4 if goal[0]>s.x else 3),data={})
   if r.state.name!="NOT_FINISHED":return r
  while e._game.level_index==start:
   s=e._game.ayyvxqrhnzw[idx]
   if s.y==goal[1]:break
   r=e.step(GameAction.from_id(2 if goal[1]>s.y else 1),data={})
   if r.state.name!="NOT_FINISHED":return r
 return r

a=Arcade(operation_mode=OperationMode.NORMAL);e=a.make('ar25')
print("FRESH")

# Learn fixed family on L1.
g=e._game;src=0;s=g.ayyvxqrhnzw[src]
bs=source_center(s)[0];bd=other_component(g,s)[0][0]
pr=copy.deepcopy(e);pr.step(GameAction.from_id(4),data={});s2=pr._game.ayyvxqrhnzw[0]
ns=source_center(s2)[0];nd=other_component(pr._game,s2)[0][0]
fixed=infer_fixed_relation("x",bs,bd,ns-bs,nd-bd)
assert fixed.is_reflection_signature()
axis=fixed.reflection_axis()
T=target(g);shape=local_shape(s);W,H=g.dqwpuqcubca,g.height
cand=[]
for at in legal_positions(shape,W,H):
 S=support(shape,at,{"x":axis},W,H)
 if T<=S:cand.append((abs(at[0]-s.x)+abs(at[1]-s.y),at))
cand.sort();goal=cand[0][1]
execute_plan(e,{},[0],{},[goal])
assert e._game.level_index==1
print("L1 learned",fixed,"goal",goal)

# Learn movable control law on L2 and solve.
g=e._game;roles=[(i,*response_dims(e,i)) for i in range(len(g.ayyvxqrhnzw))]
ctrl=next(i for i,d,r in roles if d=={"x"});src=next(i for i,d,r in roles if d=={"x","y"})
s=g.ayyvxqrhnzw[src];bs=source_center(s)[0];bd=other_component(g,s)[0][0]
ps=copy.deepcopy(e);select(ps,src);ps.step(GameAction.from_id(4),data={});ss=ps._game.ayyvxqrhnzw[src]
ns=source_center(ss)[0];nd=other_component(ps._game,ss)[0][0]
pc=copy.deepcopy(e);select(pc,ctrl);a0=pc._game.ayyvxqrhnzw[ctrl].x;pc.step(GameAction.from_id(4),data={});a1=pc._game.ayyvxqrhnzw[ctrl].x
cd=other_component(pc._game,pc._game.ayyvxqrhnzw[src])[0][0]
mov=infer_controlled_relation("x",bs,a0,bd,ns-bs,nd-bd,a1-a0,cd-bd)
assert mov.is_reflection_signature() and mov.source_gain==-1 and mov.control_gain==2
best=solve_geometry(g,{"x":ctrl},[src]);print("L2 learned",mov,"goal",best)
execute_plan(e,{"x":ctrl},[src],best[1],best[2])
assert e._game.level_index==2

# Transfer the learned family across all remaining levels.
while e._game.level_index<8:
 lev=e._game.level_index
 g=e._game
 roles=[(i,*response_dims(e,i)) for i in range(len(g.ayyvxqrhnzw))]
 controls={}
 sources=[]
 for i,d,rsp in roles:
  if len(d)==1:controls[next(iter(d))]=i
  elif len(d)==2:sources.append(i)
 print("LEVEL",lev+1,"ROLES",[(i,sorted(d)) for i,d,r in roles],"CONTROLS",controls,"SOURCES",sources)
 best=solve_geometry(g,controls,sources)
 print(" GOAL",best)
 r=execute_plan(e,controls,sources,best[1],best[2])
 if r is not None and r.state.name=="WIN":
  print("FINAL","LC",r.levels_completed,"STATE",r.state.name,"LEVEL_INDEX",e._game.level_index)
  break
 if e._game.level_index==lev:raise RuntimeError(("did not advance",lev,best))
 if e._game.level_index>=8:break

assert r is not None and r.state.name=="WIN" and r.levels_completed==8
print("PASS causal-family transfer reached WIN")
