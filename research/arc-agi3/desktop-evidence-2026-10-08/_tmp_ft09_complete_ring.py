from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np,hashlib
arc=Arcade(operation_mode=OperationMode.NORMAL);e=arc.make('ft09')
centers=[(x,y) for y in (36,44,52) for x in (36,44,52) if (x,y)!=(44,44)]
for i,(x,y) in enumerate(centers,1):
 r=e.step(GameAction.ACTION6,data={'x':x,'y':y})
 board=np.asarray(r.frame[-1],dtype=np.int16)
 print('CLICK',i,x,y,'LEVELS',r.levels_completed,'STATE',r.state.name,'COLORS',[(cx,cy,int(board[cy,cx])) for cx,cy in centers],'SHA',hashlib.sha1(board.tobytes()).hexdigest()[:10],flush=True)
 if r.levels_completed or r.state.name!='NOT_FINISHED':break
