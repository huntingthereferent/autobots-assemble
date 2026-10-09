from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np, copy

a=Arcade(operation_mode=OperationMode.NORMAL)

def invmap(cam):
 out={}
 for y in range(64):
  for x in range(64):
   g=cam.display_to_grid(x,y)
   if g is not None and g not in out:out[g]=(x,y)
 return out
def vis(g):return [s for s in g.current_level.get_sprites() if s.is_visible]
def current_selected(e):
 return e._game.xseexqzst
def semantic_local(game,s):
 saved=s.pixels.copy()
 s.pixels=game.hlxyvcmpk[s.name]
 A=np.array(s.render(),dtype=int)
 s.pixels=saved
 M=frozenset((c,r,int(A[r,c])) for r in range(A.shape[0]) for c in range(A.shape[1]) if int(A[r,c]) in (8,13))
 return M,A.shape
def group_names(game,s):
 try:return frozenset(x.name for x in game.vausolnec[s])
 except:return frozenset([s.name])
def find_group_sprite(game,names):
 for s in vis(game):
  if s.name in names:return s
 return None
def select_group(e,names):
 s=find_group_sprite(e._game,names)
 if s is None:raise RuntimeError(("group missing",names))
 if current_selected(e) is s:return s
 A=np.array(s.render(),dtype=int);inv=invmap(e._game.camera)
 for rr in range(A.shape[0]):
  for cc in range(A.shape[1]):
   if int(A[rr,cc])==-1:continue
   gp=(s.x+cc,s.y+rr)
   if gp not in inv:continue
   x,y=inv[gp]
   e.step(GameAction.from_id(6),data={"x":x,"y":y})
   if e._game.xseexqzst is not None and e._game.xseexqzst.name in names:return e._game.xseexqzst
 raise RuntimeError(("select failed",names,s.x,s.y))
def move_selected(e,x,y,base_lc):
 r=None
 while e._game.xseexqzst.x!=x:
  r=e.step(GameAction.from_id(4 if x>e._game.xseexqzst.x else 3),data={})
  if r.levels_completed>base_lc or r.state.name!="NOT_FINISHED":return r
 while e._game.xseexqzst.y!=y:
  r=e.step(GameAction.from_id(2 if y>e._game.xseexqzst.y else 1),data={})
  if r.levels_completed>base_lc or r.state.name!="NOT_FINISHED":return r
 return r

def discover_cycles(e):
 g=e._game;roots=vis(g);out=[]
 for root in roots:
  names=group_names(g,root)
  probe=copy.deepcopy(e)
  ps=find_group_sprite(probe._game,names)
  probe._game.swfljqaiqu(ps)
  seen=set();states=[]
  for k in range(16):
   s=probe._game.xseexqzst
   M,shape=semantic_local(probe._game,s)
   sig=(s.name,s.rotation,getattr(probe._game,"ztpxqonhr",None),M,shape)
   if sig in seen:break
   seen.add(sig)
   states.append((k,s.x,s.y,s.width,s.height,M,shape,s.name,s.rotation))
   probe.step(GameAction.from_id(5),data={})
  out.append((names,states))
 return out

def solve_level(e):
 g=e._game;W,H=g.current_level.grid_size;roots=vis(g)
 cycles=discover_cycles(e)
 print(" DISCOVER",[(i,len(st),[(q[0],q[3],q[4],q[7],q[8],len(q[5])) for q in st]) for i,(names,st) in enumerate(cycles)],flush=True)
 allstates=[]
 for i,(names,states) in enumerate(cycles):
  opts=[]
  for k,bx,by,w,h,M,shape,nm,rot in states:
   for x in range(W-w+1):
    for y in range(H-h+1):
     G=frozenset((x+dx,y+dy,v) for dx,dy,v in M)
     opts.append((k+abs(x-bx)+abs(y-by),k,x,y,G,nm,rot))
  allstates.append(opts)
 order=sorted(range(len(roots)),key=lambda i:-len(cycles[i][1][0][5]))
 best=[None];nodes=[0]
 def dfs(depth,occ,chosen,cost):
  nodes[0]+=1
  if best[0] is not None and cost>=best[0][0]:return
  if depth==len(order):
   if occ and all(v==2 for v in occ.values()):
    best[0]=(cost,dict(chosen))
   return
  i=order[depth];need={p for p,v in occ.items() if v==1}
  cand=allstates[i] if depth==0 else [s for s in allstates[i] if s[4]&need]
  for st in sorted(cand,key=lambda q:q[0]):
   c,k,x,y,G,nm,rot=st
   if any(occ.get(p,0)>=2 for p in G):continue
   no=dict(occ)
   for p in G:no[p]=no.get(p,0)+1
   chosen[i]=(k,x,y,G,nm,rot)
   dfs(depth+1,no,chosen,cost+c)
   del chosen[i]
 dfs(0,{}, {},0)
 print(" SEARCH_NODES",nodes[0],"BEST",best[0],flush=True)
 return cycles,best[0]

def execute(e,cycles,solution):
 base_lc=0 if e._game.level_index==0 else e._game.level_index
 # actual levels_completed equals level_index at level start in this game
 last=None
 for idx in range(len(cycles)):
  names,_=cycles[idx]
  k,x,y,G,nm,rot=solution[1][idx]
  select_group(e,names)
  for _ in range(k):
   last=e.step(GameAction.from_id(5),data={})
   if last.levels_completed>base_lc or last.state.name!="NOT_FINISHED":return last
  last=move_selected(e,x,y,base_lc) or last
  if last is not None and (last.levels_completed>base_lc or last.state.name!="NOT_FINISHED"):return last
 return last

e=a.make("cn04");r=None
total=len(e._game._levels)
print("TOTAL_LEVELS",total)
while True:
 lc=0 if r is None else r.levels_completed
 lev=e._game.level_index
 if r is not None and r.state.name=="WIN":break
 print("\nLEVEL",lev+1,"LC",lc,"SPRITES",[(s.name,s.x,s.y,s.rotation,s.width,s.height) for s in vis(e._game)],flush=True)
 cycles,sol=solve_level(e)
 if sol is None:raise RuntimeError(("no solution",lev))
 r=execute(e,cycles,sol)
 print(" AFTER","LC",None if r is None else r.levels_completed,"STATE",None if r is None else r.state.name,"LEVEL_INDEX",e._game.level_index,flush=True)
 if r is None:raise RuntimeError("no action")
 if r.state.name=="WIN":break
 if r.levels_completed<=lc:raise RuntimeError(("did not advance",lev,sol))
print("FINAL",r.levels_completed,r.state.name,e._game.level_index)
assert r.state.name=="WIN"
print("PASS cn04 empirical-cycle typed-cover full solve")
