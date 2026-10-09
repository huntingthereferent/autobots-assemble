from __future__ import annotations
import sys
sys.path.insert(0,r"C:\Users\teepa\arc3\solve")
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
from latent_state import perceive

def choose_groups(v):
    groups=[g for g in v.horizontal_groups if len(g.colors)>=3]
    if len(groups)<3:
        return None
    groups=sorted(groups,key=lambda g:g.y0)
    # candidate triplets: same arity; bottom colors cover top colors
    best=None
    for i,t in enumerate(groups):
        for j,m in enumerate(groups):
            if j<=i: continue
            for k,b in enumerate(groups):
                if k<=j: continue
                if len(t.colors)!=len(m.colors): continue
                if len(set(t.colors)-set(b.colors))>0: continue
                score=(b.y0-t.y0, -len(set(m.colors)), len(t.colors))
                if best is None or score>best[0]:
                    best=(score,t,m,b)
    return None if best is None else best[1:]

def click(env,x,y,label):
    a=GameAction.ACTION6
    a.set_data({"x":int(x),"y":int(y)})
    return env.step(a,data={"x":int(x),"y":int(y)},reasoning={"latent_synthesis":label})

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
obs=env.observation_space
last=-1
for attempt in range(12):
    level=int(obs.levels_completed)
    print("\nLEVEL",level,"state",obs.state)
    if level==last:
        print("NO_ADVANCE"); break
    last=level
    v=perceive(obs)
    picked=choose_groups(v)
    if picked is None:
        print("NO_PATTERN"); break
    top,mid,bot=picked
    print("top",top.colors,"mid",mid.colors,"bottom",bot.colors)
    palette={}
    for color,p in zip(bot.colors,bot.member_pixels):
        palette.setdefault(color,p)
    ok=True
    for idx,(color,slot) in enumerate(zip(top.colors,mid.centers)):
        if color not in palette:
            ok=False; print("MISSING_COLOR",color); break
        px,py=palette[color]
        obs=click(env,px,py,f"select symbol {color}")
        sx,sy=slot
        obs=click(env,sx,sy,f"write slot {idx}")
        if int(obs.levels_completed)>level:
            break
    if not ok: break
    if int(obs.levels_completed)==level:
        obs=env.step(GameAction.ACTION5,data={},reasoning={"latent_synthesis":"execute current program"})
    print("after",obs.levels_completed,obs.state)
    if "WIN" in str(obs.state):
        break
