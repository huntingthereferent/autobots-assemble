from itertools import permutations
import numpy as np
import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction
from latent import objects

def g(obs):
    a=np.asarray(obs.frame)
    if a.ndim==3:a=a[-1]
    return a.reshape(64,64)

def click(env,xy,why):
    a=GameAction.ACTION6;a.set_data({"x":int(xy[0]),"y":int(xy[1])})
    return env.step(a,data={"x":int(xy[0]),"y":int(xy[1])},reasoning={"probe":why})

def parse(env):
    obs=env.observation_space
    os=list(objects(g(obs)))
    # bottom movable pieces: same size, lower quarter, distinct colors
    low=[o for o in os if o.cy2/2>48 and 4<=o.size<=64]
    bysize={}
    for o in low:bysize.setdefault(o.size,[]).append(o)
    src=max(bysize.values(),key=lambda xs:len({o.color for o in xs}))
    src_by={}
    for o in src:src_by[o.color]=o
    colors=set(src_by)
    # top reference: same color set, upper strip, largest same-color component
    rb={}
    for o in os:
        if o.cy2/2<12 and o.color in colors:
            if o.color not in rb or o.size>rb[o.color].size:rb[o.color]=o
    refs=sorted(rb.values(),key=lambda o:o.x0)
    # destination placeholders: tiny equal color/size objects in middle; choose count == n
    n=len(colors); mid=[o for o in os if 12<o.cy2/2<48 and 1<=o.size<=8]
    groups={}
    for o in mid:groups.setdefault((o.color,o.size),[]).append(o)
    choices=[xs for _,xs in groups.items() if len(xs)==n]
    choices.sort(key=lambda xs:min(o.size for o in xs))
    dest=sorted(choices[0],key=lambda o:(o.y0,o.x0)) if choices else []
    return [o.color for o in refs],{c:(o.cx2//2,o.cy2//2) for c,o in src_by.items()},[(o.cx2//2,o.cy2//2) for o in dest]

def eval_plan(env,ref,source,order,tag):
    for c,d in zip(ref,order):
        click(env,source[c],tag+" select");click(env,d,tag+" place")
    return env.step(GameAction.ACTION5,data={},reasoning={"probe":tag+" eval"})

def solve_known(env):
    # level 0: one-row placeholders => visible reference order maps left->right
    ref,src,slots=parse(env)
    if len(ref)!=4 or len(slots)!=4:return False
    o=eval_plan(env,ref,src,slots,"L0")
    if o.levels_completed!=1:return False
    # level 1: 3 top open + 4 lower open; path witness from geometry:
    # top-left, top-second, lower row left->right, top-right.
    ref,src,slots=parse(env)
    if len(ref)!=7 or len(slots)!=7:return False
    rows={}
    for xy in slots:rows.setdefault(xy[1],[]).append(xy)
    rs=sorted((y,sorted(xs)) for y,xs in rows.items())
    if len(rs)!=2 or sorted(map(lambda z:len(z[1]),rs))!=[3,4]:return False
    top=rs[0][1]; bottom=rs[1][1]
    order=top[:2]+bottom+top[2:]
    o=eval_plan(env,ref,src,order,"L1")
    return o.levels_completed==2

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
env=arc.make("sb26")
# inspect current level2 slots after dynamic known replay
if not solve_known(env):
    print("KNOWN_REPLAY_FAIL")
    raise SystemExit
ref,source,slots=parse(env)
print("L2 REF",ref)
print("L2 SLOTS",slots)
tries=0
for order in permutations(slots):
    env.step(GameAction.RESET,data={},reasoning={"probe":"full reset"})
    if not solve_known(env):
        print("KNOWN_REPLAY_FAIL_AT",tries);break
    ref,source,slots2=parse(env)
    # randomized colors okay; geometry slots should be same shape
    if len(ref)!=len(order):
        print("PARSE_MISMATCH",len(ref),len(order));break
    o=eval_plan(env,ref,source,order,"L2 candidate")
    tries+=1
    if o.levels_completed>2:
        print("FOUND",order,"tries",tries,"levels",o.levels_completed)
        break
    if tries%250==0:print("tries",tries,flush=True)
else:
    print("NOT_FOUND",tries)
