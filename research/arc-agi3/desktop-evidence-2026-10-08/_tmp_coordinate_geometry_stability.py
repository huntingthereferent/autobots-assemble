from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy,hashlib
CFG={
"ft09":[(0,0),(36,36),(44,36),(52,36),(36,44),(52,44),(36,52),(44,52),(52,52)],
"lp85":[(0,0),(2,29),(56,29)],
"r11l":[(0,0),(25,57)],
"s5i5":[(0,0),(36,18),(43,18),(21,35),(21,42)],
"tn36":[(0,0),(41,51),(32,51),(19,41),(24,41),(29,41),(34,41),(39,41),(19,44),(24,44),(29,44),(34,44),(39,44)],
"vc33":[(0,0),(60,24),(60,32)],
}
def geom(g):
 arr=[]
 for s in g.current_level.get_sprites():
  try:tags=tuple(sorted(s.tags))
  except:tags=()
  if "sys_click" in tags:
   arr.append((s.name,int(s.x),int(s.y),int(s.width),int(s.height),bool(s.visible),tags))
 arr.sort()
 try:cam=tuple(g.camera._calculate_scale_and_offset())
 except:cam=None
 return hashlib.sha1(repr((arr,cam)).encode()).hexdigest()[:12],len(arr),cam

arc=Arcade(operation_mode=OperationMode.NORMAL)
for name,reps in CFG.items():
 root=arc.make(name); base=geom(root._game); groups={}
 groups.setdefault(base[0],[]).append("ROOT")
 details={base[0]:base}
 for xy in reps:
  q=copy.deepcopy(root);r=q.step(GameAction.ACTION6,data={"x":xy[0],"y":xy[1]})
  fp=geom(q._game);groups.setdefault(fp[0],[]).append(xy);details[fp[0]]=fp
 print("\nGAME",name,"GEOM_CLASSES",len(groups))
 for k,v in groups.items():print(" ",k,"NCLICK",details[k][1],"CAM",details[k][2],"FROM",v)
