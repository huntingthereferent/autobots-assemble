from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np, copy
from collections import Counter,defaultdict

a=Arcade(operation_mode=OperationMode.NORMAL)

def public_grid(e):
 r=e.step(GameAction.from_id(7),data={})
 F=np.array(r.frame[0],int)
 G=np.array([[F[2+3*y,2+3*x] for x in range(20)] for y in range(20)],int)
 return G,r

def segment(G):
 bg=Counter(G.flatten().tolist()).most_common(1)[0][0]
 S={(x,y) for y in range(20) for x in range(20) if int(G[y,x])!=bg}
 comps=[]
 while S:
  p=S.pop();q=[p];c={p}
  while q:
   x,y=q.pop()
   for n in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
    if n in S:S.remove(n);c.add(n);q.append(n)
  comps.append(c)
 out=[]
 for c in comps:
  xs=[x for x,y in c];ys=[y for x,y in c]
  box=(min(xs),min(ys),max(xs),max(ys))
  vals={int(G[y,x]) for x,y in c}
  marks={(x,y) for x,y in c if int(G[y,x])==8}
  out.append(dict(cells=c,box=box,vals=vals,marks=marks,bg=bg))
 return out

def click(e,x,y):
 return e.step(GameAction.from_id(6),data={"x":2+3*x,"y":2+3*y})

def reach_l2():
 e=a.make("cn04")
 click(e,13,9);e.step(GameAction.from_id(5),data={})
 for _ in range(10):e.step(GameAction.from_id(3),data={})
 e.step(GameAction.from_id(1),data={})
 G,r=public_grid(e)
 assert r.levels_completed==1
 return e,G

e,G=reach_l2()
segs=segment(G)
# Remove tiny/header-like component by requiring at least one marker.
objs=[o for o in segs if o["marks"]]
objs.sort(key=lambda o:(o["box"][1],o["box"][0]))
print("BG",objs[0]["bg"],"OBJECTS",len(objs))
for i,o in enumerate(objs):
 print("OBJ",i,"BOX",o["box"],"MARKS",sorted(o["marks"]),"VALS",sorted(o["vals"]),"N",len(o["cells"]))

# identify selected object by ordinary color 0
selidx=next(i for i,o in enumerate(objs) if 0 in o["vals"])
print("SELECTED",selidx)

# Discover each object's public action5 visual sequence from a fresh L2.
cycles=[]
for i,o0 in enumerate(objs):
 ee,_=reach_l2()
 G0,_=public_grid(ee);oo=[o for o in segment(G0) if o["marks"]];oo.sort(key=lambda o:(o["box"][1],o["box"][0]))
 target=oo[i]
 if i!=selidx:
  # click a non-background occupied cell, preferring ordinary not marker
  candidates=[p for p in target["cells"] if int(G0[p[1],p[0]])!=8] or list(target["cells"])
  x,y=sorted(candidates)[0];click(ee,x,y)
 states=[];seen={}
 for k in range(8):
  GG,_=public_grid(ee)
  ss=[o for o in segment(GG) if 0 in o["vals"]]
  if len(ss)!=1:
   print("BAD_SELECTED",i,k,len(ss));break
  s=ss[0];x0,y0,x1,y1=s["box"]
  offs=frozenset((x-x0,y-y0) for x,y in s["marks"])
  # canonical selected visual: occupied cells relative bbox, marker flag only
  occ=frozenset((x-x0,y-y0,1 if int(GG[y,x])==8 else 0) for x,y in s["cells"])
  sig=(x1-x0+1,y1-y0+1,occ)
  if sig in seen:
   print(" REPEAT",i,"at",k,"prior",seen[sig])
   break
  seen[sig]=k
  states.append((k,(x0,y0),(x1-x0+1,y1-y0+1),offs,occ))
  ee.step(GameAction.from_id(5),data={})
 cycles.append(states)
 print("CYCLE",i,"LEN",len(states),[(q[0],q[2],sorted(q[3])) for q in states])

# Enumerate untyped exact-pair-cover configurations.
states=[]
for i,cyc in enumerate(cycles):
 opts=[]
 for k,(bx,by),(w,h),offs,occ in cyc:
  for x in range(20-w+1):
   for y in range(20-h+1):
    M=frozenset((x+dx,y+dy) for dx,dy in offs)
    cost=k+abs(x-bx)+abs(y-by)
    opts.append((cost,k,x,y,M))
 states.append(opts)

order=sorted(range(len(states)),key=lambda i:-len(cycles[i][0][3]))
solutions=[];nodes=[0]
def dfs(d,count,chosen,cost):
 nodes[0]+=1
 if len(solutions)>=30:return
 if d==len(order):
  if count and all(v==2 for v in count.values()):
   solutions.append((cost,dict(chosen)))
  return
 i=order[d]
 need={p for p,v in count.items() if v==1}
 cand=states[i] if not need else [s for s in states[i] if s[4]&need]
 for st in sorted(cand,key=lambda z:z[0]):
  c,k,x,y,M=st
  if any(count.get(p,0)>=2 for p in M):continue
  nc=dict(count)
  for p in M:nc[p]=nc.get(p,0)+1
  chosen[i]=(k,x,y,M)
  dfs(d+1,nc,chosen,cost+c)
  del chosen[i]
  if len(solutions)>=30:return

dfs(0,{}, {},0)
solutions.sort(key=lambda z:z[0])
print("SEARCH_NODES",nodes[0],"SOLUTIONS",len(solutions))
for j,s in enumerate(solutions[:20]):print("SOL",j,s)
