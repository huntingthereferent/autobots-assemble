from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy

PRE5=[3,3,3,3,3,2,2,2,2,2,2,2,2,2,2,3,3,5,2,2,2,2,2,2,2,2,1,1,1,1,1,1,1,5,4,4,4,4,4,4,4,2,2,2,2,2,2,2,5,3,3,3,3,3,3,3,3,3,3,3,3,2,2,2,2,2,2,2,2,2,2,2,5,4,4,4,4,4,4,4,5,4,4,4,4,4,4,4]

def occ(g):
 b=g.naxbskjmlg()
 return tuple(tuple(int(v) for v in row) for row in b)

def select(e,idx):
 g=e._game;cur=-1 if g.yvifanjrcyu not in g.ayyvxqrhnzw else g.ayyvxqrhnzw.index(g.yvifanjrcyu)
 for _ in range((idx-cur)%len(g.ayyvxqrhnzw)):e.step(GameAction.from_id(5),data={})

def act_on(e,idx,act):
 select(e,idx);e.step(GameAction.from_id(act),data={})

a=Arcade(operation_mode=OperationMode.NORMAL);root=a.make('ar25')
for z in PRE5:root.step(GameAction.from_id(z),data={})

# Discovered causally: object 1 responds on x; object 0 responds on y.
xy=copy.deepcopy(root)
act_on(xy,1,4)  # x-control +1
act_on(xy,0,2)  # y-control +1

yx=copy.deepcopy(root)
act_on(yx,0,2)
act_on(yx,1,4)

print("XY_POS",[(s.x,s.y) for s in xy._game.ayyvxqrhnzw])
print("YX_POS",[(s.x,s.y) for s in yx._game.ayyvxqrhnzw])
print("OCC_EQUAL",occ(xy._game)==occ(yx._game))
assert occ(xy._game)==occ(yx._game)
print("PASS observational commutation of discovered x/y operators")
