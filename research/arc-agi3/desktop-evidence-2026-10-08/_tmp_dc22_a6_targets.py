from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy
arc=Arcade(operation_mode=OperationMode.NORMAL);root=arc.make("dc22")
for lab,z in [("ROOT",None),("S1",1),("S2",2),("S3",3),("S4",4)]:
 e=copy.deepcopy(root)
 if z:e.step(GameAction.from_id(z),data={})
 g=e._game
 spr=[]
 for s in g.current_level.get_sprites():
  try: tags=tuple(sorted(s.tags))
  except: tags=()
  if "buezna" in tags:
   spr.append((s.name,int(s.x),int(s.y),int(s.width),int(s.height),tags))
 try: cam=g.camera._calculate_scale_and_offset()
 except Exception as ex: cam=str(ex)
 print(lab,"TARGETS",spr,"CAM",cam)
