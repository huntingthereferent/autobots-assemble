from collections import defaultdict

# Persistent marker ids per object: a0,a1 / b0,b1 / c0,c1.
# Publicly learned geometric states and identity permutations.
statespec={
0:[
 (0,(10,3),(6,2),[(0,1,'a0'),(5,0,'a1')]),
 (1,(10,3),(2,6),[(0,0,'a0'),(1,5,'a1')]),
 (2,(10,3),(6,2),[(0,1,'a1'),(5,0,'a0')]),
 (3,(10,3),(2,6),[(0,0,'a1'),(1,5,'a0')]),
],
1:[
 (0,(2,4),(5,7),[(4,0,'b0'),(4,6,'b1')]),
 (1,(2,4),(7,5),[(0,4,'b1'),(6,4,'b0')]),
 (2,(2,4),(5,7),[(0,0,'b1'),(0,6,'b0')]),
 (3,(2,4),(7,5),[(0,0,'b0'),(6,0,'b1')]),
],
2:[
 (0,(9,9),(7,7),[(1,0,'c0'),(6,5,'c1')]),
 (1,(9,9),(7,7),[(1,6,'c1'),(6,1,'c0')]),
 (2,(9,9),(7,7),[(0,1,'c1'),(5,6,'c0')]),
 (3,(9,9),(7,7),[(0,5,'c0'),(5,0,'c1')]),
]}

H1={'a0':0,'a1':0,'b0':1,'b1':0,'c0':0,'c1':1}
H2={'a0':0,'a1':1,'b0':0,'b1':0,'c0':1,'c1':0}

opts=[];index=[]
for i in range(3):
 arr=[]
 for k,(bx,by),(w,h),marks in statespec[i]:
  for x in range(20-w+1):
   for y in range(20-h+1):
    items=tuple((x+dx,y+dy,m) for dx,dy,m in marks)
    pts=frozenset((px,py) for px,py,m in items)
    cost=k+abs(x-bx)+abs(y-by)
    if cost<=35:arr.append((cost,k,x,y,items,pts))
 opts.append(arr)
 dd=defaultdict(list)
 for st in arr:
  for p in st[5]:dd[p].append(st)
 index.append(dd)

sol=[]
def rec(rem,count,ch,cost):
 if cost>35:return
 if not rem:
  if count and all(v==2 for v in count.values()):
   by=defaultdict(list)
   for i,st in ch.items():
    for x,y,m in st[4]:by[(x,y)].append(m)
   pairs=tuple(sorted(tuple(sorted(v)) for v in by.values()))
   def pred(H):return all(H[a]==H[b] for a,b in pairs)
   if pred(H1)!=pred(H2):
    sol.append((cost,dict(ch),pairs,pred(H1),pred(H2)))
   return
 need=[p for p,v in count.items() if v==1]
 if need:
  choices=[(sum(len(index[i].get(p,())) for i in rem),p) for p in need]
  choices=[z for z in choices if z[0]]
  if not choices:return
  _,p=min(choices);pairs=[(i,st) for i in rem for st in index[i].get(p,())]
 else:
  i=0 if 0 in rem else min(rem);pairs=[(i,st) for st in opts[i]]
 for i,st in pairs:
  c,k,x,y,items,pts=st
  if cost+c>35 or any(count.get(q,0)>=2 for q in pts):continue
  nc=dict(count)
  for q in pts:nc[q]=nc.get(q,0)+1
  ch[i]=st;rec(tuple(j for j in rem if j!=i),nc,ch,cost+c);del ch[i]
rec((0,1,2),{}, {},0)
sol.sort(key=lambda z:z[0])
print("DISCRIMINATING",len(sol))
for j,z in enumerate(sol[:20]):
 cost,ch,pairs,p1,p2=z
 print(j,"COST",cost,"PRED",p1,p2,"K",tuple(ch[i][1] for i in range(3)),"POS",tuple((ch[i][2],ch[i][3]) for i in range(3)),"PAIRS",pairs)
