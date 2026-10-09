from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import copy,hashlib,numpy as np,collections

def H(r): return hashlib.sha1(np.array(r.frame[0],dtype=np.int16).tobytes()).hexdigest()[:12]
cfg={
"bp35":{"simple":[3,4,7],"c":[(0,0),(12,0),(18,0),(24,0),(30,12),(36,12),(42,12),(48,12)]},
"dc22":{"simple":[1,2,3,4],"c":[(0,0),(45,17),(45,34)]},
"cd82":{"simple":[1,2,3,4,5],"c":[(0,0),(35,2)]},
}
arc=Arcade(operation_mode=OperationMode.NORMAL)
for name,c in cfg.items():
    root=arc.make(name); branches=[]
    for z in c["simple"]:
        q=copy.deepcopy(root); r=q.step(GameAction.from_id(z),data={})
        branches.append((f"S{z}",H(r),q))
    for xy in c["c"]:
        q=copy.deepcopy(root); r=q.step(GameAction.ACTION6,data={"x":xy[0],"y":xy[1]})
        branches.append((f"C{xy}",H(r),q))
    groups=collections.defaultdict(list)
    for lab,h,e in branches: groups[h].append((lab,e))
    print("\nGAME",name,"BRANCHES",len(branches),"PUBLIC_CLASSES",len(groups))
    for h,items in groups.items():
        print(" OBS",h,[x[0] for x in items])
        if len(items)>1:
            for i in range(len(items)):
                for j in range(i+1,len(items)):
                    la,a=items[i];lb,b=items[j]
                    dif=[]
                    va=vars(a._game); vb=vars(b._game)
                    for k in sorted(set(va)|set(vb)):
                        x=va.get(k);y=vb.get(k)
                        if isinstance(x,(int,float,bool,str,type(None))) and isinstance(y,(int,float,bool,str,type(None))) and x!=y:
                            dif.append((k,x,y))
                        elif isinstance(x,(list,tuple,dict,set)) and isinstance(y,type(x)):
                            try:
                                if len(x)!=len(y):dif.append((k,"len",len(x),len(y)))
                            except:pass
                    print("  COLLISION",la,lb,"DIFF",dif[:20])
