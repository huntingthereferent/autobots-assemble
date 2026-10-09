from __future__ import annotations
import sys,logging,collections
from pathlib import Path
import numpy as np
from arc_agi import Arcade,OperationMode
from arcengine import GameAction,GameState
sys.path.insert(0,r'C:\Users\teepa\arc3\ARC-AGI-3-Kaggle-Starter\vendor\ARC-AGI-3-Agents')
from agents.agent import Agent

def parse(frame):
 a=np.asarray(frame.frame[-1],dtype=np.int16).reshape(64,64)
 cand=[]
 for y in range(2,56,2):
  for x in range(2,56,2):
   block=a[y:y+6:2,x:x+6:2]
   if block.shape!=(3,3):continue
   center=int(block[1,1]);allvals=[int(v) for v in block.flatten()];ring=[int(v) for v in np.delete(block.flatten(),4)]
   if center<8 or center==13:continue
   typ=None
   if all(v==center for v in allvals):typ='node'
   elif 6 in allvals and all(v in (center,6) for v in allvals):typ='multi'
   elif all(v in (0,2,3,4) for v in ring) and sum(v in (0,2,3) for v in ring)>=3:typ='ref'
   if typ:cand.append((x,y,typ,center,tuple(tuple(int(q) for q in row) for row in block)))
 lattice=collections.Counter((x%8,y%8) for x,y,t,c,p in cand)
 best=max(lattice,key=lattice.get)
 filtered=[it for it in cand if (it[0]%8,it[1]%8)==best]
 nodes=[(x,y,t,c,p) for x,y,t,c,p in filtered if t!='ref']
 refs=[(x,y,t,c,p) for x,y,t,c,p in filtered if t=='ref']
 swatch=[]
 for y in range(0,12,4):
  vals=collections.Counter(int(v) for v in a[y:y+4,52:64].ravel() if int(v)>=8)
  if vals:
   v,_=vals.most_common(1)[0]
   if v not in swatch:swatch.append(v)
 colors=set(c for x,y,t,c,p in filtered)
 palette=swatch if len(swatch)>=len(colors) else [c for c,k in collections.Counter(c for x,y,t,c,p in nodes).most_common()]+sorted(colors-set(c for x,y,t,c,p in nodes))
 return best,nodes,refs,palette,len(cand),lattice.most_common(4)
def active_group(nodes,refs):
 points={(x,y) for x,y,t,c,p in nodes+refs}
 groups=[]
 while points:
  start=points.pop();group={start};todo=[start]
  while todo:
   x,y=todo.pop()
   for dx in (-8,0,8):
    for dy in (-8,0,8):
     nb=(x+dx,y+dy)
     if nb in points:points.remove(nb);group.add(nb);todo.append(nb)
  groups.append(group)
 if not groups:raise ValueError('no visible sprite groups')
 # The visible start panel may contain a tutorial duplicate. Keep the
 # largest connected reference-and-cell group, breaking ties toward the right.
 chosen=max(groups,key=lambda g:(len(g),max(x for x,y in g),max(y for x,y in g)))
 return ([n for n in nodes if n[:2] in chosen],
         [n for n in refs if n[:2] in chosen])

def discover(observation):
 _,raw_nodes,raw_refs,palette,_,_=parse(observation)
 nodes,refs=active_group(raw_nodes,raw_refs)
 nodes=sorted(nodes,key=lambda n:(n[1],n[0]))
 if not nodes or not refs:raise RuntimeError(('missing visible cells or symbols',len(nodes),len(refs)))
 bypos={(n[0],n[1]):i for i,n in enumerate(nodes)}
 if len(set(palette))!=len(palette):raise RuntimeError('palette duplicated')
 colors={c:i for i,c in enumerate(palette)}
 if any(n[3] not in colors for n in nodes+refs):
  raise RuntimeError(('palette incomplete',palette))
 allowed={i:set(range(len(palette))) for i in range(len(nodes))}
 constrained=set()
 for rx,ry,_,refcolor,pattern in refs:
  for row,line in enumerate(pattern):
   for col,symbol in enumerate(line):
    if row==1 and col==1:continue
    p=(rx+(col-1)*8,ry+(row-1)*8)
    if p not in bypos:continue
    idx=bypos[p];constrained.add(idx)
    valid={colors[refcolor]} if symbol==0 else set(range(len(palette)))-{colors[refcolor]}
    allowed[idx]&=valid
 if any(not allowed[i] for i in constrained):
  raise RuntimeError(('constraint contradiction',[(nodes[i][:2],allowed[i]) for i in constrained if not allowed[i]]))
 effects=[]
 for i,(x,y,t,c,pattern) in enumerate(nodes):
  targets={(x,y)}
  if t=='multi':
   targets|={(x+(col-1)*8,y+(row-1)*8) for row,line in enumerate(pattern) for col,v in enumerate(line) if v==6}
  effects.append({bypos[p] for p in targets if p in bypos})
 return nodes,refs,palette,allowed,constrained,effects

