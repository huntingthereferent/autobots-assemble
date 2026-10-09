"""Public-frame-only SK48 object and order sensor. No SDK imports / saved routes.

Grounding: 6x6 control sprite on playing field and 4px color tiles
(8,9,12,14). Bottom reference row and active control row come from pixels.
"""
import numpy as np
TILES=(8,9,12,14)
def frame(o):
 return np.asarray(o.frame[-1],dtype=np.uint8).reshape(64,64)
def head_and_controls(a):
 hits=[]
 for y in range(6,48):
  for x in range(4,55):
   b=int(a[y,x])
   if b not in (6,15):continue
   block=a[y:y+6,x:x+6]
   if (len(block)==6 and np.all(block[0,:]==b)
       and np.all(block[:,0]==b) and int(block[1,1])==0
       and int(block[2,2]) in (0,6)):
    hits.append((x,y,b))
 return hits
def distinct_colors(row,start=0,end=64):
 out=[]
 for x in range(start,min(end,len(row))):
  c=int(row[x])
  if c in TILES and (not out or c!=out[-1][1]):
   out.append((x,c))
 return out
def public_target(a):
 # Palette-coded four-color printed legend at board bottom.
 for y in (57,58,59,60):
  cs=[c for x,c in distinct_colors(a[y],17,57)]
  if len(cs)>=4:return tuple(cs[:4])
 return ()
def features(a):
 target=public_target(a)
 heads=head_and_controls(a)
 candidates=[]
 for x,y,b in heads:
  colors=distinct_colors(a[y+2],x+6,55)
  seq=tuple(c for _,c in colors)
  good=0
  for c,want in zip(seq,target):
   if c!=want:break
   good+=1
  candidates.append({"head":(x,y,b),"attached_row":seq,
    "matched_prefix":good,
    "colors_with_x":colors,"has_4_colors":len(seq)>=4})
 return {"target":target,"heads":heads,
         "candidates":candidates,
         "best_prefix":max((c["matched_prefix"] for c in candidates),default=0),
         "visible_target_remaining":sum(int(c) in TILES for c in a[25,30:54:6])}
