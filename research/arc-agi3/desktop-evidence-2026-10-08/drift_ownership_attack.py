"""
Attack the current strongest architecture without changing layers.
Question: can 'relation owns continuation + completion' still drift?
Yes if ownership is merely declared. Test provenance of ownership itself.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Relation:
 name:str
 observed:tuple
 next_move:int|None
 completion:tuple|None
 next_source:str
 completion_source:str

def declared_ownership(r):
 if r.next_move is None or r.completion is None: return "STOP"
 return "RETURN"  # vulnerable: trusts ownership labels

def provenance_ownership(r):
 if r.next_move is None or r.completion is None: return "STOP"
 if r.next_source!="observed_relation": return "DRIFT_NEXT"
 if r.completion_source!="observed_oscillation": return "DRIFT_COMPLETION"
 return "RETURN"

cases=[
 Relation("earned_pair",(8,0),2,("survives",8),"observed_relation","observed_oscillation"),
 Relation("semantic_next",(8,16),3,("survives",8),"interpretation","observed_oscillation"),
 Relation("semantic_close",(8,16),1,("looks_complete",16),"observed_relation","interpretation"),
 Relation("both_declared",(8,21),5,("marker_stable",21),"interpretation","interpretation"),
 Relation("unknown",(8,),None,None,"none","none"),
]
for r in cases:
 print(r.name,
       "declared=",declared_ownership(r),
       "provenance=",provenance_ownership(r),
       "next_src=",r.next_source,
       "close_src=",r.completion_source)

print("\nFAILURE:")
print("Ownership alone is another guardrail if the child can self-assert ownership.")
print("The architecture must carry the witness that GENERATED next/completion,")
print("not booleans saying it owns them.")
