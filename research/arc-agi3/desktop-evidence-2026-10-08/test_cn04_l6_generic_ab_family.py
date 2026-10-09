import runpy
from ab_family_closure import Occurrence,ab_family

ns=runpy.run_path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE\cn04_l6_predictive_history_scan.py")
allrows=ns["allrows"]

for obj,rows in allrows.items():
    occ=[]
    for t,(cur,future) in enumerate(rows):
        rel=tuple(
            (f"prev{i}", rows[t-i][0] if t-i>=0 else None)
            for i in range(1,6)
        )
        occ.append(Occurrence(cur,rel,future))
    states=ab_family(occ)
    split={k:v for k,v in states.items() if v.retained_names}
    print("OBJ",obj,"SPLIT",len(split))
    for ref,s in split.items():
        print(" ",ref,"=>",s.retained_names)
        assert s.retained_names==("prev1",), (obj,ref,s)
print("PASS real Level-6 trajectories through generic A/B family closure")
