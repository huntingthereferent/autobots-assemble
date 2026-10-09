from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy
a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
MEET=[2,2,2,1,1]
base=a.make('ar25');r0=None
for z in SOL+MEET:r0=base.step(GameAction.from_id(z),data={})
def run(w):
 e=copy.deepcopy(base);r=r0
 for z in w:r=e.step(GameAction.from_id(z),data={})
 return e,r
def summary(w):
 e,r=run(w);g=e._game
 sel=-1 if g.yvifanjrcyu not in g.ayyvxqrhnzw else g.ayyvxqrhnzw.index(g.yvifanjrcyu)
 stack=[(tuple(s["ouurgkpbbjj"]),tuple(s["jtkyjqznbnp"])) for s in g.flqblmrxsla]
 return {
  "word":w,
  "frame":hash(r.frame[0].tobytes()),
  "sel":sel,
  "stack_len":len(stack),
  "stack_tail_hash":[hash(repr(s)) for s in stack[-3:]],
  "xuk":g.xukxeewuexo,
  "xjw":g.xjwpeqpcxav,
  "qeh":g.qehjebksqcm,
  "huj":g.hujpxmlafgh,
  "level":g.level_index,
 }
for w in [(),(2,),(1,7,7),(7,2,7),(7,7),(2,7),(5,),(5,5),(5,5,5)]:
 print(summary(w))
