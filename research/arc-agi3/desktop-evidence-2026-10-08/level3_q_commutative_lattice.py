from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy,itertools
from collections import defaultdict

a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
Q=(2,2,2,1,1,5,1,7)
AX=[1,2,3,4]

e=a.make('ar25');r=None
for z in SOL+list(Q):r=e.step(GameAction.from_id(z),data={})
root=copy.deepcopy(e); rootk=r.frame[0].tobytes()

def apply_count(c):
 e=copy.deepcopy(root);rr=None
 w=[]
 for z,n in zip(AX,c):w += [z]*n
 if not w:return rootk,2,'NOT_FINISHED'
 for z in w:
  rr=e.step(GameAction.from_id(z),data={})
  if rr.levels_completed>2:return None,rr.levels_completed,rr.state.name
 return rr.frame[0].tobytes(),rr.levels_completed,rr.state.name

vecs=[]
for total in range(0,7):
 for c1 in range(total+1):
  for c2 in range(total-c1+1):
   for c3 in range(total-c1-c2+1):
    c4=total-c1-c2-c3
    vecs.append((c1,c2,c3,c4))

groups=defaultdict(list);close=[]
for c in vecs:
 k,l,s=apply_count(c)
 if l>2:close.append(c)
 else:groups[k].append(c)
print('VECS',len(vecs),'STATE_CLASSES',len(groups),'CLOSE',close,flush=True)

coll=[]
for vs in groups.values():
 if len(vs)>1:
  vs=sorted(vs,key=lambda x:(sum(x),x))
  base=vs[0]
  for v in vs[1:]:
   d=tuple(v[i]-base[i] for i in range(4))
   coll.append((sum(map(abs,d)),sum(v),base,v,d))
coll.sort()
print('COLLISIONS',len(coll),flush=True)
for row in coll[:80]:print('REL',row,flush=True)

# relations to root = identity vectors
ids=sorted([v for v in groups[rootk] if v!=(0,0,0,0)],key=lambda x:(sum(x),x))
print('IDENTITY_VECTORS',ids[:50],flush=True)
