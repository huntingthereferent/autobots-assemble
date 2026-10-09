# Reconstruct the first 37 Level-3 public candidates from saved cycle geometry,
# then emit their action-state tuples and marker-pairing graphs.
# Geometry values are public-observation results from cn04_public_l3_active_discovery.py.

from collections import defaultdict

# starts and public cycle marker offsets/size.
starts={0:(10,3),1:(2,4),2:(9,9)}
cycles={
0:[
 (0,(10,3),(6,2),[(0,1),(5,0)]),
 (1,(10,3),(7,13),[(1,0),(2,5)]),
 (2,(10,3),(7,7),[]),
],
1:[
 (0,(2,4),(5,7),[(4,0),(4,6)]),
 (1,(2,4),(7,5),[(0,4),(6,4)]),
 (2,(2,4),(5,7),[(0,0),(0,6)]),
 (3,(2,4),(7,5),[(0,0),(6,0)]),
],
2:[
 (0,(9,9),(7,7),[(1,0),(6,5)]),
 (1,(9,9),(7,7),[(1,6),(6,1)]),
 (2,(9,9),(7,7),[(0,1),(5,6)]),
 (3,(9,9),(7,7),[(0,5),(5,0)]),
]}
states=[];index=[]
for i in range(3):
 opts=[]
 for k,(bx,by),(w,h),offs in cycles[i]:
  for x in range(20-w+1):
   for y in range(20-h+1):
    M=tuple(sorted((x+dx,y+dy,j) for j,(dx,dy) in enumerate(offs)))
    pts=frozenset((a,b) for a,b,j in M)
    cost=k+abs(x-bx)+abs(y-by)
    if cost<=35:opts.append((cost,k,x,y,M,pts))
 states.append(opts)
 dct=defaultdict(list)
 for st in opts:
  for p in st[5]:dct[p].append(st)
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
  c,k,x,y,M,pts=st
  if cost+c>35 or any(count.get(q,0)>=2 for q in pts):continue
  nc=dict(count)
  for q in pts:nc[q]=nc.get(q,0)+1
  chosen[i]=st;dfs(tuple(j for j in rem if j!=i),nc,chosen,cost+c);del chosen[i]
dfs((0,1,2),{}, {},0)

uniq={}
for cost,pl in sols:
 key=tuple((i,pl[i][1],pl[i][2],pl[i][3]) for i in sorted(pl));uniq[key]=(cost,pl)
ranked=sorted(uniq.values(),key=lambda z:(z[0],tuple((i,z[1][i][1],z[1][i][2],z[1][i][3]) for i in sorted(z[1]))))

for n,(cost,pl) in enumerate(ranked[:37]):
 bypos=defaultdict(list)
 for i,st in pl.items():
  for x,y,j in st[4]:bypos[(x,y)].append((i,j))
 edges=tuple(sorted(tuple(sorted(v)) for v in bypos.values() if len(v)==2))
 kt=tuple(pl[i][1] for i in range(3))
 print(n,"OUT",n==36,"COST",cost,"K",kt,"EDGES",edges,"POS",tuple((pl[i][2],pl[i][3]) for i in range(3)))
