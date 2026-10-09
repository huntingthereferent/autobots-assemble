from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy
root=Arcade(operation_mode=OperationMode.NORMAL).make('ft09')
prefix=((36,36),(36,44),(36,52),(52,44))
for xy in prefix:root.step(GameAction.ACTION6,data={'x':xy[0],'y':xy[1]})
g=root._game
print('L',g.level_index+1,'BUDGET',g.lpw.dzy,'COLORS',g.gqb,'IRW',g.irw,'TARGET_SPRITES',len(g.gig),'Hkx',len(g.fhc),'NTi',len(g.mou),flush=True)
nodes=sorted(g.fhc+g.mou,key=lambda s:(s.y,s.x))
before={(s.x,s.y):int(s.pixels[1,1]) for s in nodes}
for s in nodes:
 q=copy.deepcopy(root)
 rr=q.step(GameAction.ACTION6,data={'x':int(s.x*2),'y':int(s.y*2)})
 gg=q._game
 changes=[(ss.x,ss.y,int(ss.pixels[1,1])) for ss in gg.fhc+gg.mou if (ss.x,ss.y) in before and int(ss.pixels[1,1])!=before[(ss.x,ss.y)]]
 print('ACTION',(s.name,s.x,s.y),'CHANGES',changes,'LV',rr.levels_completed,flush=True)
for c in g.gig:
 print('CONSTRAINT',(c.name,c.x,c.y),'SHAPE',c.pixels.tolist(),flush=True)
