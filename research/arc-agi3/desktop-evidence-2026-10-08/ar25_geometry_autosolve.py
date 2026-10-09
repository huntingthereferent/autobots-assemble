from arc_agi import Arcade,OperationMode
from arcengine import GameAction

a=Arcade(operation_mode=OperationMode.NORMAL)
BOOT=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
ACT={-1:3,1:4}
AY={-1:1,1:2}

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
    vx,hy=axes(g)
    cax=None if vx is None else vx.x;cay=None if hy is None else hy.y
    AX=[None] if vx is None else list(range(-2,W+3))
    AY=[None] if hy is None else list(range(-2,H+3))
    payloads=list(g.ouurgkpbbjj);sh=[cells(s) for s in payloads]
    best=None
    for ax in AX:
      for ay in AY:
        opts=[]
        for s,c in zip(payloads,sh):
          by={}
          for x in range(-8,W+8):
            for y in range(-8,H+8):
              m=orbit_bits(c,x,y,ax,ay,TI)
              if not m:continue
              cost=abs(x-s.x)+abs(y-s.y)
              old=by.get(m)
              if old is None or cost<old[0]:by[m]=(cost,(x,y))
          opts.append(by)
        acost=(0 if ax is None else abs(ax-cax))+(0 if ay is None else abs(ay-cay))
        if len(opts)==1:
          for m,(pc,p) in opts[0].items():
            if m==full:
              z=(acost+pc,ax,ay,[p])
              if best is None or z[0]<best[0]:best=z
        elif len(opts)==2:
          A=sorted(opts[0].items(),key=lambda kv:(-kv[0].bit_count(),kv[1][0]))
          B=sorted(opts[1].items(),key=lambda kv:(-kv[0].bit_count(),kv[1][0]))
          maxb=B[0][0].bit_count() if B else 0
          for ma,(ca,pa) in A:
            if ma.bit_count()+maxb < (0 if best is None else len(T)): pass
            need=full & ~ma
            for mb,(cb,pb) in B:
              if (mb&need)==need:
                z=(acost+ca+cb,ax,ay,[pa,pb])
                if best is None or z[0]<best[0]:best=z
                break
        else:
          raise RuntimeError("unsupported payload count")
    if best is None:raise RuntimeError("no exact geometry")
    return best,T

def do(e,z):
    r=e.step(GameAction.from_id(z),data={})
    return r

def select(e,target):
    g=e._game
    cur=-1 if g.yvifanjrcyu not in g.ayyvxqrhnzw else g.ayyvxqrhnzw.index(g.yvifanjrcyu)
    n=len(g.ayyvxqrhnzw)
    k=(target-cur)%n
    for _ in range(k):
        r=do(e,5)
        if r.state.name!="NOT_FINISHED":return r
    return r if k else None

def move_obj(e,idx,gx=None,gy=None):
    r=select(e,idx)
    g=e._game
    s=g.ayyvxqrhnzw[idx]
    if gx is not None:
      while s.x!=gx:
        r=do(e,4 if gx>s.x else 3)
        if getattr(e._game,"hujpxmlafgh",False) or r.state.name!="NOT_FINISHED":return r
        s=e._game.ayyvxqrhnzw[idx]
    if gy is not None:
      while s.y!=gy:
        r=do(e,2 if gy>s.y else 1)
        if getattr(e._game,"hujpxmlafgh",False) or r.state.name!="NOT_FINISHED":return r
        s=e._game.ayyvxqrhnzw[idx]
    return r

e=a.make('ar25');r=None;actions=list(BOOT)
for z in BOOT:r=do(e,z)
print("BOOT",r.levels_completed,e._game.level_index,len(actions),flush=True)

while r.state.name=="NOT_FINISHED" and r.levels_completed<8:
    g=e._game; lev=g.level_index; lc=r.levels_completed
    best,T=infer(g);cost,ax,ay,pp=best
    vx,hy=axes(g)
    print("PLAN","LEVEL",lev+1,"TARGETS",len(T),"COST",cost,"AX",ax,ay,"PAY",pp,
          "CUR_AX",None if vx is None else vx.x,None if hy is None else hy.y,
          "CUR_PAY",[(s.x,s.y) for s in g.ouurgkpbbjj],flush=True)
    # carriers are first in ayy; move only their legal coordinate
    if vx is not None and vx.x!=ax:
        idx=g.ayyvxqrhnzw.index(vx); before=len(actions)
        curx=vx.x
        select_steps=(idx-((-1 if g.yvifanjrcyu not in g.ayyvxqrhnzw else g.ayyvxqrhnzw.index(g.yvifanjrcyu))))%len(g.ayyvxqrhnzw)
        actions += [5]*select_steps + ([4]*(ax-curx) if ax>curx else [3]*(curx-ax))
        r=move_obj(e,idx,gx=ax)
    g=e._game
    if r.state.name!="NOT_FINISHED":break
    vx,hy=axes(g)
    if hy is not None and hy.y!=ay:
        idx=g.ayyvxqrhnzw.index(hy); cury=hy.y
        cur=-1 if g.yvifanjrcyu not in g.ayyvxqrhnzw else g.ayyvxqrhnzw.index(g.yvifanjrcyu)
        ss=(idx-cur)%len(g.ayyvxqrhnzw)
        actions += [5]*ss + ([2]*(ay-cury) if ay>cury else [1]*(cury-ay))
        r=move_obj(e,idx,gy=ay)
    if r.state.name!="NOT_FINISHED":break
    # payloads correspond in ouurg order
    for p,(gx,gy) in zip(list(e._game.ouurgkpbbjj),pp):
        g=e._game
        idx=g.ayyvxqrhnzw.index(p)
        cur=-1 if g.yvifanjrcyu not in g.ayyvxqrhnzw else g.ayyvxqrhnzw.index(g.yvifanjrcyu)
        ss=(idx-cur)%len(g.ayyvxqrhnzw)
        actions += [5]*ss
        sx,sy=p.x,p.y
        actions += ([4]*(gx-sx) if gx>sx else [3]*(sx-gx))
        actions += ([2]*(gy-sy) if gy>sy else [1]*(sy-gy))
        r=move_obj(e,idx,gx=gx,gy=gy)
        if r.state.name!="NOT_FINISHED" or getattr(e._game,"hujpxmlafgh",False):break
    if r.state.name!="NOT_FINISHED":break
    if getattr(e._game,"hujpxmlafgh",False):
        actions.append(7);r=do(e,7)
    if r.levels_completed==lc:
        print("FAILED_TO_ADVANCE","LEVEL",lev+1,"LC",r.levels_completed,"HUJ",getattr(e._game,"hujpxmlafgh",None),flush=True)
        break
    print("ADVANCED","TO_LC",r.levels_completed,"GAME_LEVEL",e._game.level_index,"ACTIONS",len(actions),flush=True)

print("FINAL","LC",r.levels_completed,"STATE",r.state.name,"ACTIONS",len(actions),flush=True)
print("AUTO_ACTIONS",actions,flush=True)
