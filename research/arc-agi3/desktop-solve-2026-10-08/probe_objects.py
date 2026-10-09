import arc_agi
from arc_agi import OperationMode
from latent import perceive
arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
for gid in ["ls20","g50t","sb26","vc33"]:
    env=arc.make(gid)
    s=perceive(env.observation_space)
    print("\nGAME",gid,"objects",len(s.objects))
    for i,o in enumerate(s.objects):
        if o.size<=200:
            print(i,"c",o.color,"n",o.size,"box",(o.x0,o.y0,o.x1,o.y1),"shape",o.shape,"center2",o.center2)
