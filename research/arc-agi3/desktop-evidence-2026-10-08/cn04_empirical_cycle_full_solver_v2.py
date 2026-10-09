from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np, copy
from collections import defaultdict

a=Arcade(operation_mode=OperationMode.NORMAL)

def invmap(cam):
 out={}
 for y in range(64):
  for x in range(64):
   g=cam.display_to_grid(x,y)
   if g is not None and g not in out:out[g]=(x,y)
 return out
def vis(g): return [s for s in g.current_level.get_sprites() if s.is_visible]
def semantic_local(game,s):
 save=s.pixels.copy();s.pixels=game.hlxyvcmpk[s.name]
 A=np.array(s.render(),int);s.pixels=save
 return frozenset((c,r,int(A[r,c])) for r in range(A.shape[0]) for c in range(A.shape[1]) if int(A[r,c]) in (8,13))
def group_names(g,s):
 try:return frozenset(x.name for x in g.vausolnec[s])
 except:return frozenset([s.name])
def find_group(g,names): return next((s for s in vis(g) if s.name in names),None)
def select_group(e,names):
 s=find_group(e._game,names)
 if e._game.xseexqzst is s:return
 A=np.array(s.render(),int);inv=invmap(e._game.camera)
 for rr in range(A.shape[0]):
  for cc in range(A.shape[1]):
   if A[rr,cc]==-1:continue
   gp=(s.x+cc,s.y+rr)
   if gp not in inv:continue
   x,y=inv[gp];e.step(GameAction.from_id(6),data={"x":x,"y":y})
   if e._game.xseexqzst and e._game.xseexqzst.name in names:return
 raise RuntimeError(("select",names))
def move_selected(e,x,y,lc):
 r=None
 while e._game.xseexqzst.x!=x:
  r=e.step(GameAction.from_id(4 if x>e._game.xseexqzst.x else 3),data={})
  if r.levels_completed>lc or r.state.name!="NOT_FINISHED":return r
 while e._game.xseexqzst.y!=y:
  r=e.step(GameAction.from_id(2 if y>e._game.xseexqzst.y else 1),data={})
  if r.levels_completed>lc or r.state.name!="NOT_FINISHED":return r
 return r
def discover(e):
 out=[]
 for root in vis(e._game):
  names=group_names(e._game,root);p=copy.deepcopy(e);s=find_group(p._game,names);p._game.swfljqaiqu(s)
  seen=set();st=[]
  for k in range(24):
   s=p._game.xseexqzst;M=semantic_local(p._game,s)
   sig=(s.name,s.rotation,getattr(p._game,"ztpxqonhr",None),M,s.width,s.height)
   if sig in seen:break
   seen.add(sig);st.append((k,s.x,s.y,s.width,s.height,M,s.name,s.rotation))
   p.step(GameAction.from_id(5),data={})
  out.append((names,st))
 return out

def solve_level(e):
 g=e._game;W,H=g.current_level.grid_size;cycles=discover(e)
 states=[];index=[]
 for i,(names,cyc) in enumerate(cycles):
  opts=[]
  for k,bx,by,w,h,M,nm,rot in cyc:
   for x in range(W-w+1):
    for y in range(H-h+1):
     G=frozenset((x+dx,y+dy,v) for dx,dy,v in M)
     opts.append((k+abs(x-bx)+abs(y-by),k,x,y,G,nm,rot))
  states.append(opts)
  d=defaultdict(list)
  for st in opts:
   for p in st[4]:d[p].append(st)
  index.append(d)
 best=[None];nodes=[0]
 def rec(rem,occ,chosen,cost):
  nodes[0]+=1
  if best[0] is not None and cost>=best[0][0]:return
  if not rem:
   if occ and all(v==2 for v in occ.values()):best[0]=(cost,dict(chosen))
   return
  need=[p for p,v in occ.items() if v==1]
  if not need:
   j=max(rem,key=lambda q:max(len(st[4]) for st in states[q]))
   candidates=[(j,st) for st in states[j]]
  else:
   choices=[]
   for p in need:
    total=sum(len(index[j].get(p,())) for j in rem)
    if total:choices.append((total,p))
   if not choices:return
   _,p=min(choices)
   candidates=[(j,st) for j in rem for st in index[j].get(p,())]
  candidates.sort(key=lambda js:js[1][0])
  for j,st in candidates:
   c,k,x,y,G,nm,rot=st
   if any(occ.get(q,0)>=2 for q in G):continue
   no=dict(occ)
   for q in G:no[q]=no.get(q,0)+1
   chosen[j]=(k,x,y,G,nm,rot)
   rec(tuple(q for q in rem if q!=j),no,chosen,cost+c)
   del chosen[j]
 rec(tuple(range(len(states))),{}, {},0)
 return cycles,best[0],nodes[0]

def execute(e,cycles,sol,lc):
 r=None
 for i in range(len(cycles)):
  names,_=cycles[i];k,x,y,*_=sol[1][i]
  select_group(e,names)
  for _ in range(k):
   r=e.step(GameAction.from_id(5),data={})
   if r.levels_completed>lc or r.state.name!="NOT_FINISHED":return r
  r=move_selected(e,x,y,lc) or r
  if r is not None and (r.levels_completed>lc or r.state.name!="NOT_FINISHED"):return r
 return r

e=a.make("cn04");r=None
while True:
 lc=0 if r is None else r.levels_completed
 lev=e._game.level_index
 cycles,sol,nodes=solve_level(e)
 print("LEVEL",lev+1,"LC",lc,"CYCLES",[len(x[1]) for x in cycles],"NODES",nodes,"BEST",None if sol is None else sol[0],flush=True)
 if sol is None:raise RuntimeError(("no solution",lev))
 r=execute(e,cycles,sol,lc)
 print(" AFTER",r.levels_completed,r.state.name,e._game.level_index,flush=True)
 if r.state.name=="WIN":break
 if r.levels_completed<=lc:raise RuntimeError(("did not advance",lev))
print("FINAL",r.levels_completed,r.state.name,e._game.level_index)
assert r.levels_completed==6 and r.state.name=="WIN"
print("PASS cn04 fresh empirical-cycle typed-cover solver")
