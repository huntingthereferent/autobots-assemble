from __future__ import annotations
import sys
sys.path.insert(0,r"C:\Users\teepa\arc3\solve")
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
from latent_state import perceive

PLACEHOLDER=2

def click(env,x,y,label):
    a=GameAction.ACTION6
    a.set_data({"x":int(x),"y":int(y)})
    return env.step(a,data={"x":int(x),"y":int(y)},reasoning={"synthesis":label})

def pattern(v):
    gs=[g for g in v.horizontal_groups if len(g.colors)>=3]
    gs=sorted(gs,key=lambda g:g.y0)
    if len(gs)<3:return None
    top=gs[0]; bottom=gs[-1]
    # palette must cover target alphabet
    if not set(top.colors).issubset(set(bottom.colors)):
        return None
    program=[g for g in gs[1:-1] if len(g.colors)==4]
    if not program:return None
    return top,program,bottom

def flatten_slots(program):
    # Rows are laid out root-to-descendant vertically. A non-placeholder slot
    # in a row is treated as a call edge to the next unconsumed row.
    next_child=[1]
    def walk(row_i):
        row=program[row_i]
        out=[]
        for color,center in zip(row.colors,row.centers):
            if color==PLACEHOLDER:
                out.append(center)
            else:
                if next_child[0] >= len(program):
                    # unsupported call structure
                    return None
                child=next_child[0]; next_child[0]+=1
                sub=walk(child)
                if sub is None:return None
                out.extend(sub)
        return out
    return walk(0)

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
obs=env.observation_space
for round_i in range(3):
    lvl=int(obs.levels_completed)
    v=perceive(obs)
    p=pattern(v)
    print("\nLEVEL",lvl)
    if p is None:
        print("NO_PATTERN"); break
    target,program,palette=p
    leaves=flatten_slots(program)
    print("target",target.colors)
    print("program",[r.colors for r in program])
    print("leaves",leaves)
    if leaves is None or len(leaves)!=len(target.colors):
        print("FLATTEN_MISMATCH",None if leaves is None else len(leaves),len(target.colors));break
    pm={}
    for c,xy in zip(palette.colors,palette.member_pixels):
        pm.setdefault(c,xy)
    for i,(c,slot) in enumerate(zip(target.colors,leaves)):
        if c not in pm:
            print("MISSING",c);raise SystemExit
        obs=click(env,*pm[c],f"select {c}")
        obs=click(env,*slot,f"write leaf {i}")
    obs=env.step(GameAction.ACTION5,data={},reasoning={"synthesis":"execute flattened program"})
    print("after",obs.levels_completed,obs.state)
    if int(obs.levels_completed)==lvl:
        print("NO_ADVANCE");break
