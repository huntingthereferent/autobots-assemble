"""A/B mathematical inverse: quotient fiber reconstruction + projected fractal.

Empirical part: inversion of the existing CD82-shaped A/B continuation
quotient test witness. This is not a new ARC game observation: the
fixture is the existing synthesized-relation test.
Generative part: an explicitly hypothetical contractive IFS, separate
from the ARC evidence. No private ARC engine reads.
"""
from pathlib import Path
import json,math
from ab_relation_synthesis import synthesize_relation,apply_synthesized
from ab_family_all_minima import Occurrence
from ab_source_family_recursive_object import normalize_sources
F=Path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE")
# Exact local CD82-shaped proof-partition and witnessed future-category
# example that was already tested in test_ab_relation_synthesis.py.
proof=((0,),(1,),(2,),(3,6),(4,7),(5,8),(9,),(10,))
future=((0,1),(2,),(3,4,6,7,9,10),(5,8))
label={k:f"F{i}" for i,part in enumerate(future) for k in part}
group=[Occurrence("CD82-shaped fixture",(),label[i]) for i in range(11)]
rel=synthesize_relation("CD82-shaped fixture",proof,group)
assert rel.continuation_partition==future
# q : old proof blocks -> continuation categories
q=dict(rel.proof_to_class)
fibers={i:tuple(sorted(j for j,c in q.items() if c==i))
        for i in range(len(future))}
restored={
 i:tuple(sorted(k for j in js for k in proof[j]))
 for i,js in fibers.items()
}
assert {k for ks in restored.values() for k in ks}==set(range(11))
assert all(restored[i]==future[i] for i in range(len(future)))
assert [len(z) for z in fibers.values()]==[2,1,4,1]
assert sum(map(len,fibers.values()))==len(proof)==8
assert sum(map(len,restored.values()))==11
# Composition A/B categories inverse: C(4) -> proof(8) -> raw (11)
print("AB_QUOTIENT_FORWARD","proof_count",len(proof),
      "continuation_count",len(future),"native_fixture_occurrences",11,flush=True)
print("AB_QUOTIENT_INVERSE","class_to_proof_block_indices",fibers,flush=True)
print("AB_QUOTIENT_INVERSE_OCCURRENCES",restored,flush=True)
# Formula source families. A/B shared residual R is itself a referent:
dc=normalize_sources([("prev_action2",),("prev_obs1",),("prev_obs2",)])
cd=normalize_sources([("prev_action1","prev_action2"),
 ("prev_action1","prev_obs1"),("prev_action1","prev_obs2")])
assert dc.residual==cd.residual and dc.core==()
assert cd.core==("prev_action1",)
print("AB_FAMILY_INVERSE","shared_R",dc.residual.alternatives,
      "DC_CORE",dc.core,"CD_CORE",cd.core,flush=True)
# HYPOTHETICAL GENERATOR: once backward branches are admitted,
# a contractive, repeated rule can have a fractal limit.
# This is a mathematical example, not an inferred SK48/ar25 rule.
intervals=[(0,1)]
counts=[]
for level in range(1,7):
 intervals=sorted(
   [(x/3,y/3) for x,y in intervals]+
   [((x+2)/3,(y+2)/3) for x,y in intervals]
 )
 assert len(intervals)==2**level
 counts.append({"depth":level,"branches":len(intervals),
   "segment_width":1/(3**level),"total_length":(2/3)**level})
print("AB_HYPOTHETICAL_FRACTAL",counts,flush=True)
out=F/"AB_ARC_INVERSE_CATEGORY_TEST_2026-10-08.json"
obj={
 "status":"tested mathematical inversion of existing category witness",
 "source_fixture":"test_ab_relation_synthesis.py CD82-shaped witness, not a fresh native ARC run",
 "native_game_invoked":False,
 "proven_witness_inverse":{
  "continuation_classes":4,"proof_blocks":8,"occurrences":11,
  "class_to_proof_block_indices":fibers,
  "class_to_occurrences":restored,
  "checked_right_and_left_incidence":True},
 "family_factorization":{"DC22_core":list(dc.core),"CD82_core":list(cd.core),
   "shared_residual":[list(x) for x in dc.residual.alternatives]},
 "hypothetical_contracting_generator":{
  "assumption":"two contracting branches x/3 and (x+2)/3; NOT observed in ARC",
  "depth_counts":counts,"not_an_ARC_mechanic":True
 }}
out.write_text(json.dumps(obj,indent=2),encoding="utf-8")
print("A_B_INVERSE_TEST_PASS","WITNESS_FIBERS",len(fibers),
      "RECONSTRUCTED",sum(map(len,restored.values())),
      "PROJECTED_FRACTAL_DEPTH",len(counts),"SAVED",out,flush=True)
