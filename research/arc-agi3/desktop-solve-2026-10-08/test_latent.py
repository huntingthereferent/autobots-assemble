import json,sys
sys.path.insert(0,r"C:\Users\teepa\arc3\solve")
import arc_agi
from arc_agi import OperationMode
from latent_state import perceive
arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
for gid in ("sb26","ls20"):
 env=arc.make(gid); v=perceive(env.observation_space)
 print("\nGAME",gid)
 print("groups")
 for b in v.horizontal_groups:
  print({"band":[b.y0,b.y1],"colors":b.colors,"centers":b.centers,"members":b.member_pixels,"sizes":b.component_sizes})
 print("counters",v.counter_strips)
