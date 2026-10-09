import sys, numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
sys.path.insert(0,r"C:\Users\teepa\arc3\solve")
import my_agent_g2_latent as g2

def click(env,x,y):
    a=GameAction.ACTION6; a.set_data({"x":x,"y":y})
    return env.step(a,data={"x":x,"y":y},reasoning={"diag":"reach"})

def reach3(env):
    for sx,sy,tx,ty in [(35,58,22,29),(19,58,28,29),(43,58,34,29),(27,58,40,29)]:
        click(env,sx,sy); click(env,tx,ty)
    env.step(GameAction.ACTION5,data={},reasoning={"diag":"l1"})
    for sx,sy,tx,ty in [
        (31,58,22,22),(17,58,28,22),(38,58,40,22),
        (10,58,22,36),(45,58,28,36),(24,58,34,36),(52,58,40,36)
    ]:
        click(env,sx,sy); click(env,tx,ty)
    return env.step(GameAction.ACTION5,data={},reasoning={"diag":"l2"})

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
obs=reach3(env)
print("LEVEL",obs.levels_completed)
print("ROWS")
for r in g2.row_groups(obs):
    print("y",r["y"]/2,"colors",r["colors"],"sizes",[(c["size"],c["w"],c["h"]) for c in r["comps"]])

# candidate target/palette pairs
rows=g2.row_groups(obs)
from collections import Counter
pairs=[]
for i,a in enumerate(rows):
    for j,b in enumerate(rows):
        if j<=i or len(a["colors"])!=len(b["colors"]): continue
        if Counter(a["colors"])!=Counter(b["colors"]): continue
        n=len(a["colors"])
        if n<3 or len(set(a["colors"]))<n-1: continue
        above=a if a["y"]<b["y"] else b
        below=b if a["y"]<b["y"] else a
        pairs.append((above,below))
print("PAIRS",[(p[0]["colors"],p[1]["colors"],p[0]["y"]/2,p[1]["y"]/2) for p in pairs])
if pairs:
    target,palette=max(pairs,key=lambda ab:(len(ab[0]["colors"]),ab[1]["y"]-ab[0]["y"]))
    boxes=g2._program_boxes(g2.grid(obs),target["y"]/2,palette["y"]/2)
    print("BOXES",boxes)
    cs=g2.components(g2.grid(obs))
    for b in boxes:
        inside=[]
        for c in cs:
            cx=c["cx2"]/2; cy=c["cy2"]/2
            if b["x0"]<cx<b["x1"] and b["y0"]<cy<b["y1"] and c["w"]<=6 and c["h"]<=6:
                inside.append((c["color"],c["size"],cx,cy,c["w"],c["h"]))
        print("INSIDE",b,inside)
print("PLAN",g2.detect_program_plan(obs))
