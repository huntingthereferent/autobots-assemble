from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
from PIL import Image
a=Arcade(operation_mode=OperationMode.NORMAL); e=a.make('ar25')
for i in [3]*5+[2]*10: o=e.step(GameAction.from_id(i),data={})
b=o.frame[0]
# Save exact returned next layer and print connected components for every non-background color.
p=np.array([[0,0,0],[0,116,217],[255,65,54],[46,204,64],[255,220,0],[170,170,170],[240,18,190],[255,133,27],[127,219,255],[255,255,255],[135,12,37],[0,0,128],[0,128,0],[128,0,128],[128,128,0],[0,128,128]],dtype=np.uint8)
Image.fromarray(p[b]).resize((768,768),Image.Resampling.NEAREST).save(r'C:\Users\teepa\arc3\AB_ARC_EVIDENCE\returned_level2.png')
print('level',o.levels_completed,'colors',[(int(c),int((b==c).sum())) for c in np.unique(b)])
