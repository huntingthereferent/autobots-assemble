from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np, copy
from collections import Counter

a=Arcade(operation_mode=OperationMode.NORMAL)

def click(e,x,y): return e.step(GameAction.from_id(6),data={"x":2+3*x,"y":2+3*y})

def reach_l2():
 e=a.make("cn04")
 click(e,13,9); e.step(GameAction.from_id(5),data={})
 for _ in range(10): e.step(GameAction.from_id(3),data={})
 r=e.step(GameAction.from_id(1),data={})
 assert r.levels_completed==1
 return e,r

def decode(r):
 if not r.frame:return None
 F=np.array(r.frame[0],int)
 return np.array([[F[2+3*y,2+3*x] for x in range(20)] for y in range(20)],int)

def segment(G):
 bg=Counter(G.flatten().tolist()).most_common(1)[0][0]
 S={(x,y) for y in range(20) for x in range(20) if int(G[y,x])!=bg}
 out=[]
 while S:
  p=S.pop();q=[p];c={p}
  while q:
   x,y=q.pop()
   for n in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
    if n in S:S.remove(n);c.add(n);q.append(n)
  vals={int(G[y,x]) for x,y in c}
  marks={(x,y) for x,y in c if int(G[y,x])==8}
  if marks:
   box=(min(x for x,y in c),min(y for x,y in c),max(x for x,y in c),max(y for x,y in c))
   out.append({"cells":c,"vals":vals,"marks":marks,"box":box})
 return out

# Discover initial public objects and action5 cycles from fresh L2 copies.
root,r0=reach_l2();r0=root.step(GameAction.from_id(7),data={});G0=decode(r0)
objs=segment(G0);objs.sort(key=lambda o:(o["box"][1],o["box"][0]))
selidx=next(i for i,o in enumerate(objs) if 0 in o["vals"])
clicks=[]
for o in objs:
 ordinary=[p for p in o["cells"] if int(G0[p[1],p[0]])!=8]
 clicks.append(sorted(ordinary or list(o["cells"]))[0])
starts={i:(o["box"][0],o["box"][1]) for i,o in enumerate(objs)}
print("PUBLIC_OBJECTS",[(i,o["box"],sorted(o["marks"]),clicks[i]) for i,o in enumerate(objs)],"SEL",selidx)

cycles=[]
for i in range(len(objs)):
 ee,rr=reach_l2()
 rr=ee.step(GameAction.from_id(7),data={})
 if i!=selidx:
  rr=click(ee,*clicks[i])
 seen=set();states=[]
 for k in range(4):
  G=decode(rr);oo=segment(G)
  ss=[o for o in oo if 0 in o["vals"]]
  assert len(ss)==1,(i,k,[(o["box"],o["vals"]) for o in oo])
  s=ss[0];x0,y0,x1,y1=s["box"]
  marks=frozenset((x-x0,y-y0) for x,y in s["marks"])
  occ=frozenset((x-x0,y-y0) for x,y in s["cells"])
  states.append((k,(x0,y0),(x1-x0+1,y1-y0+1),marks,occ))
  rr=ee.step(GameAction.from_id(5),data={})
 cycles.append(states)

# Enumerate every geometric exact-pair cover with cost <= 35.
states=[]
for i,cyc in enumerate(cycles):
 opts=[]
 for k,(bx,by),(w,h),marks,occ in cyc:
  for x in range(20-w+1):
   for y in range(20-h+1):
    M=frozenset((x+dx,y+dy) for dx,dy in marks)
    O=frozenset((x+dx,y+dy) for dx,dy in occ)
    cost=k+abs(x-bx)+abs(y-by)
    if cost<=35:opts.append((cost,k,x,y,M,O))
 states.append(opts)

index=[]
for opts in states:
 d={}
 for st in opts:
  for p in st[4]:d.setdefault(p,[]).append(st)
 index.append(d)
sols=[]
def dfs(rem,count,chosen,cost):
 if cost>35:return
 if not rem:
  if count and all(v==2 for v in count.values()):
   sols.append((cost,dict(chosen)))
  return
 need=[p for p,v in count.items() if v==1]
 if need:
  choices=[]
  for p in need:
   total=sum(len(index[i].get(p,())) for i in rem)
   if total:choices.append((total,p))
  if not choices:return
  _,p=min(choices)
  pairs=[(i,st) for i in rem for st in index[i].get(p,())]
 else:
  i=max(rem,key=lambda j:len(cycles[j][0][3]))
  pairs=[(i,st) for st in states[i]]
 pairs.sort(key=lambda z:z[1][0])
 for i,st in pairs:
  c,k,x,y,M,O=st
  if cost+c>35 or any(count.get(q,0)>=2 for q in M):continue
  nc=dict(count)
  for q in M:nc[q]=nc.get(q,0)+1
  chosen[i]=(k,x,y,M,O)
  dfs(tuple(j for j in rem if j!=i),nc,chosen,cost+c)
  del chosen[i]

dfs(tuple(range(len(states))),{}, {},0)
# dedupe exact plans
uniq={}
for cost,pl in sols:
 key=tuple((i,pl[i][0],pl[i][1],pl[i][2]) for i in sorted(pl))
 uniq[key]=(cost,pl)
ranked=sorted(uniq.values(),key=lambda z:(z[0],tuple((i,z[1][i][0],z[1][i][1],z[1][i][2]) for i in sorted(z[1]))))
print("GEOMETRIC_CANDIDATES",len(ranked),"BEST_COSTS",[x[0] for x in ranked[:20]])

def run_plan(plan):
 e,r=reach_l2()
 placed=set()
 remaining=set(range(len(objs)))
 # choose an execution order dynamically: an object is selectable if one of its
 # initial occupied cells is not covered by already placed final footprints.
 while remaining:
  picked=None
  for i in sorted(remaining):
   available=[p for p in objs[i]["cells"] if p not in placed]
   if available:
    picked=(i,sorted(available)[0]);break
  if picked is None:return False,None
  i,p=picked
  if i!=selidx or remaining!=set(range(len(objs))):
   r=click(e,*p)
  k,gx,gy,M,O=plan[i]
  for _ in range(k):
   r=e.step(GameAction.from_id(5),data={})
   if r.levels_completed>1:return True,r
   if r.state.name!="NOT_FINISHED":return False,r
  sx,sy=starts[i]
  dx,dy=gx-sx,gy-sy
  for _ in range(abs(dx)):
   r=e.step(GameAction.from_id(4 if dx>0 else 3),data={})
   if r.levels_completed>1:return True,r
   if r.state.name!="NOT_FINISHED":return False,r
  for _ in range(abs(dy)):
   r=e.step(GameAction.from_id(2 if dy>0 else 1),data={})
   if r.levels_completed>1:return True,r
   if r.state.name!="NOT_FINISHED":return False,r
  placed|=O
  remaining.remove(i)
 return False,r

for j,(cost,pl) in enumerate(ranked):
 ok,r=run_plan(pl)
 print("TRIAL",j,"COST",cost,"OK",ok,"LC",None if r is None else r.levels_completed,flush=True)
 if ok:
  print("FIRST_PUBLIC_SUCCESS",j,cost,{i:(pl[i][0],pl[i][1],pl[i][2],sorted(pl[i][3])) for i in sorted(pl)})
  break
else:
 raise RuntimeError("no public candidate succeeded")
