from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
from collections import Counter

a=Arcade(operation_mode=OperationMode.NORMAL)
def click(e,x,y): return e.step(GameAction.from_id(6),data={"x":2+3*x,"y":2+3*y})
def move(e,dx,dy,lc):
 r=None
 for _ in range(abs(dx)):
  r=e.step(GameAction.from_id(4 if dx>0 else 3),data={})
  if r.levels_completed>lc:return r
 for _ in range(abs(dy)):
  r=e.step(GameAction.from_id(2 if dy>0 else 1),data={})
  if r.levels_completed>lc:return r
 return r

# Publicly discovered replay to Level 3.
def reach_l3():
 e=a.make("cn04")
 # L1 public solution
 click(e,13,9);e.step(GameAction.from_id(5),data={})
 for _ in range(10):e.step(GameAction.from_id(3),data={})
 r=e.step(GameAction.from_id(1),data={})
 assert r.levels_completed==1
 # L2 first public-success plan:
 # obj0 no-op; obj1 (12,4)->(8,6); obj2 (4,11)->(4,5); obj3 k3 (16,16)->(12,8)
 click(e,12,10);r=move(e,-4,2,1) or r
 click(e,5,13);r=move(e,0,-6,1) or r
 click(e,16,17)
 for _ in range(3):r=e.step(GameAction.from_id(5),data={})
 r=move(e,-4,-8,1) or r
 assert r.levels_completed==2,(r.levels_completed,r.state.name)
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
  vals={int(G[y,x]) for x,y in c};marks={(x,y) for x,y in c if int(G[y,x])==8}
  box=(min(x for x,y in c),min(y for x,y in c),max(x for x,y in c),max(y for x,y in c))
  out.append({"cells":c,"vals":vals,"marks":marks,"box":box})
 return out

# stable public L3 observation (discovery run only)
root,rr=reach_l3();rr=root.step(GameAction.from_id(7),data={});G0=decode(rr)
objs=segment(G0);objs.sort(key=lambda o:(o["box"][1],o["box"][0]))
# infer current selection as the unique object not flattened to public material color 4
selcand=[i for i,o in enumerate(objs) if any(v not in (4,8) for v in o["vals"])]
selidx=selcand[0] if len(selcand)==1 else None
clicks=[]
for o in objs:
 clicks.append(sorted(o["cells"])[0])
starts={i:(o["box"][0],o["box"][1]) for i,o in enumerate(objs)}
print("L3_OBJECTS",[(i,o["box"],sorted(o["marks"]),clicks[i]) for i,o in enumerate(objs)],"SEL",selidx)

# discover public action5 cycles (visual state only)
cycles=[]
for i in range(len(objs)):
 ee,r=reach_l3();r=ee.step(GameAction.from_id(7),data={})
 cp=clicks[i]
 if i!=selidx:r=click(ee,*cp)
 seen=set();cyc=[];prev=set(objs[i]["cells"])
 for k in range(12):
  G=decode(r);oo=segment(G)
  # selected object is the component with maximum overlap with the prior footprint;
  # on k=0 require it to contain the clicked cell.
  if k==0:
   cand=[o for o in oo if cp in o["cells"]]
   s=max(cand,key=lambda o:len(o["cells"])) if cand else max(oo,key=lambda o:len(o["cells"]&prev))
  else:
   s=max(oo,key=lambda o:len(o["cells"]&prev))
  x0,y0,x1,y1=s["box"]
  marks=frozenset((x-x0,y-y0) for x,y in s["marks"])
  occ=frozenset((x-x0,y-y0) for x,y in s["cells"])
  sig=(x1-x0+1,y1-y0+1,marks,occ)
  if sig in seen:break
  seen.add(sig);cyc.append((k,(x0,y0),(x1-x0+1,y1-y0+1),marks,occ))
  prev=set(s["cells"])
  r=ee.step(GameAction.from_id(5),data={})
 cycles.append(cyc)
 print("CYCLE",i,"LEN",len(cyc),[(q[0],q[2],sorted(q[3])) for q in cyc])

# untyped geometric states
states=[];index=[]
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
 dct={}
 for st in opts:
  for p in st[4]:dct.setdefault(p,[]).append(st)
 index.append(dct)

sols=[]
def dfs(rem,count,chosen,cost):
 if cost>35:return
 if not rem:
  if count and all(v==2 for v in count.values()):sols.append((cost,dict(chosen)))
  return
 need=[p for p,v in count.items() if v==1]
 if need:
  choices=[(sum(len(index[i].get(p,())) for i in rem),p) for p in need]
  choices=[x for x in choices if x[0]]
  if not choices:return
  _,p=min(choices);pairs=[(i,st) for i in rem for st in index[i].get(p,())]
 else:
  i=max(rem,key=lambda j:len(cycles[j][0][3]));pairs=[(i,st) for st in states[i]]
 pairs.sort(key=lambda z:z[1][0])
 for i,st in pairs:
  c,k,x,y,M,O=st
  if cost+c>35 or any(count.get(q,0)>=2 for q in M):continue
  nc=dict(count)
  for q in M:nc[q]=nc.get(q,0)+1
  chosen[i]=(k,x,y,M,O);dfs(tuple(j for j in rem if j!=i),nc,chosen,cost+c);del chosen[i]

dfs(tuple(range(len(states))),{}, {},0)
uniq={}
for cost,pl in sols:
 key=tuple((i,pl[i][0],pl[i][1],pl[i][2]) for i in sorted(pl));uniq[key]=(cost,pl)
ranked=sorted(uniq.values(),key=lambda z:(z[0],tuple((i,z[1][i][0],z[1][i][1],z[1][i][2]) for i in sorted(z[1]))))
print("CANDIDATES",len(ranked),"COSTS",[z[0] for z in ranked[:20]])

def run_plan(pl):
 e,r=reach_l3();remaining=set(range(len(objs)));placed=set()
 while remaining:
  choice=None
  for i in sorted(remaining):
   avail=[p for p in objs[i]["cells"] if p not in placed]
   if avail:choice=(i,sorted(avail)[0]);break
  if choice is None:return False,r
  i,p=choice
  if selidx is None or not (i==selidx and len(remaining)==len(objs)):r=click(e,*p)
  k,gx,gy,M,O=pl[i]
  for _ in range(k):
   r=e.step(GameAction.from_id(5),data={})
   if r.levels_completed>2:return True,r
   if r.state.name!="NOT_FINISHED":return False,r
  sx,sy=starts[i];r=move(e,gx-sx,gy-sy,2) or r
  if r.levels_completed>2:return True,r
  if r.state.name!="NOT_FINISHED":return False,r
  placed|=O;remaining.remove(i)
 return False,r

for j,(cost,pl) in enumerate(ranked[:100]):
 ok,r=run_plan(pl)
 print("TRIAL",j,"COST",cost,"OK",ok,"LC",r.levels_completed,flush=True)
 if ok:
  print("FIRST_L3_PUBLIC_SUCCESS",j,cost,{i:(pl[i][0],pl[i][1],pl[i][2],sorted(pl[i][3])) for i in sorted(pl)})
  break
else:
 raise RuntimeError("no L3 public success in first 100")
