"""Mathematical fractal projection paired to real SK48 inverse A/B branches.

No claims about native ARC spatial geometry: 3 contractions are chosen
as a *new* game-generation coordinate model. The phase histories and
their native verification statuses come from actual native test JSONs.
"""
import json,math
from pathlib import Path
from itertools import product
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
d3=json.loads((F/"SK48_AB_REAL_CATEGORY_INVERSE_BRANCH_HOLDOUT_2026-10-08.json").read_text())
d4=json.loads((F/"SK48_AB_INVERSE_DEPTH4_NATIVE_BOUNDARY_2026-10-08.json").read_text())
d5=json.loads((F/"SK48_AB_INVERSE_DEPTH5_FRONTIER_2026-10-08.json").read_text())
assert len(d3["counterexamples"])==0 and len(d3["branches"])==40
assert d4["total"]==81 and d4["continuation_classes"]==1
assert d5["all_paths_tested_for_visible_state"]==243
assert d5["visible_classes"]==1 and len(d5["six_action_holdout_fingerprints"])==1
atoms=((2,),(1,7),(4,7))
d3lookup={tuple(x["symbol"]):x for x in d3["branches"]}
d4lookup={tuple(x["source"]):x for x in d4["witnesses"]}
d5samples={tuple(x["word"]):x for x in d5["sampled_records"]}
levels={}
for n in range(6):
 nodes=[]
 for word in product(range(3),repeat=n):
  acts=[a for k in word for a in atoms[k]]
  lo=sum(2*k/5**(j+1) for j,k in enumerate(word))
  hi=lo+1/5**n
  if n<=3:
   assert d3lookup[word]["history"]==acts
   assert d3lookup[word]["matched_categories"]==[n]
   status="native 20 suffixes of length 4"
  elif n==4:
   assert d4lookup[word]["actions"]==acts
   status="native 8 suffixes of length 5"
  else:
   status=("native public-state and sampled 6-action futures"
       if word in d5samples else "native public-state only")
  nodes.append({"code":list(word),"native_action_history":acts,
      "projection_interval":[round(lo,12),round(hi,12)],
      "witness_scope":status})
 ordered=sorted(x["projection_interval"] for x in nodes)
 assert all(ordered[i][1] < ordered[i+1][0] for i in range(len(ordered)-1))
 assert len(nodes)==3**n
 levels[n]={"branch_count":len(nodes),"interval_width":5**(-n),
 "total_projected_length":(3/5)**n,"nodes":nodes}
 print("FRACTAL_PROJECTION",n,"HISTORIES",len(nodes),"VISIBLE_EVIDENCE",
       status,"TOTAL_LENGTH",round((3/5)**n,6),flush=True)
dimension=math.log(3)/math.log(5)
obj={"status":"tested mathematical projection, native source branches",
 "native_game_spatial_fractal_evidence":False,
 "real_witness_generators":[list(x) for x in atoms],
 "symbolic_inverse_fiber":"H_(n+1) = union_i {h concatenated with generator_i : h in H_n}",
 "projected_geometry":"f_i(x)=(x+2i)/5; i=0,1,2",
 "projected_limit_set":"K = f_0(K) union f_1(K) union f_2(K), IF indefinite generator reuse is admitted",
 "conditional_hausdorff_dimension":dimension,
 "levels":levels,
 "native_witness_files":[
 "SK48_AB_REAL_CATEGORY_INVERSE_BRANCH_HOLDOUT_2026-10-08.json",
 "SK48_AB_INVERSE_DEPTH4_NATIVE_BOUNDARY_2026-10-08.json",
 "SK48_AB_INVERSE_DEPTH5_FRONTIER_2026-10-08.json"],
 "warnings":["At depth 5 only 24 of 243 paths have tested six-action futures",
 "Spatial contractions are a NEW modeling choice, not ARC's native physics",
 "Indefinite continuation and scale invariance are NOT verified by finite games"]}
out=F/"SK48_AB_INVERTED_FRACTAL_PROJECTION_2026-10-08.json"
out.write_text(json.dumps(obj,indent=2),encoding="utf-8")
print("FRACTAL_MATH_PASS","DIM",dimension,"LEVEL5",len(levels[5]["nodes"]),
  "SAMPLED",len(d5samples),"SAVED",out,flush=True)
