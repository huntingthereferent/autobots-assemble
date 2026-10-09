import sys,arc_agi
sys.path.insert(0,r"C:\Users\teepa\arc3\solve\g2")
from arc_agi import OperationMode
from mirror import detect,plan
arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("m0r0")
m=detect(env.observation_space)
print("DETECT",None if m is None else {"q":m["q"],"node_size":m["node_size"],"state":m["state"]})
p,n=plan(m)
print("PLAN",p,"STATES",n)
