from __future__ import annotations
import sys
sys.path.insert(0,r"C:\Users\teepa\arc3\solve")
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
from latent_state import perceive
from program_synthesis import parse_synthesis

def click(env,xy,label):
 x,y=xy
 a=GameAction.ACTION6;a.set_data({"x":int(x),"y":int(y)})
 return env.step(a,data={"x":int(x),"y":int(y)},reasoning={"s":label})

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26");obs=env.observation_space

# Levels 0-2 generic.
for _ in range(3):
 s=parse_synthesis(perceive(obs));pm={c:p for c,p in s.palette}
 for c,slot in zip(s.target,s.leaves):
  obs=click(env,pm[c],"sel");obs=click(env,slot,"write")
 obs=env.step(GameAction.ACTION5,data={},reasoning={"s":"exec"})

# Level 3 synthesized child call14.
v=perceive(obs);s=parse_synthesis(v);pm={c:p for c,p in s.palette}
root=list(s.routines[0].centers)
root_tokens=[11,8,14,12,15]
for c,slot in zip(root_tokens,root):
 obs=click(env,pm[c],"root");obs=click(env,slot,"rootw")
# child14 leaves visually inferred from its framed routine
for c,slot in zip([9,6],[(31,36),(37,36)]):
 obs=click(env,pm[c],"child");obs=click(env,slot,"childw")
obs=env.step(GameAction.ACTION5,data={},reasoning={"s":"exec3"})
print("before L4",obs.levels_completed)

# Level 4 current structure.
v=perceive(obs)
gs=sorted(v.horizontal_groups,key=lambda g:g.y0)
target=gs[0].colors
bottom=gs[-1]
from collections import defaultdict, deque
pq=defaultdict(deque)
for c,p in zip(bottom.colors,bottom.member_pixels):
 pq[c].append(p)
root=[(19,22),(25,22),(31,22),(37,22),(43,22)]
child=[(25,36),(31,36),(37,36)]
print("target",target,"palette",bottom.colors)
def take(color):
 return pq[color].popleft()
for tok,slot in zip([6,9,9,11,15],root):
 obs=click(env,take(tok),f"root {tok}");obs=click(env,slot,"write root")
for tok,slot in zip([14,8,8],child):
 obs=click(env,take(tok),f"child {tok}");obs=click(env,slot,"write child")
vv=perceive(obs)
print("PROGRAM_GROUPS",[(g.y0,g.colors,g.centers,g.component_sizes) for g in vv.horizontal_groups])
print("PROGRAM_COMPONENTS",[(c.color,c.size,c.box,round(c.fill,2)) for c in vv.components if 15<=c.y0<=45 and c.size<=80])
obs=env.step(GameAction.ACTION5,data={},reasoning={"s":"exec4"})
print("RESULT",obs.levels_completed,obs.win_levels,obs.state)
nxt=perceive(obs)
print("NEXT_GROUPS",[(g.y0,g.y1,g.colors,g.centers,g.member_pixels,g.component_sizes) for g in nxt.horizontal_groups])
print("NEXT_COMPONENTS",[(c.color,c.size,c.box,(c.member_x,c.member_y),round(c.fill,2)) for c in nxt.components if c.size<=800])

# Level 5+: generic symbolic parser/constraint solver.
from symbolic_program_solver import parse_program, solve_program
model=parse_program(nxt)
print("GENERIC_MODEL",model)
assignment=solve_program(model) if model is not None else None
print("GENERIC_ASSIGNMENT",assignment)
if model is not None and assignment is not None:
    rmap={r.idx:r for r in model.resources}
    for xy,rid in assignment.items():
        res=rmap[rid]
        obs=click(env,res.xy,f"generic resource {rid} {res.kind} {res.color}")
        obs=click(env,xy,f"generic write {xy}")
    obs=env.step(GameAction.ACTION5,data={},reasoning={"s":"generic symbolic execute"})
    print("GENERIC_RESULT",obs.levels_completed,obs.win_levels,obs.state)

    # Continue with the same generic parser/solver on subsequent levels.
    for generic_round in range(4):
        lvl_now=int(obs.levels_completed)
        if "WIN" in str(obs.state):
            break
        mm=parse_program(perceive(obs))
        print("ROUND",generic_round,"LEVEL",lvl_now,"MODEL",mm)
        aa=solve_program(mm) if mm is not None else None
        print("ROUND_ASSIGNMENT",aa)
        if mm is None or aa is None:
            vv2=perceive(obs)
            print("FAIL_GROUPS",[(g.y0,g.y1,g.colors,g.centers,g.member_pixels,g.component_sizes) for g in vv2.horizontal_groups])
            print("FAIL_COMPONENTS",[(c.color,c.size,c.box,(c.member_x,c.member_y),round(c.fill,2)) for c in vv2.components if c.size<=900])
            import numpy as np
            from PIL import Image
            aa=np.asarray(obs.frame)
            if aa.ndim==3:
                aa=aa[-1]
            aa=aa.reshape(64,64).astype(np.uint8)
            pp=np.array([[0,0,0],[0,116,217],[255,65,54],[46,204,64],[255,220,0],[170,170,170],[240,18,190],[255,133,27],[127,219,255],[135,12,37],[0,0,0],[255,255,255],[128,128,128],[0,128,128],[0,128,128],[255,165,0]],dtype=np.uint8)
            Image.fromarray(pp[aa]).resize((512,512),Image.Resampling.NEAREST).save(r"C:\Users\teepa\arc3\solve\sb26_final.png")

            # Final-level recursive hypothesis derived from the visible two-row
            # repeated target and the two callable routines.
            if lvl_now==7:
                final_resources={
                    15:(7,59),11:(14,59),12:(21,59),8:(28,59),9:(35,59),14:(42,59),
                    "call8":(48,57),"call9":(55,57)
                }
                root_slots=[(22,26),(28,26),(34,26),(40,26)]
                child_slots=[(22,40),(28,40),(34,40),(40,40)]
                root_prog=[8,11,12,"call9"]
                child_prog=[9,14,15,"call8"]
                for tok,xy in zip(root_prog,root_slots):
                    obs=click(env,final_resources[tok],f"recursive root {tok}")
                    obs=click(env,xy,"write recursive root")
                for tok,xy in zip(child_prog,child_slots):
                    obs=click(env,final_resources[tok],f"recursive child {tok}")
                    obs=click(env,xy,"write recursive child")
                obs=env.step(GameAction.ACTION5,data={},reasoning={"s":"execute recursive synthesis"})
                print("RECURSIVE_FINAL_RESULT",obs.levels_completed,obs.win_levels,obs.state)
            break
        rr={r.idx:r for r in mm.resources}
        for xy,rid in aa.items():
            res=rr[rid]
            obs=click(env,res.xy,f"generic resource {rid} {res.kind} {res.color}")
            obs=click(env,xy,f"generic write {xy}")
        obs=env.step(GameAction.ACTION5,data={},reasoning={"s":"generic symbolic execute"})
        print("ROUND_RESULT",obs.levels_completed,obs.win_levels,obs.state)
        if int(obs.levels_completed)==lvl_now:
            break
