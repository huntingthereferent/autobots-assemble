from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy

L1=[3]*5+[2]*10

def occxy(g):
    b=g.naxbskjmlg()
    return {(x,y) for y in range(g.height) for x in range(g.dqwpuqcubca) if int(b[y,x])>=0}

def comps(S):
    S=set(S);out=[]
    while S:
        q=[S.pop()];c=set(q)
        while q:
            x,y=q.pop()
            for n in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
                if n in S:S.remove(n);c.add(n);q.append(n)
        out.append(c)
    return sorted(out,key=lambda c:(min(x for x,y in c),min(y for x,y in c),len(c)))

def sig(c):
    xs=[x for x,y in c];ys=[y for x,y in c]
    return (len(c),min(xs),max(xs),min(ys),max(ys),sum(xs)/len(xs),sum(ys)/len(ys))

def select(e,idx):
    g=e._game;cur=-1 if g.yvifanjrcyu not in g.ayyvxqrhnzw else g.ayyvxqrhnzw.index(g.yvifanjrcyu)
    for _ in range((idx-cur)%len(g.ayyvxqrhnzw)):e.step(GameAction.from_id(5),data={})

a=Arcade(operation_mode=OperationMode.NORMAL);root=a.make('ar25');r=None
for z in L1:r=root.step(GameAction.from_id(z),data={})
print("BASE",[(i,s.x,s.y) for i,s in enumerate(root._game.ayyvxqrhnzw)])
for idx in [0,1]:
    e=copy.deepcopy(root);select(e,idx)
    before=comps(occxy(e._game))
    print("\nOBJ",idx,"BEFORE",[sig(c) for c in before])
    for act in [3,4]:
        ee=copy.deepcopy(e)
        p0=[(s.x,s.y) for s in ee._game.ayyvxqrhnzw]
        ee.step(GameAction.from_id(act),data={})
        p1=[(s.x,s.y) for s in ee._game.ayyvxqrhnzw]
        after=comps(occxy(ee._game))
        print(" ACT",act,"DIRECT",(p1[idx][0]-p0[idx][0],p1[idx][1]-p0[idx][1]),"AFTER",[sig(c) for c in after])
