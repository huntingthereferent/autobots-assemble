from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy, numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL)
for name in ["bp35","cd82","cn04","dc22","ft09","g50t","ka59","lf52","lp85","ls20","m0r0","r11l","re86","s5i5","sb26","sc25","sk48","sp80","su15","tn36","tr87","tu93","vc33","wa30"]:
    try:
        e=a.make(name)
        r=e.step(GameAction.from_id(1),data={})
        attrs=[x for x in dir(r) if not x.startswith("_")]
        print(name,"RESULT_ATTRS",attrs[:30])
        print(" state",getattr(r,"state",None),"levels",getattr(r,"levels_completed",None))
        for k in ["frame","observation","grid","board"]:
            v=getattr(r,k,None)
            if v is not None:
                try: print(" ",k,type(v),getattr(v,"shape",None))
                except: pass
        break
    except Exception as ex:
        print(name,"ERR",type(ex).__name__,str(ex)[:100])
