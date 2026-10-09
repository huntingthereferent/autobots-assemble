import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
from latent import objects

def grid(obs):
    a=np.asarray(obs.frame)
    if a.ndim==3:a=a[-1]
    return a.reshape(64,64)

def click(env,x,y,why):
    a=GameAction.ACTION6
    a.set_data({"x":int(x),"y":int(y)})
    return env.step(a,data={"x":int(x),"y":int(y)},reasoning={"rule":"reference-permutation-transfer","why":why})

def infer(obs):
    os=list(objects(grid(obs)))
    # Candidate bottom source row: >=3 distinct same-sized, distinct-colored small objects in lower quarter.
    lower=[o for o in os if o.cy2/2 > 48 and 4 <= o.size <= 64]
    groups={}
    for o in lower:
        groups.setdefault(o.size,[]).append(o)
    src=max(groups.values(), key=lambda g:(len({o.color for o in g}),len(g)), default=[])
    src=[o for o in src if o.color not in (0,)]
    # keep a horizontal row, distinct colors
    bycolor={}
    for o in src:
        bycolor.setdefault(o.color,o)
    src=list(bycolor.values())
    src.sort(key=lambda o:o.x0)
    colors={o.color for o in src}
    n=len(colors)
    if n<3:
        return None

    # Reference row: upper objects whose colors match the source color set.
    refs=[o for o in os if o.cy2/2 < 16 and o.color in colors]
    # choose one object/color, prefer largest because outlines may create nested same-center components
    rb={}
    for o in refs:
        if o.color not in rb or o.size>rb[o.color].size:
            rb[o.color]=o
    refs=list(rb.values())
    refs.sort(key=lambda o:o.x0)
    if {o.color for o in refs} != colors:
        return None

    # Destination slots: a horizontal middle row of n equal-size tiny objects,
    # generally sharing one placeholder color not in the movable set.
    mids=[o for o in os if 16 < o.cy2/2 < 48 and 1 <= o.size <= 16]
    mg={}
    for o in mids:
        mg.setdefault((o.color,o.size),[]).append(o)
    dest=[]
    # Destination placeholders form exactly n tiny equal-shape components.
    # Sort row-major; cells of another color/shape are blocked/non-destinations.
    exact=[(k,g) for k,g in mg.items() if len(g)==n]
    exact.sort(key=lambda kg:(kg[0][1], kg[0][0]))
    if exact:
        dest=sorted(exact[0][1], key=lambda o:(o.y0,o.x0))
    if len(dest)!=n:
        return None

    by_src={o.color:o for o in src}
    plan=[]
    for ref,dst in zip(refs,dest):
        s=by_src[ref.color]
        plan.append(((s.cx2//2,s.cy2//2),(dst.cx2//2,dst.cy2//2),ref.color))
    return plan

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
for level_try in range(12):
    obs=env.observation_space
    print("AT",obs.levels_completed,"/",obs.win_levels,"state",obs.state)
    if obs.levels_completed>=obs.win_levels:
        break
    plan=infer(obs)
    print("PLAN",plan)
    if not plan:
        print("INFER_FAIL")
        break
    before=obs.levels_completed
    for src,dst,color in plan:
        obs=click(env,*src,why=f"select source color {color}")
        obs=click(env,*dst,why=f"place source color {color} into reference-aligned slot")
    obs=env.step(GameAction.ACTION5,data={},reasoning={"rule":"reference-permutation-transfer","why":"evaluate completed visible reference match"})
    print("EVAL",obs.levels_completed,"state",obs.state)
    if obs.levels_completed<=before:
        print("NO_PROGRESS")
        break
