from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np

def learned_apply(A):
    # Discovered from graph-isomorphism continuity:
    # output(r',c') receives input(r,c) at r'=c, c'=H-1-r.
    H,W=A.shape
    B=np.empty((W,H),dtype=A.dtype)
    for r in range(H):
        for c in range(W):
            B[c,H-1-r]=A[r,c]
    return B

a=Arcade(operation_mode=OperationMode.NORMAL)
e=a.make("cn04")
sp=list(e._game.current_level.get_sprites())
obj1=sp[1]
A=np.array(obj1.render(),dtype=int)
P=learned_apply(A)
print("OBJECT1_BEFORE",A.shape);print(A)
print("PREDICTED",P.shape);print(P)

# Select object 1 through the public click action discovered by probing.
e.step(GameAction.from_id(6),data={"x":41,"y":31})
sp=list(e._game.current_level.get_sprites())
sel=sp.index(e._game.xseexqzst) if e._game.xseexqzst in sp else -1
print("SELECTED",sel)
assert sel==1

e.step(GameAction.from_id(5),data={})
B=np.array(e._game.xseexqzst.render(),dtype=int)
print("OBSERVED",B.shape);print(B)
print("MATCH",np.array_equal(P,B))
assert np.array_equal(P,B)
print("PASS learned order-4 operator transfers to unseen object")
