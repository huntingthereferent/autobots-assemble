"""SK48 Level7 POSITIVE REFERENCE, separated from independent exploration.
Native public observation and selectable-control coordinates only.
Previous successful P7 route used as calibration, not blind discovery.
"""
from pathlib import Path
import ast,json,hashlib,logging
from _sk48_native_public_stage_harness import enter,run_level,F
from _sk48_public_goal_sensor import frame
logging.disable(logging.CRITICAL)
tree=ast.parse((F/"_tmp_sk48_complete_replay.py").read_text())
ref=list(next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="P7" for t in n.targets)))
out=[]
for trial in range(2):
 e,o,prior=enter(7,selector=trial)
 root=hashlib.sha256(frame(o).tobytes()).hexdigest()
 o,n,switches=run_level(e,o,ref,7)
 row={"trial":trial,"L7_first_win_at":n,"level":int(o.levels_completed),
      "L7_entry_sha":root,"switches":switches,
      "prior_consumed":[x[1] for x in prior]}
 out.append(row)
 print("L7_REFERENCE_PUBLIC",row,flush=True)
dest=F/"sk48_l7_positive_reference_public_control.json"
dest.write_text(json.dumps({"source":"saved P7 positive sequence ONLY reference-assisted calibration",
  "P7":ref,"trials":out},indent=2),encoding="utf-8")
print("SAVED",dest,flush=True)
