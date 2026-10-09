from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import itertools, math

a=Arcade(operation_mode=OperationMode.NORMAL)

SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
L3A=[5,5,4,5,7,2,5,2,2,2,2,3,5]+[1]*8+[3]*4+[5]+[1]*8
L3B=[5]+[4]*8+[2]*3+[5]+[3]*8+[2]*13
L4=[2]*6+[5]+[4]*7+[5]+[4]*7
L5=[2]*4+[5]+[4]*5+[5]+[3]*10+[1]*7
L6=[2]*11+[5,3,5]+[3]*15+[2]*4+[5]+[3]*7+[2]*12
L7=[2]*2+[5]+[4]*9+[5]+[3]*10+[1]*6+[5]+[4]*3+[1]*6
L8=[2]*6+[5]+[4]*9+[5]+[3]*9+[1]*7+[5]+[4]*9+[1]*4
FULL=SOL+L3A+L3B+L4+L5+L6+L7+L8

def payload_cells(s):
    return [(dx,dy) for dy,row in enumerate(s.pixels) for dx,v in enumerate(row) if int(v)>=0]

def axis_info(g):
    vx = next((s for s in g.jtkyjqznbnp if "0054kgxrvfihgm" in s.tags), None)
    hy = next((s for s in g.jtkyjqznbnp if "0002nuguepuujf" in s.tags), None)
    return vx,hy

def orbit_mask(cells,x,y,ax,ay,W,H,T_index):
    m=0
    for dx,dy in cells:
        px,py=x+dx,y+dy
        xs=(px,) if ax is None else (px,2*ax-px)
        ys=(py,) if ay is None else (py,2*ay-py)
        for xx in xs:
            for yy in ys:
                i=T_index.get((xx,yy))
                if i is not None:
                    m |= 1<<i
    return m

def solve_geometry(g):
    T=sorted({(t.x,t.y) for t in g.fswikrcrdmx})
    TI={p:i for i,p in enumerate(T)}
    FULLMASK=(1<<len(T))-1
    W,H=g.dqwpuqcubca,g.height
    vx,hy=axis_info(g)
    current_ax=None if vx is None else vx.x
    current_ay=None if hy is None else hy.y
    ax_candidates=[None] if vx is None else list(range(-2,W+3))
    ay_candidates=[None] if hy is None else list(range(-2,H+3))
    payloads=list(g.ouurgkpbbjj)
    shapes=[payload_cells(s) for s in payloads]

    best=None
    tested=0
    for ax in ax_candidates:
      for ay in ay_candidates:
        opt=[]
        for s,cells in zip(payloads,shapes):
            bymask={}
            for x in range(-8,W+8):
              for y in range(-8,H+8):
                m=orbit_mask(cells,x,y,ax,ay,W,H,TI)
                if m:
                    cost=abs(x-s.x)+abs(y-s.y)
                    old=bymask.get(m)
                    if old is None or cost<old[0]:
                        bymask[m]=(cost,(x,y))
            opt.append(bymask)
        # exact set cover for 1 or 2 payloads (all remaining levels here)
        axis_cost=(0 if ax is None else abs(ax-current_ax))+(0 if ay is None else abs(ay-current_ay))
        if len(opt)==1:
            for m,(pc,p) in opt[0].items():
                tested+=1
                if m==FULLMASK:
                    cand=(axis_cost+pc,ax,ay,[p],len(T))
                    if best is None or cand[0]<best[0]: best=cand
        elif len(opt)==2:
            A=sorted(opt[0].items(),key=lambda kv:(-kv[0].bit_count(),kv[1][0]))
            B=sorted(opt[1].items(),key=lambda kv:(-kv[0].bit_count(),kv[1][0]))
            for ma,(ca,pa) in A:
                need=FULLMASK & ~ma
                for mb,(cb,pb) in B:
                    tested+=1
                    if (mb & need)==need:
                        cand=(axis_cost+ca+cb,ax,ay,[pa,pb],len(T))
                        if best is None or cand[0]<best[0]: best=cand
                        break
        else:
            raise RuntimeError("more than 2 payloads not supported in this proof script")
    return best,tested

# Capture each level start while replaying the known witness only to move between levels.
e=a.make('ar25');r=None
seen_levels={}
for i,z in enumerate(FULL):
    before=e._game.level_index
    if before>=2 and before not in seen_levels:
        seen_levels[before]=i
    r=e.step(GameAction.from_id(z),data={})
# final start may have been captured before its first action already
print("CAPTURED_LEVELS",sorted(seen_levels))

for lev in range(2,8):
    e=a.make('ar25');r=None
    for z in FULL[:seen_levels[lev]]:
        r=e.step(GameAction.from_id(z),data={})
    g=e._game
    vx,hy=axis_info(g)
    best,tested=solve_geometry(g)
    print("LEVEL",lev+1,
          "TARGETS",len(g.fswikrcrdmx),
          "CUR_AX",None if vx is None else vx.x,None if hy is None else hy.y,
          "CUR_PAY",[(s.x,s.y) for s in g.ouurgkpbbjj],
          "INFER",best,
          "TESTED",tested)
