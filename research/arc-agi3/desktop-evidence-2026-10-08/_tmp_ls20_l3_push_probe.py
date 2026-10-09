from arc_agi import Arcade,OperationMode
from arcengine import GameAction
p1=(3,3,3,1,1,1,1,4,4,4,1,1,1)
p2=(1,4,1,1,1,1,1,4,4,2,4,2,2,2,2,2,2,1,2,2,3,3,4,1,4,1,1,1,1,1,1,1,3,3,3,3,3,3,2,3,2,2,2,2,2)
p3=(1,1,1,1,1,1,1,1,4,4,4,4,2,2,2,2,2,3,3,4,4,2,2,2,1)
e=Arcade(operation_mode=OperationMode.NORMAL).make('ls20')
for a in p1+p2:e.step(GameAction.from_id(a),data={})
g=e._game
W={(s.x,s.y) for s in g.current_level.get_sprites_by_tag('ihdgageizm')}
P={(s.x-1,s.y-1) for s in g.current_level.get_sprites_by_tag('npxgalaybz')}
G={(s.x,s.y) for s in g.current_level.get_sprites_by_tag('rjlbuycveu')}
R={(s.x,s.y) for s in g.current_level.get_sprites_by_tag('rhsxkxzdjz')}
S={(s.x,s.y) for s in g.current_level.get_sprites_by_tag('soyhouuebz')}
print('GRID: # wall . floor P refill G goal R rot C color',flush=True)
for y in range(5,55,5):
 out=''
 for x in range(9,59,5):
  pos=(x,y);out+='#' if pos in W else 'P' if pos in P else 'G' if pos in G else 'R' if pos in R else 'C' if pos in S else '.'
 print(y,out,flush=True)
print('PUSHERS',[(q.sprite.x,q.sprite.y,q.dx,q.dy,q.width,q.height,q.start_x,q.start_y) for q in g.hasivfwip],flush=True)
for i,a in enumerate(p3,1):
 h=e._game
 bef=(h.gudziatsk.x,h.gudziatsk.y,h._step_counter_ui.current_steps,len(h.euemavvxz))
 r=e.step(GameAction.from_id(a),data={})
 h=e._game
 print('MOVE',i,a,bef,'=>',(h.gudziatsk.x,h.gudziatsk.y,h._step_counter_ui.current_steps,len(h.euemavvxz)),'STATE',r.state.name,flush=True)
