from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np,hashlib,copy
arc=Arcade(operation_mode=OperationMode.NORMAL);root=arc.make('ft09')
def frame(e):return np.asarray(e._last_response.frame[-1],dtype=np.int16).copy()
ref=copy.deepcopy(root);ref.step(GameAction.ACTION6,data={'x':0,'y':0});baseline=frame(ref)
board_slice=np.s_[32:57,32:57]
centers=[(x,y) for y in (36,44,52) for x in (36,44,52)]
for x,y in centers:
 e=copy.deepcopy(root);r=e.step(GameAction.ACTION6,data={'x':x,'y':y})
 cur=frame(e);pixels=np.argwhere(cur!=baseline)
 bb=cur[board_slice]
 print('CLICK',x,y,'DELTA',len(pixels),'BBHASH',hashlib.sha1(bb.tobytes()).hexdigest()[:12],'OUTPUT',r.levels_completed,r.state.name,'CHANGED_COORDS',[(int(q[1]),int(q[0]),int(cur[q[0],q[1]])) for q in pixels[:16]],flush=True)
print('INITIAL_BOARD_SAMPLE')
base=frame(root)
for y in range(28,60,2):
 print(f'{y:02d} ',''.join('0123456789ABCDEF'[int(base[y,x])%16] for x in range(28,60,2)),flush=True)
