from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from generator_explanation_kernel import lattice_involutions,support

FIRST=[3]*5+[2]*10
def shape_cells(s):
 return {(dx,dy) for dy,row in enumerate(s.pixels) for dx,v in enumerate(row) if int(v)>=0}
def legal_positions(shape,W,H):
 maxx=max(x for x,y in shape);maxy=max(y for x,y in shape)
 return [(x,y) for x in range(0,W-maxx) for y in range(0,H-maxy)]

for label,prefix in [("L1",[]),("L2",FIRST)]:
 a=Arcade(operation_mode=OperationMode.NORMAL);e=a.make('ar25');r=None
 for z in prefix:r=e.step(GameAction.from_id(z),data={})
 g=e._game;T={(t.x,t.y) for t in g.fswikrcrdmx};s=g.ouurgkpbbjj[0]
 shape=shape_cells(s);W,H=g.dqwpuqcubca,g.height
 pos=legal_positions(shape,W,H)
 gens=lattice_involutions(W,H,margin=0)
 best=[]
 for gen in gens:
  for at in pos:
   S=support(shape,at,[gen],W,H)
   if T<=S:
    extras=len(S-T);move=abs(at[0]-s.x)+abs(at[1]-s.y)
    best.append((extras,move,gen.name,gen.b1,gen.b2,at,len(S)))
 best.sort()
 print(label,"LEGAL_EXPLANATIONS",len(best),flush=True)
 for row in best[:30]:print(" ",row,flush=True)
