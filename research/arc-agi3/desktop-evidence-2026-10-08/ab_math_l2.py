# ARC adapter audit: expose only board-native directed relations; do not choose a next action.
# This is intentionally an evidence construction, not a solver.
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np, sys
sys.path.insert(0,r'E:\axioms\experiment2')
from two_step import ab
a=Arcade(operation_mode=OperationMode.NORMAL); e=a.make('ar25')
for i in [3]*5+[2]*10: o=e.step(GameAction.from_id(i),data={})
b=o.frame[0]
# Native lattice witnesses from the whole returned board: corresponding black/navy marks.
L=[(4,46),(7,46),(10,46),(10,49),(10,52)]
R=[(58,46),(55,46),(52,46),(52,49),(52,52)] # horizontal reflection correspondence
nodes={}; rel={}
# Value is signed x coordinate relative to divider center x=31. Same board coordinate quantity for both sides.
for j,(p,q) in enumerate(zip(L,R)):
 for side,(x,y) in [('L',p),('R',q)]:
  k=f'{side}{j}'; nodes[k]={'type':'source','value':x-31,'source':f'ar25:L2:pixel:{x},{y}'}
 rel[f'm{j}']={'negative':f'L{j}','positive':f'R{j}','kind':'mirror','orientation':'0->1'}
x={'nodes':nodes,'source_relations':rel,'current':list(nodes),'history':[],'outcome':'INPUT_EVIDENCE'}
x1=ab(x); x2=ab(x1)
print('X1',[(x1['nodes'][k]['value'],x1['nodes'][k]['support']['kind']) for k in x1['current']])
print('X1 outcome',x1['outcome'],'count',len(x1['current']))
print('X2 values',[x2['nodes'][k]['value'] for k in x2['current']])
print('X2 outcome',x2['outcome'],'count',len(x2['current']))
