from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np,hashlib,copy
from ab_recursive_partition import ab_fixed_point

ACTIONS=[1,2,3,4,5,7]

def fh(r):
 if not getattr(r,"frame",None):return "EMPTY"
 return hashlib.sha1(np.array(r.frame[0],dtype=np.int16).tobytes()).hexdigest()[:12]

a=Arcade(operation_mode=OperationMode.NORMAL);root=a.make("ar25")
nodes={};front=[((),root,"START")]
for dep in range(4):
 nxt=[]
 for path,env,obs in front:
  imm=[];children={}
  for z in ACTIONS:
   q=copy.deepcopy(env)
   try:
    r=q.step(GameAction.from_id(z),data={});no=fh(r)
    imm.append((z,no,r.levels_completed,r.state.name))
    if r.state.name=="NOT_FINISHED":
     cp=path+(z,);children[z]=cp;nxt.append((cp,q,no))
   except Exception as ex:imm.append((z,"ERR",type(ex).__name__,None))
  nodes[path]={"obs":obs,"immediate":tuple(imm),"children":children}
 front=nxt[:50]

classes,h=ab_fixed_point(nodes)
print("NODES",len(nodes))
print("A/B_CLASSES",[len(p) for p in h],"ROUNDS",len(h)-1)

# How many raw public observations split into multiple final A/B states?
from collections import defaultdict
raw=defaultdict(set)
for p,n in nodes.items():raw[n["obs"]].add(classes[p])
split={o:s for o,s in raw.items() if len(s)>1}
print("RAW_OBS",len(raw),"SPLIT_OBS",len(split))
for o,s in list(split.items())[:20]:print(" ",o,"=>",len(s))

# Inspect the most strongly split public referent.
target=max(split,key=lambda o:len(split[o]))
members=[p for p,n in nodes.items() if n["obs"]==target]
print("TARGET",target,"N",len(members),"AB_CLASSES",len(split[target]))
byclass=defaultdict(list)
for p in members:byclass[classes[p]].append(p)
for k,paths in byclass.items():
 print(" CLASS",k,"PATHS",paths)
 for p in paths[:3]:
  print("  ",p,"FUTURE",nodes[p]["immediate"])

# On this target, the A/B quotient must match the action-7 continuation quotient.
def a7hash(p):
 return next(no for z,no,lc,st in nodes[p]["immediate"] if z==7)
class_partition=frozenset(frozenset(v) for v in byclass.values())
a7groups=defaultdict(list)
for p in members:a7groups[a7hash(p)].append(p)
a7_partition=frozenset(frozenset(v) for v in a7groups.values())
print("A7_GROUPS",dict(a7groups))
print("AB_EQUALS_A7",class_partition==a7_partition)
assert class_partition==a7_partition

# Across every split public observation, identify which actions actually vary.
print("SPLIT_ACTION_CAUSES")
cause_counts=defaultdict(int)
for obs,state_ids in split.items():
 ms=[p for p,n in nodes.items() if n["obs"]==obs]
 varying=[]
 for z in ACTIONS:
  sigs=set()
  for p in ms:
   item=next(x for x in nodes[p]["immediate"] if x[0]==z)
   sigs.add(item[1:])
  if len(sigs)>1:varying.append(z)
 cause_counts[tuple(varying)]+=1
 print(" ",obs,"N",len(ms),"AB",len(state_ids),"VARY",varying)
print("CAUSE_COUNTS",dict(cause_counts))

# For recursively split observations with identical one-step futures, find the
# shortest action suffix whose witnessed outcome differs.
def distinguish(p,q,seen=None):
 if p not in nodes or q not in nodes:return None
 if seen is None:seen=set()
 if (p,q) in seen:return None
 seen.add((p,q))
 np,nq=nodes[p],nodes[q]
 # Direct response difference.
 for z in ACTIONS:
  ap=next(x for x in np["immediate"] if x[0]==z)
  aq=next(x for x in nq["immediate"] if x[0]==z)
  if ap[1:]!=aq[1:]:
   return (z,)
 # Recurse only through children witnessed on both sides.
 best=None
 for z in ACTIONS:
  cp=np["children"].get(z);cq=nq["children"].get(z)
  if cp is None or cq is None:continue
  tail=distinguish(cp,cq,seen)
  if tail is not None:
   cand=(z,)+tail
   if best is None or len(cand)<len(best):best=cand
 return best

print("DELAYED_WITNESSES")
for obs,state_ids in split.items():
 ms=[p for p,n in nodes.items() if n["obs"]==obs]
 varying=[]
 for z in ACTIONS:
  sigs={next(x for x in nodes[p]["immediate"] if x[0]==z)[1:] for p in ms}
  if len(sigs)>1:varying.append(z)
 if varying:continue
 # pick two members belonging to different final A/B classes.
 pair=None
 for i,p in enumerate(ms):
  for q in ms[i+1:]:
   if classes[p]!=classes[q]:pair=(p,q);break
  if pair:break
 if pair:
  suf=distinguish(*pair)
  print(" ",obs,pair,"=>",suf)

print("PASS AR25 through generic recursive A/B public-state closure")
