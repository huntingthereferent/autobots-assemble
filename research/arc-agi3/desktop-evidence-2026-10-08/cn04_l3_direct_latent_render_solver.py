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
def selidx(e):
 sp=vis(e._game);return sp.index(e._game.xseexqzst) if e._game.xseexqzst in sp else -1
def select(e,idx):
 if selidx(e)==idx:return
 sp=vis(e._game);s=sp[idx];A=np.array(s.render(),dtype=int);inv=invmap(e._game.camera)
 for rr in range(A.shape[0]):
  for cc in range(A.shape[1]):
   if int(A[rr,cc])==-1:continue
   gp=(s.x+cc,s.y+rr)
   if gp not in inv:continue
   x,y=inv[gp];e.step(GameAction.from_id(6),data={"x":x,"y":y})
   if selidx(e)==idx:return
 raise RuntimeError(idx)
def move(e,idx,x,y,lc):
 global r
 select(e,idx)
 while e._game.xseexqzst.x!=x:
  r=e.step(GameAction.from_id(4 if x>e._game.xseexqzst.x else 3),data={})
  if r.levels_completed>lc:return r
 while e._game.xseexqzst.y!=y:
  r=e.step(GameAction.from_id(2 if y>e._game.xseexqzst.y else 1),data={})
  if r.levels_completed>lc:return r
 return r

def semantic_local(game,s):
 saved=s.pixels.copy()
 s.pixels=game.hlxyvcmpk[s.name]
 A=np.array(s.render(),dtype=int)
 s.pixels=saved
 return frozenset((c,rr,int(A[rr,c])) for rr in range(A.shape[0]) for c in range(A.shape[1]) if int(A[rr,c]) in (8,13)),A.shape

# reach L3
e=a.make("cn04");r=None
for z,data in [(6,{"x":41,"y":31}),(5,{})]+[(3,{})]*10+[(1,{})]:r=e.step(GameAction.from_id(z),data=data)
move(e,1,8,12,1);move(e,2,3,9,1);select(e,3)
for _ in range(3):r=e.step(GameAction.from_id(5),data={})
r=move(e,3,12,14,1) or r
assert r.levels_completed==2
g=e._game;sp=vis(g);W,H=g.current_level.grid_size
print("L3START",[(i,s.x,s.y,s.rotation,s.width,s.height) for i,s in enumerate(sp)])

cycles=[]
for idx in range(len(sp)):
 probe=copy.deepcopy(e);ps=vis(probe._game);probe._game.swfljqaiqu(ps[idx])
 seen=set();states=[]
 for k in range(12):
  s=probe._game.xseexqzst
  M,shape=semantic_local(probe._game,s)
  sig=(s.name,s.rotation,probe._game.ztpxqonhr,M,shape)
  if sig in seen:break
  seen.add(sig);states.append((k,s.x,s.y,s.width,s.height,M,shape))
  probe.step(GameAction.from_id(5),data={})
 cycles.append(states)
 print("CYCLE",idx,[(k,w,h,sorted(M)) for k,bx,by,w,h,M,shape in states])

allstates=[]
for idx,states in enumerate(cycles):
 opts=[]
 for k,bx,by,w,h,M,shape in states:
  for x in range(W-w+1):
   for y in range(H-h+1):
    G=frozenset((x+dx,y+dy,v) for dx,dy,v in M)
    opts.append((k+abs(x-bx)+abs(y-by),k,x,y,G))
 allstates.append(opts)

order=sorted(range(len(sp)),key=lambda i:-len(cycles[i][0][5]))
best=[None]
def dfs(d,occ,chosen,cost):
 if best[0] is not None and cost>=best[0][0]:return
 if d==len(order):
  if occ and all(v==2 for v in occ.values()):
   best[0]=(cost,dict(chosen));print("BEST",best[0],flush=True)
  return
 i=order[d];need={p for p,v in occ.items() if v==1}
 cand=allstates[i] if d==0 else [s for s in allstates[i] if s[4]&need]
 for st in sorted(cand,key=lambda x:x[0]):
  c,k,x,y,G=st
  if any(occ.get(p,0)>=2 for p in G):continue
  no=dict(occ)
  for p in G:no[p]=no.get(p,0)+1
  chosen[i]=(k,x,y,G);dfs(d+1,no,chosen,cost+c);del chosen[i]
dfs(0,{}, {},0)
print("FINAL",best[0])
assert best[0]

# execute found candidate publicly
plan=best[0][1]
for idx in range(len(sp)):
 k,x,y,G=plan[idx]
 select(e,idx)
 for _ in range(k):
  r=e.step(GameAction.from_id(5),data={})
  if r.levels_completed>2:break
 if r.levels_completed>2:break
 r=move(e,idx,x,y,2) or r
 if r.levels_completed>2:break
print("RESULT","LC",r.levels_completed,"LEVEL",e._game.level_index,"STATE",r.state.name)
assert r.levels_completed>=3
print("PASS L3 direct latent-render empirical-cycle cover")
