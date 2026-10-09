# Reuse the reach/capture helper and test repeated public observations over a longer local trajectory.
exec(open(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE\cn04_hidden_phase_action_response.py").read().split("states={}")[0])
import copy
root=reach_l5()
sp=[s for s in root._game.current_level.get_sprites() if s.is_visible]
root._game.swfljqaiqu(sp[0])
p=copy.deepcopy(root)
rows=[]
for k in range(24):
 rr=p.step(GameAction.from_id(7),data={})
 cur=fh(rr)
 outs=[]
 for z in [1,2,3,4,5]:
  q=copy.deepcopy(p);nr=q.step(GameAction.from_id(z),data={});outs.append(fh(nr))
 rows.append((k,cur,tuple(outs)))
 nr=p.step(GameAction.from_id(5),data={})
 if nr.state.name!="NOT_FINISHED":break

from collections import defaultdict
for L in range(0,5):
 tab=defaultdict(set)
 for t,(k,cur,outs) in enumerate(rows):
  hist=tuple(rows[j][1] for j in range(max(0,t-L),t)) if L else ()
  tab[(hist,cur)].add(outs)
 bad={k:v for k,v in tab.items() if len(v)>1}
 print("H",L,"AMBIG",len(bad))
 if bad:
  for key,v in list(bad.items())[:3]:print(" ",key,"N",len(v))
 else:
  print("MIN",L);break
print("NROWS",len(rows))
# Print every occurrence of the ambiguous public frame.
for t,row in enumerate(rows):
 if row[1]=="b8e5aebd8004":
  print("B8",t,"PREV",rows[t-1][1] if t else None,"OUTS",row[2])
