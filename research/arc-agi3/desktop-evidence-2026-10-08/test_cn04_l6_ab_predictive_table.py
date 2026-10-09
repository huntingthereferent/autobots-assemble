import runpy
from collections import defaultdict
from ab_family_closure import Occurrence,ab_family,project

ns=runpy.run_path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE\cn04_l6_predictive_history_scan.py")
allrows=ns["allrows"]

total_raw=0
total_ab=0
for obj,rows in allrows.items():
    occ=[]
    for t,(cur,future) in enumerate(rows):
        relations=tuple(
            (f"prev{i}", rows[t-i][0] if t-i>=0 else None)
            for i in range(1,6)
        )
        occ.append(Occurrence(cur,relations,future))

    states=ab_family(occ)
    table=defaultdict(set)
    raw_refs=set()

    for o in occ:
        raw_refs.add(o.referent)
        s=states[o.referent]
        key=project(o,s)
        table[key].add(o.future)

    bad={k:v for k,v in table.items() if len(v)>1}
    assert not bad,(obj,bad)

    total_raw+=len(raw_refs)
    total_ab+=len(table)
    print("OBJ",obj,"RAW_STATES",len(raw_refs),"AB_STATES",len(table),
          "SPLIT_EXTRA",len(table)-len(raw_refs),"DETERMINISTIC",not bad)

print("TOTAL_RAW",total_raw,"TOTAL_AB",total_ab,"EXTRA",total_ab-total_raw)
print("PASS A/B outputs themselves form a deterministic predictive-state table")
