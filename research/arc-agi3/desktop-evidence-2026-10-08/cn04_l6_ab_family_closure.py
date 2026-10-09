import runpy
from collections import defaultdict
ns=runpy.run_path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE\cn04_l6_predictive_history_scan.py")
allrows=ns["allrows"]

def ab_family(rows,max_depth=6):
    # Each occurrence: same current public referent may have different future vector.
    by=defaultdict(list)
    for t,(cur,future) in enumerate(rows):
        rel={}
        for depth in range(1,max_depth+1):
            rel[f"prev{depth}"]=rows[t-depth][0] if t-depth>=0 else None
        by[cur].append((t,future,rel))

    promoted={}
    for cur,occ in by.items():
        futures={x[1] for x in occ}
        if len(futures)<=1:
            promoted[cur]=()
            continue

        # A/B over the witness family: smallest relation subset whose value-tuples
        # make continuation deterministic.
        names=[f"prev{i}" for i in range(1,max_depth+1)]
        chosen=None
        from itertools import combinations
        for n in range(1,len(names)+1):
            for subset in combinations(names,n):
                buckets=defaultdict(set)
                for t,fut,rel in occ:
                    key=tuple(rel[x] for x in subset)
                    buckets[key].add(fut)
                if all(len(v)==1 for v in buckets.values()):
                    chosen=subset
                    break
            if chosen:break
        promoted[cur]=chosen
    return promoted

for obj,rows in allrows.items():
    promoted=ab_family(rows)
    amb={o:r for o,r in promoted.items() if r}
    print("OBJ",obj,"RAW",len(set(o for o,f in rows)),"AB_SPLITS",len(amb))
    for obs,rels in amb.items():
        print(" ",obs,"=>",rels)
        assert rels==("prev1",), (obj,obs,rels)

print("PASS Level-6 A/B family closure: every witnessed public collision closes with one retained relation")
