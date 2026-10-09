from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import itertools
a=Arcade(operation_mode=OperationMode.NORMAL)
SOL=[3]*5+[2]*10+[7,5]+[2]*5+[5,3,5]+[2]*3+[5,3]
MEET=[5,5,4,5,7,2,5]
e=a.make('ar25');r=None
for z in SOL+MEET:r=e.step(GameAction.from_id(z),data={})
g=e._game
T={(t.x,t.y) for t in g.fswikrcrdmx}
W,H=g.dqwpuqcubca,g.height
shapes=[]
for s in g.ouurgkpbbjj:
    cells=[(dx,dy) for dy,row in enumerate(s.pixels) for dx,v in enumerate(row) if int(v)>=0]
    shapes.append(cells)
print("BOARD",W,H,"TARGETS",len(T),sorted(T))
print("SHAPES",shapes)
def mask(cells,x,y,axis):
    pts=set()
    for dx,dy in cells:
        px,py=x+dx,y+dy
        if 0<=px<W and 0<=py<H: pts.add((px,py))
        ry=2*axis-py
        if 0<=px<W and 0<=ry<H: pts.add((px,ry))
    return pts&T
# only placements whose direct/reflected footprint hits targets
opts=[]
for cells in shapes:
    arr=[]
    for axis in range(-10,H+11):
      for x in range(-4,W+4):
       for y in range(-4,H+4):
        m=mask(cells,x,y,axis)
        if m: arr.append((axis,x,y,frozenset(m)))
    opts.append(arr)
print("OPTIONS",*[len(x) for x in opts])
# group by axis and retain nondominated masks shortest-ish
for axis in range(-10,H+11):
    A=[o for o in opts[0] if o[0]==axis]
    B=[o for o in opts[1] if o[0]==axis]
    best=(0,None,None,set())
    # unique masks, one placement each
    ua={}
    ub={}
    for o in A: ua.setdefault(o[3],o)
    for o in B: ub.setdefault(o[3],o)
    for ma,oa in ua.items():
      if len(ma)+max((len(m) for m in ub),default=0)<best[0]: continue
      for mb,ob in ub.items():
        u=set(ma)|set(mb); n=len(u)
        if n>best[0]: best=(n,oa,ob,u)
        if n==len(T):
          print("SOLVE_GEOM","axis",axis,"L",(oa[1],oa[2]),"CAP",(ob[1],ob[2]))
          print("COVER",sorted(u)); raise SystemExit
    if best[0]>=20:
      print("AXIS_BEST",axis,best[0],"L",None if not best[1] else best[1][1:3],"CAP",None if not best[2] else best[2][1:3],"MISS",sorted(T-best[3]))
print("NO_STATIC_SOLVE")
