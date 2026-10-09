"""SK48 public A/B prefix permutation test (no private game reads).

Conjecture: permutations of four ACTION4 and three ACTION1 moves
have the same continuation under the independently discovered suffix.
Only actual native frames and game completion count as evidence.
"""
from arc_agi import Arcade,OperationMode
from arcengine import GameAction
from itertools import combinations
from collections import defaultdict,Counter
from pathlib import Path
import copy,hashlib,json,numpy as np,logging
logging.disable(logging.CRITICAL)
root=Arcade(operation_mode=OperationMode.NORMAL).make("sk48")
tail=(3,2,2,4,3,1,4)
entries=[]
for up_spots in combinations(range(7),3):
 prefix=tuple(1 if i in up_spots else 4 for i in range(7))
 env=copy.deepcopy(root)
 for a in prefix:
  obs=env.step(GameAction.from_id(a),data={})
 before_tail=hashlib.sha256(np.asarray(obs.frame[-1],dtype=np.uint8).tobytes()).hexdigest()
 for a in tail:
  obs=env.step(GameAction.from_id(a),data={})
 entries.append({"prefix":prefix,
                 "prefix_frame_sha256":before_tail,
                 "level_after":int(obs.levels_completed),
                 "status_after":obs.state.name,
                 "end_frame_sha256":hashlib.sha256(np.asarray(obs.frame[-1],dtype=np.uint8).tobytes()).hexdigest()})
bins=defaultdict(list)
for x in entries:bins[x["prefix_frame_sha256"]].append(x)
success=[x for x in entries if x["level_after"]>=1]
print("RESULT total",len(entries),"unique_prefix_frames",len(bins),
      "wins_at_14",len(success),"completion_counts",dict(Counter(x["level_after"] for x in entries)),flush=True)
for x in entries:
 print("PREFIX","".join(str(z) for z in x["prefix"]),
       "L1",x["level_after"],"PREFIX_CLASS",x["prefix_frame_sha256"][:9],
       "END",x["end_frame_sha256"][:9],flush=True)
p=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE\sk48_level1_public_ab_permutations.json")
p.write_text(json.dumps({"game":"sk48",
                         "experiment":"A/B permutations of 3 UP and 4 RIGHT then common suffix",
                         "actions_tail":tail,"private_engine_reads":False,
                         "results":entries,"unique_prefix_classes":len(bins),
                         "success_count":len(success)},indent=2),encoding="utf-8")
print("SAVED",p,flush=True)
