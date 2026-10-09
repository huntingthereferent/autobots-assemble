"""SK48 native-public visible connection detector, a conservative A/B correction.

Reject color tiles merely on the same row. A tile contributes only when
the horizontal body pattern 1/2 connects continuously from the control
to the left edge of its color block (4 pixels). Preserve full public
frame and action history in caller. No native game imports here.
"""
from _sk48_public_goal_sensor import features as unverified_features, frame
import numpy as np
def connected_features(a):
 raw=unverified_features(a); target=raw["target"]
 found=[]
 for c in raw["candidates"]:
  x,y,b=c["head"]
  colors=[]
  cursor=x+6
  yy=y+2
  for tile_x,tile_color in c["colors_with_x"]:
   if tile_x<cursor:continue
   section=a[yy,cursor:tile_x]
   if not len(section) or not np.all(np.isin(section,(1,2))):
    break
   colors.append(int(tile_color))
   cursor=tile_x+4
  n=0
  for col,wanted in zip(colors,target):
   if col!=wanted:break
   n+=1
  found.append({"head":c["head"],"connected_colors":colors,
                "prefix":n,"head_y":y,"colors_with_x":c["colors_with_x"]})
 return {"reference":target,"controls":raw["heads"],"candidates":found,
         "connected_prefix":max((c["prefix"] for c in found),default=0),
         "unverified_row_alignment_prefix":raw["best_prefix"]}
