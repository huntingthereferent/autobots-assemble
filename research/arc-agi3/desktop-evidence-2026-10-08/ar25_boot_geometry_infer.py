from arc_agi import Arcade,OperationMode
from arcengine import GameAction
a=Arcade(operation_mode=OperationMode.NORMAL)
FIRST=[3]*5+[2]*10

def cells(s):
 return [(dx,dy) for dy,row in enumerate(s.pixels) for dx,v in enumerate(row) if int(v)>=0]
def axes(g):
 vx=next((s for s in g.jtkyjqznbnp if "0054kgxrvfihgm" in s.tags),None)
 hy=next((s for s in g.jtkyjqznbnp if "0002nuguepuujf" in s.tags),None)
 return vx,hy
def ob(c,x,y,ax,ay,TI):
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
 full=(1<<len(T))-1;W,H=g.dqwpuqcubca,g.height;vx,hy=axes(g)
 movable=set(g.ayyvxqrhnzw)
 AX=[None] if vx is None else (list(range(-2,W+3)) if vx in movable else [vx.x])
 AY=[None] if hy is None else (list(range(-2,H+3)) if hy in movable else [hy.y])
 best=None
 for ax in AX:
  for ay in AY:
   opts=[]
   for s in g.ouurgkpbbjj:
    by={}
    c=cells(s)
    for x in range(-8,W+8):
     for y in range(-8,H+8):
      m=ob(c,x,y,ax,ay,TI)
      if not m:continue
      cost=abs(x-s.x)+abs(y-s.y)
      if m not in by or cost<by[m][0]:by[m]=(cost,(x,y))
    opts.append(by)
   ac=(0 if vx is None or vx not in movable else abs(ax-vx.x))+(0 if hy is None or hy not in movable else abs(ay-hy.y))
   if len(opts)==1:
    for m,(pc,p) in opts[0].items():
     if m==full:
      z=(ac+pc,ax,ay,[p])
      if best is None or z[0]<best[0]:best=z
 return best,T
for tag,prefix in [("L1",[]),("L2",FIRST)]:
 e=a.make('ar25');r=None
 for z in prefix:r=e.step(GameAction.from_id(z),data={})
 b,T=infer(e._game)
 vx,hy=axes(e._game)
 print(tag,"LC",0 if r is None else r.levels_completed,"INFER",b,"TARGETS",len(T),
       "CUR_AX",None if vx is None else (vx.x,vx in e._game.ayyvxqrhnzw),
       None if hy is None else (hy.y,hy in e._game.ayyvxqrhnzw),
       "PAY",[(s.x,s.y) for s in e._game.ouurgkpbbjj])
