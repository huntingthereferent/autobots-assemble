from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import json,numpy as np,pathlib,collections
rec=json.loads(pathlib.Path(r'C:\Users\teepa\arc3\AB_ARC_EVIDENCE\ft09_verified_6of6.json').read_text(encoding='utf-8'))
def parse(frame):
 a=np.asarray(frame.frame[-1],dtype=np.int16).reshape(64,64)
 cand=[]
 for y in range(2,56,2):
  for x in range(2,56,2):
   block=a[y:y+6:2,x:x+6:2]
   if block.shape!=(3,3):continue
   center=int(block[1,1]);allvals=[int(v) for v in block.flatten()];ring=[int(v) for v in np.delete(block.flatten(),4)]
   if center<8 or center==13:continue
   typ=None
   if all(v==center for v in allvals):typ='node'
   elif 6 in allvals and all(v in (center,6) for v in allvals):typ='multi'
   elif all(v in (0,2,3,4) for v in ring) and sum(v in (0,2,3) for v in ring)>=3:typ='ref'
   if typ:cand.append((x,y,typ,center,tuple(tuple(int(q) for q in row) for row in block)))
 lattice=collections.Counter((x%8,y%8) for x,y,t,c,p in cand)
 best=max(lattice,key=lattice.get)
 filtered=[it for it in cand if (it[0]%8,it[1]%8)==best]
 nodes=[(x,y,t,c,p) for x,y,t,c,p in filtered if t!='ref']
 refs=[(x,y,t,c,p) for x,y,t,c,p in filtered if t=='ref']
 swatch=[]
 for y in range(0,12,4):
  vals=collections.Counter(int(v) for v in a[y:y+4,52:64].ravel() if int(v)>=8)
  if vals:
   v,_=vals.most_common(1)[0]
   if v not in swatch:swatch.append(v)
 colors=set(c for x,y,t,c,p in filtered)
 palette=swatch if len(swatch)>=len(colors) else [c for c,k in collections.Counter(c for x,y,t,c,p in nodes).most_common()]+sorted(colors-set(c for x,y,t,c,p in nodes))
 return best,nodes,refs,palette,len(cand),lattice.most_common(4)
import copy
arc=Arcade(operation_mode=OperationMode.NORMAL);env=arc.make('ft09')
for level,lv in enumerate(rec['paths'],1):
 if level<=4:
  for x,y in lv:env.step(GameAction.ACTION6,data={'x':x,'y':y})
  continue
 _,nodes,refs,palette,ct,lat=parse(env.observation_space)
 truth={(x,y):c for x,y,t,c,p in nodes}
 mismatches=[]
 for x,y,t,c,pat in nodes:
  q=copy.deepcopy(env)
  r=q.step(GameAction.ACTION6,data={'x':x,'y':y})
  actual={xx for xx,yy,tt,cc,pp in parse(q.observation_space)[1] if truth.get((xx,yy))!=cc}
  # compare positions not x alone
  actual={(xx,yy) for xx,yy,tt,cc,pp in parse(q.observation_space)[1] if truth.get((xx,yy))!=cc}
  if t=='node':prediction={(x,y)}
  else:prediction={(x,y)} | {(x+(col-1)*8,y+(row-1)*8) for row,line in enumerate(pat) for col,v in enumerate(line) if v==6}
  prediction&=set(truth)
  if prediction!=actual:mismatches.append((x,y,t,prediction,actual,pat))
 print('OPERATOR',level,'NODES',len(nodes),'MULTI',sum(t=='multi' for x,y,t,c,p in nodes),'TESTED',len(nodes),'MISMATCHES',len(mismatches),'FIRST',mismatches[:3],flush=True)
 for x,y in lv:env.step(GameAction.ACTION6,data={'x':x,'y':y})
