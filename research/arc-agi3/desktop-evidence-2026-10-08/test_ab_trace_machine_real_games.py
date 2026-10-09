import runpy
from ab_family_closure import Occurrence
from ab_trace_machine import build_ab_model,summarize

# --- CN04 Level 6 ---
cn=runpy.run_path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE\cn04_l6_predictive_history_scan.py")
allrows=cn["allrows"]
cn_occ=[]
for obj,rows in allrows.items():
    for t,(cur,future) in enumerate(rows):
        rel=tuple((f"prev{i}",rows[t-i][0] if t-i>=0 else None) for i in range(1,6))
        cn_occ.append(Occurrence((obj,cur),rel,future))
cn_model=build_ab_model(cn_occ)
print("CN04",summarize(cn_model))
assert all(len(v)==1 for v in cn_model.table.values())

# --- CD82 depth-4 public tree ---
cd=runpy.run_path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE\cd82_ab_predictive_table_depth4.py")
cd_occ=cd["occ"]
cd_model=build_ab_model(cd_occ)
s=summarize(cd_model)
print("CD82",s)
assert any(len(st.retained_names)>1 for st in cd_model.states.values())
assert all(len(v)==1 for v in cd_model.table.values())

print("PASS same generic A/B trace machine on CN04 and CD82")
