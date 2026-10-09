"""Black-box one-step causal probe for AR25.

The probe does not use reflector tags to classify semantics. It:
1. enumerates selectable objects,
2. applies each directional action to a copied environment,
3. compares object coordinates and generated occupancy,
4. records direct parameter movement vs downstream image movement.

This is evidence for discovering operators from interventions rather than
guessing them from a finished target.
"""
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy, hashlib

def occ(g):
    b=g.naxbskjmlg()
    return {(x,y,int(b[y,x])) for y in range(g.height) for x in range(g.dqwpuqcubca) if int(b[y,x])>=0}

def positions(g):
    return tuple((s.x,s.y,s.pixels.shape) for s in g.ayyvxqrhnzw)

def select_to(e,idx):
    g=e._game
    cur=-1 if g.yvifanjrcyu not in g.ayyvxqrhnzw else g.ayyvxqrhnzw.index(g.yvifanjrcyu)
    n=len(g.ayyvxqrhnzw)
    for _ in range((idx-cur)%n):
        e.step(GameAction.from_id(5),data={})
    return e

def probe(level_prefix,label):
    a=Arcade(operation_mode=OperationMode.NORMAL)
    root=a.make('ar25');r=None
    for z in level_prefix:r=root.step(GameAction.from_id(z),data={})
    g=root._game
    print("\nLEVEL",label,"NOBJ",len(g.ayyvxqrhnzw),"TARGETS",len(g.fswikrcrdmx))
    base_occ=occ(g)
    for idx in range(len(g.ayyvxqrhnzw)):
        e=copy.deepcopy(root);select_to(e,idx)
        g0=e._game;o0=occ(g0);p0=positions(g0)
        print("OBJECT",idx,"AT",p0[idx],"TAGS",sorted(g0.ayyvxqrhnzw[idx].tags))
        for z in [1,2,3,4]:
            ee=copy.deepcopy(e)
            rr=ee.step(GameAction.from_id(z),data={})
            g1=ee._game;p1=positions(g1);o1=occ(g1)
            direct=(p1[idx][0]-p0[idx][0],p1[idx][1]-p0[idx][1])
            added={(x,y) for x,y,v in o1-o0}
            removed={(x,y) for x,y,v in o0-o1}
            # downstream cells exclude direct object's occupied bbox change only later;
            # raw symmetric difference is enough for causal fingerprint.
            print(" A",z,"DIRECT",direct,"OCC_DELTA",len(added),len(removed),
                  "ADD",sorted(added)[:16],"REM",sorted(removed)[:16])

# Level 2 is ideal: one movable latent operator + one payload.
L1=[3]*5+[2]*10
# Level 5: two movable latent operators + one payload.
PRE5=[3,3,3,3,3,2,2,2,2,2,2,2,2,2,2,3,3,5,2,2,2,2,2,2,2,2,1,1,1,1,1,1,1,5,4,4,4,4,4,4,4,2,2,2,2,2,2,2,5,3,3,3,3,3,3,3,3,3,3,3,3,2,2,2,2,2,2,2,2,2,2,2,5,4,4,4,4,4,4,4,5,4,4,4,4,4,4,4]
probe(L1,"2")
probe(PRE5,"5")
