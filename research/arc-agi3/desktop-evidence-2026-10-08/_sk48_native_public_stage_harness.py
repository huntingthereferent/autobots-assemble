"""SK48 public-only native stage harness, research tests only.

Read prior alternative route evidence; stop every stage at first native
completion. ACTION6 always selects next control from visible pixels.
Never inspect private game implementation/state.
"""
from pathlib import Path
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import json,numpy as np
from _sk48_public_goal_sensor import frame
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
def routes():
 l1=json.loads((F/"sk48_live_single_stream_bfs.json").read_text())["solution"]["path"]
 l2=[v["L2_actions"] for v in json.loads((F/"sk48_l2_fresh_macro_completion_witnesses.json").read_text())["results"] if v["passed"] and v["different_from_saved_reference"]]
 l3=[v["L3_path"] for v in json.loads((F/"sk48_l3_native_fresh_macro_wins.json").read_text())["results"] if v["passed"] and v["different_from_saved_reference"]]
 l4=[v["path"] for v in json.loads((F/"sk48_l4_native_reference_mutation_ab.json").read_text())["successful_interventions"] if v["method"]=="swap_adjacent"]
 l5=[v["actions"] for v in json.loads((F/"sk48_l5_native_fresh_swap_witnesses.json").read_text())["routes"] if v["passed"]]
 l6=[v["route"] for v in json.loads((F/"sk48_l6_native_fresh_swap_witnesses.json").read_text())["results"] if v["all_pass"]]
 return [ [l1],l2,l3,l4,l5,l6 ]
def controls(a):
 out=[]
 for y in range(49):
  for x in range(55):
   v=int(a[y,x])
   if v not in (6,15):continue
   b=a[y:y+6,x:x+6]
   if b.shape!=(6,6) or not(np.all(b[0,:]==v) and np.all(b[:,0]==v)):continue
   if int(b[1,1]) not in (0,4):continue
   if not any(int(z)!=v for z in b[1:5,1:5].flat):continue
   out.append((x,y,v))
 return sorted(set(out),key=lambda z:z[0])
def run_level(e,o,path,target):
 active=0;clicks=[]
 for k,z in enumerate(path,1):
  if z==6:
   c=controls(frame(o))
   if len(c)!=2:raise RuntimeError(("public controls unidentified",target,k,c))
   active=1-active;x,y,_=c[active]
   o=e.step(GameAction.ACTION6,data={"x":x+2,"y":y+2})
   clicks.append((k,x+2,y+2))
  else:o=e.step(GameAction.from_id(z),data={})
  if o.levels_completed>=target:break
 if o.levels_completed<target:raise RuntimeError(("stage failed",target,k))
 return o,k,clicks
def enter(target,selector=0):
 e=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
 o=e.observation_space;milestones=[]
 for i,options in enumerate(routes()[:target-1],1):
  seq=options[(selector+i)%len(options)]
  o,n,clicks=run_level(e,o,seq,i)
  milestones.append((i,n,clicks))
 return e,o,milestones
