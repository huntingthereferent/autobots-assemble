from arc_agi import Arcade,OperationMode
from arcengine import GameAction
import numpy as np
a=Arcade(operation_mode=OperationMode.NORMAL); PRE=[3]*5+[2]*10
e=a.make('ar25');o=None
for z in PRE:o=e.step(GameAction.from_id(z),data={})
B=o.frame[0].copy()
# Inspect exact L2 root for fixed structures that can receive the movable 8-path after first re-expression.
# First get B8.
for z in [7,5]: o=e.step(GameAction.from_id(z),data={})
B8=o.frame[0].copy()
yy,xx=np.where(B8==0); path=set(zip(xx.tolist(),yy.tolist()))
mnx,mny=min(x for x,y in path),min(y for x,y in path)
norm={(x-mnx,y-mny) for x,y in path}
print("PATH bbox",(mnx,max(x for x,y in path),mny,max(y for x,y in path)),"norm",sorted(norm))
# Search whole B8 for exact same support geometry represented by any single non-background color.
# This is correspondence detection for the witnessed movable structure, not arbitrary action search.
for c in sorted(set(map(int,B8.ravel()))):
 if c==9: continue
 pts=set(zip(*[[]]))
 hits=[]
 for oy in range(64-(max(y for x,y in norm)+1)+1):
  for ox in range(64-(max(x for x,y in norm)+1)+1):
   vals=[int(B8[oy+dy,ox+dx]) for dx,dy in norm]
   if all(v==c for v in vals): hits.append((ox,oy))
 print("color",c,"exact-support anchors",hits[:50],"N",len(hits))
# Also find 5-marker counterpart geometry (source L) and its flip at B8.
src={(0,0),(3,0),(6,0),(6,3),(6,6)}
for c in sorted(set(map(int,B8.ravel()))):
 if c==9:continue
 hits=[]
 for oy in range(58):
  for ox in range(58):
   if all(int(B8[oy+dy,ox+dx])==c for dx,dy in src):hits.append((ox,oy))
 print("SRC5 color",c,hits[:30],"N",len(hits))
