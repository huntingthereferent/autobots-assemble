from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy,hashlib,numpy as np
def H(r):return hashlib.sha1(np.array(r.frame[0],dtype=np.int16).tobytes()).hexdigest()[:12]
arc=Arcade(operation_mode=OperationMode.NORMAL)
for name in ["lp85","r11l","tn36","vc33"]:
 root=arc.make(name);g=root._game
 sc,ox,oy=g.camera._calculate_scale_and_offset()
 targets=[]
 for s in g.current_level.get_sprites():
  try:tags=tuple(sorted(s.tags))
  except:tags=()
  if "sys_click" not in tags:continue
  x=int((s.x+s.width//2)*sc+ox);y=int((s.y+s.height//2)*sc+oy)
  targets.append((s.name,(x,y),int(s.x),int(s.y),int(s.width),int(s.height),tags))
 print("\nGAME",name,"TARGETS",targets)
 branches=[]
 for lab,xy in [("MISS",(0,0))]+[(t[0],t[1]) for t in targets]:
  q=copy.deepcopy(root);r=q.step(GameAction.ACTION6,data={"x":xy[0],"y":xy[1]})
  branches.append((lab,xy,H(r),q))
 for lab,xy,h,q in branches: print(" ",lab,xy,h)
 by={}
 for lab,xy,h,q in branches:by.setdefault(h,[]).append((lab,q))
 for h,items in by.items():
  if len(items)>1:
   print(" COLLISION",h,[x[0] for x in items])
   for i in range(len(items)):
    for j in range(i+1,len(items)):
     la,a=items[i];lb,b=items[j];dif=[]
     va,vb=vars(a._game),vars(b._game)
     for k in sorted(set(va)|set(vb)):
      x,y=va.get(k),vb.get(k)
      if isinstance(x,(int,float,bool,str,type(None))) and isinstance(y,(int,float,bool,str,type(None))) and x!=y:dif.append((k,x,y))
     print("  ",la,lb,dif[:25])
