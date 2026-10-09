from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); e=a.make('ar25')
for i in [3]*5+[2]*10: o=e.step(GameAction.from_id(i),data={})
# Earned closure from L1: moving down made the two 9x9 carriers occupy the SAME y-range;
# at closure their embedded 5-dot patterns also became fully contained/aligned with their carriers.
# L2 returned board already has both carriers y45..53 and both dot patterns y46..52.
# So next relation is orientation mismatch of embedded patterns. Test vertical movement: it preserves orientation,
# therefore cannot repair mismatch; ACTION5/7 didn't. Probe ACTION6 at corresponding embedded dots as the only remaining
# interaction class capable of changing internal relation, paired symmetrically.
pts=[(4,46),(7,46),(10,46),(10,49),(10,52),(52,46),(55,46),(58,46),(52,49),(52,52)]
for j,(x,y) in enumerate(pts,1):
 o=e.step(GameAction.ACTION6,data={'x':x,'y':y}); print(j,(x,y),o.levels_completed,o.state)
 if o.levels_completed>1: break
