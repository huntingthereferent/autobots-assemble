import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
from latent import objects

def g(obs):
    a=np.asarray(obs.frame)
    if a.ndim==3:a=a[-1]
    return a.reshape(64,64)

def parse(obs):
    os=list(objects(g(obs)))
    low=[o for o in os if o.cy2/2>48 and 4<=o.size<=64]
    bysize={}
    for o in low:bysize.setdefault(o.size,[]).append(o)
    src=max(bysize.values(),key=lambda xs:len({o.color for o in xs}),default=[])
    src_by={o.color:o for o in src}
    colors=set(src_by)
    refs={}
    for o in os:
        if o.cy2/2<12 and o.color in colors:
            if o.color not in refs or o.size>refs[o.color].size:refs[o.color]=o
    n=len(colors)
    mid=[o for o in os if 12<o.cy2/2<48 and 1<=o.size<=8]
    groups={}
    for o in mid:groups.setdefault((o.color,o.size),[]).append(o)
    choices=[xs for _,xs in groups.items() if len(xs)==n]
    dest=sorted(choices[0],key=lambda o:(o.y0,o.x0)) if choices else []
    return {
        "n":n,
        "ref_colors":[o.color for o in sorted(refs.values(),key=lambda x:x.x0)],
        "src_colors":[o.color for o in sorted(src_by.values(),key=lambda x:x.x0)],
        "slots":[(o.cx2//2,o.cy2//2) for o in dest],
        "rows":{}
    }

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
for i in range(8):
    if i:
        env.step(GameAction.RESET,data={},reasoning={"probe":"reset variability"})
    print(i,parse(env.observation_space))
