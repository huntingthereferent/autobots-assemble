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
def vis(g):return [s for s in g.current_level.get_sprites() if s.is_visible]
def semantic_local(game,s):
 save=s.pixels.copy();s.pixels=game.hlxyvcmpk[s.name];A=np.array(s.render(),int);s.pixels=save
 return frozenset((c,r,int(A[r,c])) for r in range(A.shape[0]) for c in range(A.shape[1]) if int(A[r,c]) in (8,13))
def group_names(g,s):
 try:return frozenset(x.name for x in g.vausolnec[s])
 except:return frozenset([s.name])
def find_group(g,names):return next((s for s in vis(g) if s.name in names),None)
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
def move(e,names,x,y,lc):
 global r
 select_group(e,names)
 while e._game.xseexqzst.x!=x:
  r=e.step(GameAction.from_id(4 if x>e._game.xseexqzst.x else 3),data={})
  if r.levels_completed>lc or r.state.name!="NOT_FINISHED":return
 while e._game.xseexqzst.y!=y:
  r=e.step(GameAction.from_id(2 if y>e._game.xseexqzst.y else 1),data={})
  if r.levels_completed>lc or r.state.name!="NOT_FINISHED":return
def discover(e):
 out=[]
 for root in vis(e._game):
  names=group_names(e._game,root);p=copy.deepcopy(e);s=find_group(p._game,names);p._game.swfljqaiqu(s)
  seen=set();st=[]
  for k in range(20):
   s=p._game.xseexqzst;M=semantic_local(p._game,s);sig=(s.name,s.rotation,p._game.ztpxqonhr,M,s.width,s.height)
   if sig in seen:break
   seen.add(sig);st.append((k,s.x,s.y,s.width,s.height,M,s.name,s.rotation))
   p.step(GameAction.from_id(5),data={})
  out.append((names,st))
 return out
def do_plan(e,plan,cycles,lc):
 global r
 for i in range(len(cycles)):
  names,_=cycles[i];k,x,y,*_=plan[i]
  select_group(e,names)
  for _ in range(k):
   r=e.step(GameAction.from_id(5),data={})
   if r.levels_completed>lc or r.state.name!="NOT_FINISHED":return
  move(e,names,x,y,lc)
  if r is not None and (r.levels_completed>lc or r.state.name!="NOT_FINISHED"):return

plans=[
 {0:(0,3,3),1:(1,2,8)},
 {0:(0,4,11),1:(0,8,12),2:(0,3,9),3:(3,12,14)},
 {0:(0,9,9),1:(0,5,4),2:(2,9,3)},
 {0:(0,5,3),1:(3,10,8),2:(1,5,10),3:(1,5,12)},
 {0:(4,7,4),1:(0,5,5),2:(3,9,4),3:(3,11,8)},
]

e=a.make("cn04");r=None
for lc,pl in enumerate(plans):
 cyc=discover(e);do_plan(e,pl,cyc,lc)
 assert r.levels_completed==lc+1,(lc,r.levels_completed)
print("AT_FINAL",[(s.name,s.x,s.y,s.rotation,s.width,s.height) for s in vis(e._game)],"LC",r.levels_completed)

cycles=discover(e);g=e._game;W,H=g.current_level.grid_size
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
 print("OBJ",i,"CYCLE",len(cyc),"STATES",len(opts),"COUNTS",sorted({len(q[5]) for q in cyc}))

best=[None];nodes=[0]
def rec(rem,occ,chosen,cost):
 nodes[0]+=1
 if best[0] is not None and cost>=best[0][0]:return
 if not rem:
  if occ and all(v==2 for v in occ.values()):
   best[0]=(cost,dict(chosen));print("BEST",best[0],flush=True)
  return
 need=[p for p,v in occ.items() if v==1]
 if not need:
  j=max(rem,key=lambda x:max(len(st[4]) for st in states[x]))
  for st in sorted(states[j],key=lambda q:q[0]):
   c,k,x,y,G,nm,rot=st
   if any(occ.get(q,0)>=2 for q in G):continue
   no=dict(occ)
   for q in G:no[q]=no.get(q,0)+1
   chosen[j]=(k,x,y,G,nm,rot);rec(tuple(x for x in rem if x!=j),no,chosen,cost+c);del chosen[j]
  return
 choices=[]
 for p in need:
  total=sum(len(index[j].get(p,())) for j in rem)
  if total:choices.append((total,p))
 if not choices:return
 _,p=min(choices)
 pairs=[]
 for j in rem:
  for st in index[j].get(p,()):pairs.append((j,st))
 pairs.sort(key=lambda js:js[1][0])
 for j,st in pairs:
  c,k,x,y,G,nm,rot=st
  if any(occ.get(q,0)>=2 for q in G):continue
  no=dict(occ)
  for q in G:no[q]=no.get(q,0)+1
  chosen[j]=(k,x,y,G,nm,rot);rec(tuple(x for x in rem if x!=j),no,chosen,cost+c);del chosen[j]

rec(tuple(range(len(states))),{}, {},0)
print("NODES",nodes[0],"FINAL",best[0])
assert best[0]
do_plan(e,best[0][1],cycles,5)
print("RESULT",r.levels_completed,r.state.name,e._game.level_index)
assert r.state.name=="WIN" and r.levels_completed==6
print("PASS cn04 full 6/6 WIN")
