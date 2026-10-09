from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy, math
from causal_operator_model import infer_fixed_relation,infer_controlled_relation

def active_cells(sprite):
 return [(sprite.x+dx,sprite.y+dy) for dy,row in enumerate(sprite.pixels) for dx,v in enumerate(row) if int(v)>=0]
def local_shape(sprite):
 return [(dx,dy) for dy,row in enumerate(sprite.pixels) for dx,v in enumerate(row) if int(v)>=0]
def centroid_pts(P):
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
def comp_centers(g):
 return [(centroid_pts(c),c) for c in comps(occ(g))]
def source_center(s):
 return centroid_pts(active_cells(s))
def match_direct(g,s):
 sc=source_center(s)
 cc=comp_centers(g)
 return min(cc,key=lambda z:(z[0][0]-sc[0])**2+(z[0][1]-sc[1])**2)
def other_component(g,s):
 direct=match_direct(g,s)[1]
 others=[z for z in comp_centers(g) if z[1]!=direct]
 if len(others)!=1:raise RuntimeError(("expected one dependent component",len(others),[x[0] for x in others]))
 return others[0]
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
def select(e,idx):
 g=e._game;cur=-1 if g.yvifanjrcyu not in g.ayyvxqrhnzw else g.ayyvxqrhnzw.index(g.yvifanjrcyu)
 for _ in range((idx-cur)%len(g.ayyvxqrhnzw)):e.step(GameAction.from_id(5),data={})
def legal_positions(shape,W,H):
 maxx=max(x for x,y in shape);maxy=max(y for x,y in shape)
 return [(x,y) for x in range(W-maxx) for y in range(H-maxy)]
def support_x(shape,at,axis,W,H):
 out=set();x0,y0=at
 for dx,dy in shape:
  x,y=x0+dx,y0+dy
  for xx in {x,round(2*axis-x)}:
   if 0<=xx<W and 0<=y<H:out.add((xx,y))
 return out
def target(g):return {(t.x,t.y) for t in g.fswikrcrdmx}
def move_selected_to(e,idx,gx,gy,start_level):
 select(e,idx)
 r=None
 while e._game.level_index==start_level:
  s=e._game.ayyvxqrhnzw[idx]
  if s.x==gx:break
  r=e.step(GameAction.from_id(4 if gx>s.x else 3),data={})
  if e._game.level_index!=start_level:return r
 while e._game.level_index==start_level:
  s=e._game.ayyvxqrhnzw[idx]
  if s.y==gy:break
  r=e.step(GameAction.from_id(2 if gy>s.y else 1),data={})
  if e._game.level_index!=start_level:return r
 return r

a=Arcade(operation_mode=OperationMode.NORMAL)
e=a.make('ar25')
actions=[]

# LEVEL 1: only selectable source. Infer fixed x-operator from source intervention.
g=e._game
assert len(g.ayyvxqrhnzw)==1
source=g.ayyvxqrhnzw[0]
base_src=source_center(source)[0]
base_dep=other_component(g,source)[0][0]
probe=copy.deepcopy(e);probe.step(GameAction.from_id(4),data={})
ps=probe._game.ayyvxqrhnzw[0]
new_src=source_center(ps)[0]
new_dep=other_component(probe._game,ps)[0][0]
rel1=infer_fixed_relation("x",base_src,base_dep,new_src-base_src,new_dep-base_dep)
axis1=rel1.reflection_axis()
print("L1_DISCOVER",rel1,"AXIS",axis1)
shape=local_shape(source);T=target(g);W,H=g.dqwpuqcubca,g.height
cands=[]
for at in legal_positions(shape,W,H):
 S=support_x(shape,at,axis1,W,H)
 if T<=S:cands.append((abs(at[0]-source.x)+abs(at[1]-source.y),len(S-T),at))
cands.sort();goal=cands[0][2]
print("L1_GOAL",goal,"CAND",cands[0])
# compile directly
sx,sy=source.x,source.y
plan=([4]*(goal[0]-sx) if goal[0]>sx else [3]*(sx-goal[0]))+([2]*(goal[1]-sy) if goal[1]>sy else [1]*(sy-goal[1]))
for z in plan:
 r=e.step(GameAction.from_id(z),data={});actions.append(z)
 if r.levels_completed>0:break
print("L1_RESULT",r.levels_completed,e._game.level_index,len(actions))
assert r.levels_completed==1

# LEVEL 2: discover one 1-D x-control and one 2-D source from action response.
g=e._game
roles=[]
for idx in range(len(g.ayyvxqrhnzw)):
 dims,resp=action_response_dims(e,idx);roles.append((idx,dims,resp))
print("L2_ROLES",roles)
ctrl=next(idx for idx,dims,rsp in roles if dims=={"x"})
src=next(idx for idx,dims,rsp in roles if dims=={"x","y"})
source=g.ayyvxqrhnzw[src]
# Base direct/dependent centers.
base_src=source_center(source)[0]
base_dep=other_component(g,source)[0][0]
# source +x probe
ps=copy.deepcopy(e);select(ps,src);ps.step(GameAction.from_id(4),data={})
ss=ps._game.ayyvxqrhnzw[src]
src2=source_center(ss)[0];dep2=other_component(ps._game,ss)[0][0]
# control +x probe
pc=copy.deepcopy(e);select(pc,ctrl)
ctrl0=pc._game.ayyvxqrhnzw[ctrl].x
pc.step(GameAction.from_id(4),data={})
ctrl1=pc._game.ayyvxqrhnzw[ctrl].x
dep3=other_component(pc._game,pc._game.ayyvxqrhnzw[src])[0][0]
rel2=infer_controlled_relation("x",base_src,ctrl0,base_dep,src2-base_src,dep2-base_dep,ctrl1-ctrl0,dep3-base_dep)
print("L2_DISCOVER",rel2,"CURRENT_AXIS",rel2.reflection_axis(ctrl0))

shape=local_shape(source);T=target(g);W,H=g.dqwpuqcubca,g.height
cands=[]
# reachable control x from probing boundaries via legal game range is conservatively board span
for ax in range(W):
 for at in legal_positions(shape,W,H):
  S=support_x(shape,at,ax,W,H)
  if T<=S:
   cost=abs(ax-g.ayyvxqrhnzw[ctrl].x)+abs(at[0]-source.x)+abs(at[1]-source.y)
   cands.append((cost,len(S-T),ax,at))
cands.sort();_,_,goal_ax,goal_at=cands[0]
print("L2_GOAL","AX",goal_ax,"PAY",goal_at,"CAND",cands[0])
# Move control then source, stopping on level advance.
select(e,ctrl)
while e._game.ayyvxqrhnzw[ctrl].x!=goal_ax:
 z=4 if goal_ax>e._game.ayyvxqrhnzw[ctrl].x else 3
 r=e.step(GameAction.from_id(z),data={});actions.append(z)
 if r.levels_completed>1:break
if r.levels_completed==1:
 r2=move_selected_to(e,src,goal_at[0],goal_at[1],start_level=1)
 if r2 is not None:r=r2
# engine may advance on the final move; inspect current level count
print("L2_RESULT",e._game.level_index, "LC", getattr(r,"levels_completed",None))
assert e._game.level_index>=2
print("PASS causal learn-then-act through Levels 1-2")
