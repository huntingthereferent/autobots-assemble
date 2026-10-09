from arc_agi import Arcade,OperationMode
from arcengine import GameAction

a=Arcade(operation_mode=OperationMode.NORMAL)

def cells(s):
    return [(dx,dy) for dy,row in enumerate(s.pixels) for dx,v in enumerate(row) if int(v)>=0]

def axes(g):
    vx=next((s for s in g.jtkyjqznbnp if "0054kgxrvfihgm" in s.tags),None)
    hy=next((s for s in g.jtkyjqznbnp if "0002nuguepuujf" in s.tags),None)
    return vx,hy

def orbit_bits(c,x,y,ax,ay,TI):
    m=0
    for dx,dy in c:
        px,py=x+dx,y+dy
        xs=(px,) if ax is None else (px,2*ax-px)
        ys=(py,) if ay is None else (py,2*ay-py)
        for xx in xs:
            for yy in ys:
                i=TI.get((xx,yy))
                if i is not None:m|=1<<i
    return m

def infer(g):
    T=sorted({(t.x,t.y) for t in g.fswikrcrdmx});TI={p:i for i,p in enumerate(T)}
    full=(1<<len(T))-1;W,H=g.dqwpuqcubca,g.height
    vx,hy=axes(g);movable=set(g.ayyvxqrhnzw)
    AX=[None] if vx is None else (list(range(-2,W+3)) if vx in movable else [vx.x])
    AY=[None] if hy is None else (list(range(-2,H+3)) if hy in movable else [hy.y])
    best=None
    for ax in AX:
      for ay in AY:
        opts=[]
        for s in g.ouurgkpbbjj:
          c=cells(s);by={}
          for x in range(-8,W+8):
            for y in range(-8,H+8):
              m=orbit_bits(c,x,y,ax,ay,TI)
              if not m:continue
              cost=abs(x-s.x)+abs(y-s.y)
              if m not in by or cost<by[m][0]:by[m]=(cost,(x,y))
          opts.append(by)
        acost=(0 if vx is None or vx not in movable else abs(ax-vx.x))+(0 if hy is None or hy not in movable else abs(ay-hy.y))
        if len(opts)==1:
          for m,(pc,p) in opts[0].items():
            if m==full:
              z=(acost+pc,ax,ay,[p])
              if best is None or z[0]<best[0]:best=z
        elif len(opts)==2:
          A=sorted(opts[0].items(),key=lambda kv:(-kv[0].bit_count(),kv[1][0]))
          B=sorted(opts[1].items(),key=lambda kv:(-kv[0].bit_count(),kv[1][0]))
          for ma,(ca,pa) in A:
            need=full & ~ma
            for mb,(cb,pb) in B:
              if (mb&need)==need:
                z=(acost+ca+cb,ax,ay,[pa,pb])
                if best is None or z[0]<best[0]:best=z
                break
        else:
          raise RuntimeError("unsupported payload count")
    if best is None:raise RuntimeError("no exact geometry")
    return best,len(T)

def moves(cur,goal,neg,pos):
    if goal is None or cur==goal:return []
    return [pos]*(goal-cur) if goal>cur else [neg]*(cur-goal)

def build_plan(g,ax,ay,payload_goals):
    vx,hy=axes(g);movable=set(g.ayyvxqrhnzw);n=len(g.ayyvxqrhnzw)
    cur=-1 if g.yvifanjrcyu not in g.ayyvxqrhnzw else g.ayyvxqrhnzw.index(g.yvifanjrcyu)
    jobs=[]
    if vx is not None and vx in movable:jobs.append((g.ayyvxqrhnzw.index(vx),ax,None))
    if hy is not None and hy in movable:jobs.append((g.ayyvxqrhnzw.index(hy),None,ay))
    for p,(gx,gy) in zip(g.ouurgkpbbjj,payload_goals):
        jobs.append((g.ayyvxqrhnzw.index(p),gx,gy))
    plan=[]
    for idx,gx,gy in jobs:
        plan += [5]*((idx-cur)%n);cur=idx
        s=g.ayyvxqrhnzw[idx]
        plan += moves(s.x,gx,3,4)
        plan += moves(s.y,gy,1,2)
    return plan

e=a.make('ar25');r=None;actions=[]
print("START","LC",0,"LEVEL",e._game.level_index,flush=True)
while (r is None or r.state.name=="NOT_FINISHED") and (r is None or r.levels_completed<8):
    lc=0 if r is None else r.levels_completed;lev=e._game.level_index
    best,nt=infer(e._game);cost,ax,ay,pp=best
    vx,hy=axes(e._game);movable=set(e._game.ayyvxqrhnzw)
    plan=build_plan(e._game,ax,ay,pp)
    print("PLAN","LEVEL",lev+1,"TARGETS",nt,"COST",cost,"AX",ax,ay,"PAY",pp,
          "PLAN_LEN",len(plan),"CUR_AX",
          None if vx is None else (vx.x,vx in movable),
          None if hy is None else (hy.y,hy in movable),
          "CUR_PAY",[(s.x,s.y) for s in e._game.ouurgkpbbjj],flush=True)
    for z in plan:
        r=e.step(GameAction.from_id(z),data={});actions.append(z)
        if r.state.name!="NOT_FINISHED" or r.levels_completed!=lc:break
    if r.state.name!="NOT_FINISHED":break
    if r.levels_completed!=lc:
        print("ADVANCED","LC",r.levels_completed,"LEVEL",e._game.level_index,"ACTIONS",len(actions),flush=True)
        continue
    if getattr(e._game,"hujpxmlafgh",False):
        r=e.step(GameAction.from_id(7),data={});actions.append(7)
        if r.levels_completed!=lc:
            print("ADVANCED","LC",r.levels_completed,"LEVEL",e._game.level_index,"ACTIONS",len(actions),flush=True)
            continue
    print("FAILED","LEVEL",lev+1,"LC",r.levels_completed,"STATE",r.state.name,flush=True)
    break
print("FINAL","LC",r.levels_completed,"STATE",r.state.name,"ACTIONS",len(actions),flush=True)
print("ACTIONS",actions,flush=True)
