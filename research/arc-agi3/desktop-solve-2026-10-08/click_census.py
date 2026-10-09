import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
from latent import perceive,effect

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
for gid in ["sb26","vc33"]:
    env=arc.make(gid)
    base=env.observation_space
    s=perceive(base)
    print("\nGAME",gid)
    pts=[]
    for i,o in enumerate(s.objects):
        if o.size>256: continue
        x,y=o.center2[0]//2,o.center2[1]//2
        pts.append((i,o.color,o.size,o.x0,o.y0,o.x1,o.y1,x,y))
    for rec in pts:
        i,c,n,x0,y0,x1,y1,x,y=rec
        try:
            env.step(GameAction.RESET,data={},reasoning={"probe":"reset"})
            before=env.observation_space
            a=GameAction.ACTION6
            a.set_data({"x":x,"y":y})
            after=env.step(a,data={"x":x,"y":y},reasoning={"probe":"click_census"})
            e=effect(before,after)
            print("obj",i,"c",c,"n",n,"box",(x0,y0,x1,y1),"click",(x,y),
                  "=>",e.class_name,e.changed_pixels,e.bbox,e.color_delta,"levels",after.levels_completed)
        except Exception as ex:
            print("obj",i,"ERR",type(ex).__name__,str(ex)[:120])