def next_click(nodes,palette,allowed,constrained,effects):
 n=len(nodes);k=len(palette);current=[palette.index(node[3]) for node in nodes]
 if k==2:
  pivot={}
  for i in sorted(constrained):
   opts=allowed[i]
   if len(opts)>1:continue
   rhs=next(iter(opts))^current[i]
   mask=sum(1<<j for j,ee in enumerate(effects) if i in ee)
   while mask:
    p=(mask&-mask).bit_length()-1
    if p in pivot:
     pm,pr=pivot[p];mask^=pm;rhs^=pr
    else:
     pivot[p]=(mask,rhs);break
   if not mask and rhs:raise RuntimeError(('inconsistent binary relations',i))
  def solve(free):
   out=free
   for p in sorted(pivot,reverse=True):
    mask,rhs=pivot[p]
    if rhs^(((mask^(1<<p))&out).bit_count()%2):out|=1<<p
    else:out&=~(1<<p)
   return out
  particular=solve(0)
  freecolumns=[i for i in range(n) if i not in pivot]
  basis=[solve(1<<i)^particular for i in freecolumns]
  best=particular
  if len(basis)<17:
   bits=particular;prev=0
   for val in range(1,1<<len(basis)):
    gray=val^(val>>1);bit=(gray^prev).bit_length()-1
    bits^=basis[bit];prev=gray
    if bits.bit_count()<best.bit_count():best=bits
  else:
   improved=True
   while improved:
    improved=False
    for z in basis:
     if (best^z).bit_count()<best.bit_count():best^=z;improved=True
  if not best:return None
  i=(best&-best).bit_length()-1
  return (nodes[i][0],nodes[i][1],effects[i],n,k)
 # For multicolor levels with single-cell operators, choose the
 # shortest forward cycle into any allowed color.
 if any(len(e)!=1 or i not in e for i,e in enumerate(effects)):
  raise RuntimeError('multicolor coupled operator not learned')
 steps=[]
 for i in sorted(constrained):
  distance=min((goal-current[i])%k for goal in allowed[i])
  if distance:steps.append((distance,i))
 if not steps:return None
 _,i=min(steps)
 return (nodes[i][0],nodes[i][1],effects[i],n,k)

class VisibleCausalPolicy(Agent):
 MAX_ACTIONS=175
 def __init__(self,*args,**kwargs):
  super().__init__(*args,**kwargs)
  self.moves=0;self.failures=[];self.checks=0;self.levels_seen=set();self.last=None
 def is_done(self,frames,latest_frame):
  return latest_frame.state is GameState.WIN or len(self.failures)>0
 def choose_action(self,frames,latest_frame):
  try:
   nodes,refs,palette,allowed,constrained,effects=discover(latest_frame)
   if self.last is not None and self.last[0]==latest_frame.levels_completed:
    _,oldcolors,affected,oldpalette=self.last
    newcolors={n[:2]:n[3] for n in nodes}
    if newcolors.keys()!=oldcolors.keys():raise RuntimeError('sprite positions changed within level')
    predicted={p:(oldpalette[(oldpalette.index(c)+1)%len(oldpalette)] if p in affected else c) for p,c in oldcolors.items()}
    if newcolors!=predicted:raise RuntimeError(('click-effect prediction failed',[(p,predicted[p],newcolors[p]) for p in newcolors if predicted[p]!=newcolors[p]][:5]))
    self.checks+=1
   if latest_frame.levels_completed not in self.levels_seen:
    print('LIVE_DISCOVERY','LEVEL',latest_frame.levels_completed+1,'NODES',len(nodes),'REFS',len(refs),'PALETTE',palette,'CONSTRAINED',len(constrained),'MULTI',sum(n[2]=='multi' for n in nodes),flush=True)
    self.levels_seen.add(latest_frame.levels_completed)
   choice=next_click(nodes,palette,allowed,constrained,effects)
   if choice is None:
    raise RuntimeError(('constraints satisfied but level still active',latest_frame.levels_completed))
   x,y,affected,n,k=choice
   self.last=(latest_frame.levels_completed,{q[:2]:q[3] for q in nodes},{nodes[i][:2] for i in affected},palette)
   a=GameAction.ACTION6;a.set_data({'x':x,'y':y});self.moves+=1
   return a
  except Exception as exc:
   self.failures.append(str(exc))
   print('POLICY_FAILURE',self.moves,str(exc),flush=True)
   return GameAction.ACTION5

logging.disable(logging.CRITICAL)
for trial in (0,1):
 arc=Arcade(operation_mode=OperationMode.NORMAL);env=arc.make('ft09')
 agent=VisibleCausalPolicy(card_id='scratch',game_id='ft09',agent_name='ft09-visible-causal-policy',ROOT_URL='http://localhost',record=False,arc_env=env)
 agent.main()
 result=agent.frames[-1]
 print('VISIBLE_AGENT_RESULT','TRIAL',trial,'ACTIONS',agent.moves,'VALIDATED_EFFECTS',agent.checks,'LEVELS',result.levels_completed,'STATE',result.state.name,'SCORE',arc.get_scorecard().score,'ERRORS',agent.failures,flush=True)
