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
arc=Arcade(operation_mode=OperationMode.NORMAL);env=arc.make('ft09')
for idx,lv in enumerate(rec['paths'],1):
 obs=env.observation_space;best,nodes,refs,palette,ct,lattice=parse(obs)
 g=env._game
 real={(s.x*2,s.y*2) for s in g.fhc+g.mou}
 found={(x,y) for x,y,t,c,p in nodes}
 refsreal={(s.x*2,s.y*2) for s in g.gig}
 refsfound={(x,y) for x,y,t,c,p in refs}
 print('PARSE',idx,'GRID',best,'CAND',ct,'LATTICE',lattice,'NODES',len(nodes),'TRUTH',len(real),'MISSED',sorted(real-found),'EXTRA',sorted(found-real),'REFS',len(refs),'TRUTH',len(refsreal),'RMISS',sorted(refsreal-refsfound),'REXTRA',sorted(refsfound-refsreal),'COLORS',palette,'TRUE_PALETTE',g.gqb,flush=True)
 for x,y in lv:env.step(GameAction.ACTION6,data={'x':x,'y':y})
