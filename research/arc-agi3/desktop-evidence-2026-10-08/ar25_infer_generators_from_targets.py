from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from involution_discovery_kernel import candidate_involutions,orbit,clipped

# Known full solve only to reach each level state; transform inference itself sees
# only target points + payload cell geometry.
SOL=[3]*5+[2]*10+[3,3]+[5]+[2]*8
# use proven full path from promoted solver output
FULL=[3,3,3,3,3,2,2,2,2,2,2,2,2,2,2,3,3,5,2,2,2,2,2,2,2,2,1,1,1,1,1,1,1,5,4,4,4,4,4,4,4,2,2,2,2,2,2,2,5,3,3,3,3,3,3,3,3,3,3,3,3,2,2,2,2,2,2,2,2,2,2,2,5,4,4,4,4,4,4,4,5,4,4,4,4,4,4,4,5,4,4,4,4,4,5,5,2,2,2,2,5,5,3,3,3,3,3,3,3,3,3,3,1,1,1,1,1,1,1,5,3,5,5,5,2,2,2,2,2,2,2,2,2,2,2,5,5,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,2,2,2,2,5,3,3,3,3,3,3,3,2,2,2,2,2,2,2,2,2,2,2,2,5,4,4,4,4,4,4,4,4,4,5,5,5,2,2,5,5,3,3,1,1,1,1,1,1,1,1,1,1,1,1,5,4,4,4,1,1,1,1,1,1,5,4,4,4,4,4,4,4,4,4,5,5,5,2,2,2,2,2,2,5,5,3,3,3,3,3,3,3,3,3,1,1,1,1,1,1,1,5,4,4,4,4,4,4,4,4,4,1,1,1,1]

a=Arcade(operation_mode=OperationMode.NORMAL)
e=a.make('ar25');r=None
starts={0:0}
prev=0
for i,z in enumerate(FULL):
    r=e.step(GameAction.from_id(z),data={})
    if r.levels_completed!=prev:
        starts[r.levels_completed]=i+1
        prev=r.levels_completed

def shape_cells(s):
    return {(dx,dy) for dy,row in enumerate(s.pixels) for dx,v in enumerate(row) if int(v)>=0}

def translated(shape,xy):
    x,y=xy
    return {(x+dx,y+dy) for dx,dy in shape}

# Search candidate transforms that explain target duplication for each level.
for lev in range(8):
    e=a.make('ar25');r=None
    for z in FULL[:starts[lev]]:
        r=e.step(GameAction.from_id(z),data={})
    g=e._game
    T={(t.x,t.y) for t in g.fswikrcrdmx}
    payloads=list(g.ouurgkpbbjj)
    # infer candidate involutions from the target itself
    cands=candidate_involutions(T)
    scored=[]
    for f in cands:
        # score how much of T maps back into T under f
        inside=sum(1 for p in T if f(p) in T)
        scored.append((inside,len(T),f))
    scored.sort(key=lambda x:(-x[0],x[2].name,x[2].b1,x[2].b2))
    top=scored[:12]
    print("LEVEL",lev+1,"TARGETS",len(T),"CANDS",len(cands))
    for inside,n,f in top:
        if inside>=max(2,n//2):
            print(" ",inside,"/",n,f)
