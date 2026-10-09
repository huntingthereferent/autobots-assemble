from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy
P1=(3,3,3,1,1,1,1,4,4,4,1,1,1)
P2=(1,4,1,1,1,1,1,4,4,2,4,2,2,2,2,2,2,1,2,2,3,3,4,1,4,1,1,1,1,1,1,1,3,3,3,3,3,3,2,3,2,2,2,2,2)
e=Arcade(operation_mode=OperationMode.NORMAL).make('ls20')
for a in P1+P2:e.step(GameAction.from_id(a),data={})
g=e._game
for p in g.hasivfwip:
 print('PUSHER',p.sprite.x,p.sprite.y,'STEP',p.dx,p.dy,'MAX_PUSH_CELLS',p.ullzqnksoj(g.gudziatsk),'TARGET',(p.start_x+p.dx*p.width*p.ullzqnksoj(g.gudziatsk),p.start_y+p.dy*p.height*p.ullzqnksoj(g.gudziatsk)),flush=True)
wall={(s.x,s.y) for s in g.current_level.get_sprites_by_tag('ihdgageizm')}
for test in [(54,35),(54,40),(54,45),(49,50),(54,50),(59,50),(54,55)]:
 print('TILE',test,'WALL',test in wall,'GOAL',any((s.x,s.y)==test for s in g.plrpelhym),flush=True)
for x,y,a in [(54,30,2),(49,50,4),(54,45,2),(54,5,2),(9,10,1),(14,45,2)]:
 q=copy.deepcopy(e);q._game.gudziatsk.set_position(x,y)
 r=q.step(GameAction.from_id(a),data={});v=q._game
 print('HYPOTHETICAL',x,y,a,'NEXT',(v.gudziatsk.x,v.gudziatsk.y),'ANIM',len(v.euemavvxz),'LEVEL',r.levels_completed,'STATE',r.state.name,flush=True)
