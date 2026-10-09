from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy,collections
root=Arcade(operation_mode=OperationMode.NORMAL).make('sk48')
paths=[(1,2,1),(1,2,1,2,1),(1,2,1,2,1,2,1),(2,2,1)]
for p in paths:
 e=copy.deepcopy(root)
 for a in p:e.step(GameAction.from_id(a),data={})
 g=e._game
 rec=[tuple((int(x),int(y),int(n)) for _,x,y,n in f) for f in g.seghobzez]
 # reversible dictionary compression: identical records retained once, with references
 symbols=[];dictionary=[]
 for f in rec:
  if f not in dictionary:dictionary.append(f)
  symbols.append(dictionary.index(f))
 print('PATH',p,'Q',g.qiercdohl,'DEPTH',len(rec),'DISTINCT',len(dictionary),'SYMBOLS',symbols,'ACTIVE',g.vzvypfsnt.y,flush=True)
 actual=[]
 for i in range(len(rec)+2):
  actual.append((int(e._game.vzvypfsnt.y),len(e._game.seghobzez)))
  e.step(GameAction.ACTION7,data={})
 predicted=[]
 for i in range(len(rec)+2):
  idx=max(1,len(symbols)-i)-1
  predicted.append((dictionary[symbols[idx]][0][1],max(1,len(symbols)-i)))
 print('ACTUAL',actual,'PREDICTED',predicted,'MATCH',actual==predicted,flush=True)
