from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import random,copy
P1=(4,4,4,1,1,1,4,3,2,2,4,3,1,4);P2=(4,4,4,1,1,4,4,1,4,3,3,1,4,4,3,3,3,3,1,4,4,1,4,2,4,3,3,2,4,4);P3=(1,1,4,1,4,1,4,2,2,3,2,4,4,4,4,1,3,3,3,3,1,1,1,4,2,2,2,3,1,1,1,1,4);P4=(1,1,3,4,1,4,1,1,3,2,3,3,2,2,2,4,4,4,1,1,3,3,1,4,2,3,1)
root=Arcade(operation_mode=OperationMode.NORMAL).make('sk48')
for z in P1+P2+P3+P4:root.step(GameAction.from_id(z),data={})
g=root._game
pads=g.vbelzuaian[:6]
START=(24,4,tuple((int(t.x),int(t.y)) for t in pads))
COLORS=tuple(int(t.pixels[1,1]) for t in pads)
def real(e):
 g=e._game;body=g.mwfajkguqx[g.vzvypfsnt]
 return (int(g.vzvypfsnt.y),len(body),tuple((int(t.x),int(t.y)) for t in g.vbelzuaian[:6]))
def fast(st,z):
 y,L,pads=st
 dy= -6 if z==1 else 6 if z==2 else 0
 dx= 6 if z==4 else -6 if z==3 else 0
 nl=L+(1 if z==4 else -1 if z==3 else 0); ny=y+dy
 if nl<1 or nl>8 or ny<6 or ny>42:return st
 old=[(5+6*i,y) for i in range(L)]
 new=[(5+6*i,ny) for i in range(nl)]
 if z==4 and (5+6*L,y)==(29,24):return st
 if z in (1,2) and any(x==29 and ny==24 for x,yy in old):return st
 if z==3 and L==1:return st
 pcoords={p:i for i,p in enumerate(pads)}
 selected=set()
 if z in (1,2):moving=set(old)|set(new)
 elif z==4:moving=set(old)|set((x+6,y) for x,yy in old)
 else:moving=set(old[1:])|set((x-6,y) for x,yy in old[1:])
 pending=[pcoords[pos] for pos in moving if pos in pcoords]
 while pending:
  i=pending.pop()
  if i in selected:continue
  selected.add(i)
  dest=(pads[i][0]+dx,pads[i][1]+dy)
  if dest in pcoords and pcoords[dest] not in selected:pending.append(pcoords[dest])
 for i in selected:
  nx,nyy=pads[i][0]+dx,pads[i][1]+dy
  if nx<11 or nx>47 or nyy<6 or nyy>42 or (nx,nyy)==(29,24):return st
 pp=tuple((x+dx,y+dy) if i in selected else (x,y) for i,(x,y) in enumerate(pads))
 return (ny,nl,pp)
print('START',START,'COLORS',COLORS,flush=True)
random.seed(921)
fails=0;valid=0
for case in range(40):
 e=copy.deepcopy(root); st=START; seq=[]
 for j in range(25):
  z=random.choice((1,2,3,4))
  e.step(GameAction.from_id(z),data={});st=fast(st,z);seq.append(z)
  r=real(e);valid+=1
  if st!=r:
   print('MISMATCH',case,j,'ACTION',z,'SEQ',tuple(seq),'FAST',st,'REAL',r,flush=True);fails+=1;break
 if fails>=8:break
print('RESULT',valid,'CHECKS',fails,'MISMATCHES',flush=True)
