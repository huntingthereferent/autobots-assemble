import sys
sys.path.insert(0,r"C:\Users\teepa\arc3\solve\g2")
import arc_agi
from arc_agi import OperationMode
from latent import grid, components

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
g=grid(env.observation_space)
cs=components(g)
cs.sort(key=lambda c:(c["y0"],c["x0"],c["color"],c["size"]))
for c in cs:
    if c["size"]>=4 and c["size"]<200:
        print(c)
