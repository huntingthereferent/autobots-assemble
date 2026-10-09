from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import json,numpy as np,pathlib
rec=json.loads(pathlib.Path(r'C:\Users\teepa\arc3\AB_ARC_EVIDENCE\ft09_verified_6of6.json').read_text(encoding='utf-8'))
a=Arcade(operation_mode=OperationMode.NORMAL);e=a.make('ft09')
for li in range(1,7):
 o=e.observation_space
 frame=np.asarray(o.frame[-1],dtype=np.int16).reshape(64,64)
 print('LEVEL',li,'UNIQUE',sorted({int(x) for x in frame.ravel()}),'TOP_SCREEN',flush=True)
 for y in range(0,64,2):
  print(f'{y:02d}', ''.join('0123456789ABCDEF'[max(0,int(frame[y,x]))] for x in range(0,64,2)),flush=True)
 for x,y in rec['paths'][li-1]:
  r=e.step(GameAction.ACTION6,data={'x':x,'y':y})
 print('COMPLETE',r.levels_completed,r.state.name,flush=True)
