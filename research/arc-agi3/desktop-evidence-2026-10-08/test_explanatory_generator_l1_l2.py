from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from generator_explanation_kernel import lattice_involutions,support

FIRST=[3]*5+[2]*10

def shape_cells(s):
 return {(dx,dy) for dy,row in enumerate(s.pixels) for dx,v in enumerate(row) if int(v)>=0}

for label,prefix in [("L1",[]),("L2",FIRST)]:
 a=Arcade(operation_mode=OperationMode.NORMAL)
 e=a.make('ar25');r=None
 for z in prefix:r=e.step(GameAction.from_id(z),data={})
 g=e._game;T={(t.x,t.y) for t in g.fswikrcrdmx};s=g.ouurgkpbbjj[0]
 shape=shape_cells(s);W,H=g.dqwpuqcubca,g.height
 gens=lattice_involutions(W,H,margin=2)
 best=[]
 for gen in gens:
  for x in range(-5,W+5):
   for y in range(-5,H+5):
    S=support(shape,(x,y),[gen],W,H)
    if T<=S:
     extras=len(S-T)
     move=abs(x-s.x)+abs(y-s.y)
     best.append((extras,move,gen.name,gen.b1,gen.b2,(x,y),len(S)))
 best.sort()
 print(label,"EXPLANATIONS",len(best))
 for row in best[:20]:print(" ",row)
