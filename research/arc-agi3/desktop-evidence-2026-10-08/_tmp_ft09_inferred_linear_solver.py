from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from collections import defaultdict
import copy,itertools,math
def parity(x):return x.bit_count()&1
def linear_solve(e):
 g=e._game
 nodes=sorted(g.fhc+g.mou,key=lambda s:(s.y,s.x))
 positions=[(s.x,s.y) for s in nodes];ix={p:i for i,p in enumerate(positions)}
 initial=[int(s.pixels[1,1]) for s in nodes]
 print('LEVEL',g.level_index+1,'COLORS',g.gqb,'NODES',len(nodes),'NTI',len(g.mou),'CONSTRAINTS',len(g.gig),'BUDGET',g.lpw.dzy,flush=True)
 targets=defaultdict(set)
 for con in g.gig:
  c=int(con.pixels[1,1])
  if c not in g.gqb:raise RuntimeError(('unknown reference color',c,g.gqb))
  for dy in (-1,0,1):
   for dx in (-1,0,1):
    if (dx,dy)==(0,0):continue
    coord=(con.x+dx*4,con.y+dy*4)
    if coord not in ix:continue
    same=int(con.pixels[dy+1,dx+1])==0
    targets[ix[coord]].add(g.gqb.index(c)^int(not same))
 if any(len(v)>1 for v in targets.values()):
  raise RuntimeError(('contradictory targets',[(positions[i],v) for i,v in targets.items() if len(v)>1]))
 before={pos:int(obj.pixels[1,1]) for pos,obj in zip(positions,nodes)}
 effects=[]; actions=[]
 for obj in nodes:
  x,y=obj.x,obj.y
  q=copy.deepcopy(e)
  rr=q.step(GameAction.ACTION6,data={'x':x*2,'y':y*2})
  if rr.levels_completed>g.level_index:
   print('SINGLE_CLICK_SOLVES',(x*2,y*2),flush=True)
   return [(x*2,y*2)]
  after={(s.x,s.y):int(s.pixels[1,1]) for s in q._game.fhc+q._game.mou}
  flips=0
  for i,pos in enumerate(positions):
   if pos in after and before[pos]!=after[pos]:flips|=1<<i
  if flips:
   actions.append((int(x*2),int(y*2)));effects.append(flips)
 m=len(actions);rows=[]
 for i,possible in targets.items():
  if initial[i] not in g.gqb:raise RuntimeError(('untyped node',positions[i],initial[i]))
  rhs=next(iter(possible))^g.gqb.index(initial[i])
  mask=sum((1<<j) for j,bits in enumerate(effects) if (bits>>i)&1)
  rows.append((mask,rhs,i))
 piv={}
 for mask,rhs,i in rows:
  while mask:
   p=(mask&-mask).bit_length()-1
   if p in piv:pm,pr=piv[p];mask^=pm;rhs^=pr
   else:piv[p]=(mask,rhs);break
  if mask==0 and rhs:raise RuntimeError(('unsatisfiable',i,len(rows),m))
 def backsolve(free):
  sol=free
  for p in sorted(piv,reverse=True):
   mask,rhs=piv[p]
   if rhs^parity((mask^(1<<p))&sol):sol|=1<<p
   else:sol&=~(1<<p)
  return sol
 particular=backsolve(0)
 freecols=[j for j in range(m) if j not in piv]
 basis=[backsolve(1<<j)^particular for j in freecols]
 best=particular
 if len(basis)<=16:
  cur=particular;prevgray=0
  for z in range(1,1<<len(basis)):
   gray=z^(z>>1);bit=(gray^prevgray).bit_length()-1;cur^=basis[bit];prevgray=gray
   if cur.bit_count()<best.bit_count():best=cur
 else:
  improving=True
  while improving:
   improving=False
   for mask in basis:
    if (best^mask).bit_count()<best.bit_count():best^=mask;improving=True
 # verify desired assignment from binary model
 for mask,rhs,i in rows:
  assert parity(mask&best)==rhs,('bad solve',i)
 print('MODEL','ACTIONS',m,'ROWS',len(rows),'RANK',len(piv),'FREE',len(basis),'PLANNED_CLICKS',best.bit_count(),'TOTAL_TARGETS',len(targets),'START_INCONSISTENT',sum(next(iter(v))!=g.gqb.index(initial[i]) for i,v in targets.items()),flush=True)
 return [actions[j] for j in range(m) if (best>>j)&1]
arc=Arcade(operation_mode=OperationMode.NORMAL);env=arc.make('ft09')
solved=[]
for i in range(6):
 if env._last_response.state.name=='WIN':break
 startlev=env._game.level_index
 path=linear_solve(env);local=[]
 for x,y in path:
  r=env.step(GameAction.ACTION6,data={'x':x,'y':y});local.append((x,y))
  if r.levels_completed>startlev:break
 print('EXEC',i+1,'PATH',local,'OUTPUT',r.levels_completed,r.state.name,'INDEX',env._game.level_index,'REMAIN',env._game.lpw.dzy,flush=True)
 if env._game.level_index==startlev and r.state.name!='WIN':
  print('WALL at',startlev,'candidate',path,flush=True);break
 solved.append(local)
 if r.state.name=='WIN':break
print('FINAL',env._last_response.levels_completed,env._last_response.state.name,'RECORD',solved,'SCORE',arc.get_scorecard().score,flush=True)
