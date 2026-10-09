from __future__ import annotations
import sys
import numpy as np
from PIL import Image
sys.path.insert(0,r"C:\Users\teepa\arc3\solve")
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
from latent_state import perceive
from program_synthesis import parse_synthesis

def click(env,xy,label):
    x,y=xy
    a=GameAction.ACTION6
    a.set_data({"x":int(x),"y":int(y)})
    return env.step(a,data={"x":int(x),"y":int(y)},reasoning={"generic_synthesis":label})

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
obs=env.observation_space
for attempt in range(12):
    lvl=int(obs.levels_completed)
    s=parse_synthesis(perceive(obs))
    print("\nLEVEL",lvl,"state",obs.state)
    if s is None:
        print("PARSE_FAIL")
        break
    print("target",s.target)
    print("placeholder",s.placeholder)
    print("routines",[(r.y0,r.colors,r.centers) for r in s.routines])
    print("leaves",s.leaves,"n",len(s.leaves))
    if len(s.leaves)!=len(s.target):
        print("LEAF_TARGET_MISMATCH")
        a=np.asarray(obs.frame)
        if a.ndim==3:
            a=a[-1]
        a=a.reshape(64,64).astype(np.uint8)
        pal=np.array([[0,0,0],[0,116,217],[255,65,54],[46,204,64],[255,220,0],[170,170,170],[240,18,190],[255,133,27],[127,219,255],[135,12,37],[0,0,0],[255,255,255],[128,128,128],[0,128,128],[0,128,128],[255,165,0]],dtype=np.uint8)
        Image.fromarray(pal[a]).resize((512,512),Image.Resampling.NEAREST).save(r"C:\Users\teepa\arc3\solve\sb26_level3.png")
        v=perceive(obs)
        print("ALL_COMPONENTS",[(c.color,c.size,c.box,(c.member_x,c.member_y),round(c.fill,2)) for c in v.components if c.size<=500])
        break
    pm={}
    for c,p in s.palette:
        pm.setdefault(c,p)
    ok=True
    for i,(color,slot) in enumerate(zip(s.target,s.leaves)):
        if color not in pm:
            print("MISSING_PALETTE",color);ok=False;break
        obs=click(env,pm[color],f"select symbol {color}")
        obs=click(env,slot,f"write leaf {i}")
    if not ok:break
    obs=env.step(GameAction.ACTION5,data={},reasoning={"generic_synthesis":"execute flattened program"})
    print("after",obs.levels_completed,obs.state)
    if int(obs.levels_completed)==lvl:
        print("NO_ADVANCE")
        break
    if "WIN" in str(obs.state):
        break
