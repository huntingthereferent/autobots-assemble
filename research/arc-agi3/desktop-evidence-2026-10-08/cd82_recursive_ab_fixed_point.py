"""Recursive A/B closure on a bounded CD82 public state tree.

Start with public referent + one-step continuation equivalence.
Then repeatedly A/B the synthesized classes against successor classes until stable.
"""
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np,hashlib,copy
from collections import defaultdict

def fh(r):
    if not getattr(r,"frame",None):return "EMPTY"
    return hashlib.sha1(np.array(r.frame[0],dtype=np.int16).tobytes()).hexdigest()[:12]

a=Arcade(operation_mode=OperationMode.NORMAL)
root=a.make("cd82")

# Build a bounded deterministic tree, retaining child path links.
nodes={}  # path -> {obs, immediate, children}
front=[((),root,"START")]
MAX_DEPTH=5
CAP=80
for depth in range(MAX_DEPTH):
    nxt=[]
    for path,env,obs in front:
        immediate=[]
        children={}
        for z in [1,2,3,4,5]:
            q=copy.deepcopy(env)
            try:
                r=q.step(GameAction.from_id(z),data={})
                no=fh(r)
                immediate.append((z,no,r.levels_completed,r.state.name))
                if r.state.name=="NOT_FINISHED":
                    cp=path+(z,)
                    children[z]=cp
                    nxt.append((cp,q,no))
            except Exception as ex:
                immediate.append((z,"ERR",type(ex).__name__,None))
        nodes[path]={"obs":obs,"immediate":tuple(immediate),"children":children,"depth":depth}
    front=nxt[:CAP]

print("NODES",len(nodes))

# Initial A/B classes: current public referent + equality of immediate continuation vector.
def renumber(keys):
    table={}
    out={}
    for p,k in keys.items():
        if k not in table:table[k]=len(table)
        out[p]=table[k]
    return out

cls=renumber({p:(n["obs"],n["immediate"]) for p,n in nodes.items()})
print("ROUND",0,"CLASSES",len(set(cls.values())))

# Recursively feed A/B outputs back in.  A state's next witness includes the
# action-labelled successor A/B class when that child is inside the tree.
rounds=0
while True:
    keys={}
    for p,n in nodes.items():
        succ=[]
        for z,no,lc,st in n["immediate"]:
            cp=n["children"].get(z)
            successor=cls.get(cp,("boundary",no,lc,st))
            succ.append((z,no,lc,st,successor))
        keys[p]=(n["obs"],tuple(succ))
    new=renumber(keys)
    rounds+=1
    changed=sum(new[p]!=cls[p] for p in nodes)
    print("ROUND",rounds,"CLASSES",len(set(new.values())),"CHANGED_IDS",changed)
    # Compare partitions, not arbitrary numeric class IDs.
    def partition(c):
        b=defaultdict(list)
        for p,v in c.items():b[v].append(p)
        return frozenset(frozenset(x) for x in b.values())
    if partition(new)==partition(cls):
        cls=new
        break
    cls=new
    if rounds>10:raise RuntimeError("no fixed point")

# Find public observations that required recursive splits beyond immediate one-step class.
initial=renumber({p:(n["obs"],n["immediate"]) for p,n in nodes.items()})
def blocks_by_obs(c):
    out=defaultdict(set)
    for p,n in nodes.items():out[n["obs"]].add(c[p])
    return out
iobs=blocks_by_obs(initial);fobs=blocks_by_obs(cls)
deep=[]
for obs in sorted(set(iobs)|set(fobs)):
    if len(fobs[obs])>len(iobs[obs]):
        deep.append((obs,len(iobs[obs]),len(fobs[obs])))
print("DEEPER_SPLITS",deep)
print("FIXED_POINT_ROUNDS",rounds)
print("PASS recursive A/B synthesized-state closure on CD82")
