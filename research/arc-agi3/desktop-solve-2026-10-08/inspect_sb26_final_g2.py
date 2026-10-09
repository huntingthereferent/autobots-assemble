import sys,importlib.util,numpy as np
sys.path.insert(0,r"C:\Users\teepa\arc3\ARC-AGI-3-Kaggle-Starter\vendor\ARC-AGI-3-Agents")
import arc_agi
from arc_agi import OperationMode
spec=importlib.util.spec_from_file_location("g2",r"C:\Users\teepa\arc3\solve\my_agent_g2.py")
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
class StopAt7(m.MyAgent):
    def is_done(self,frames,latest):
        return int(getattr(latest,"levels_completed",0))>=7
arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
agent=StopAt7(card_id="inspect-final",game_id="sb26",agent_name="inspect-final",ROOT_URL="http://localhost",record=False,arc_env=env,tags=["inspect"])
agent.main()
o=agent.frames[-1]
print("STOP levels",o.levels_completed,"state",o.state,"actions",agent.action_counter)
g=m.grid(o); cs=m.components(g)
for c in sorted(cs,key=lambda z:(z["color"],z["size"],z["y0"],z["x0"])):
    if c["size"]<=420:
        print(c["color"],c["size"],c["x0"],c["y0"],c["x1"],c["y1"],"w",c["w"],"h",c["h"])
dummy=object.__new__(m.MyAgent)
print("PARSE",m.MyAgent._parse_construction(dummy,o))
