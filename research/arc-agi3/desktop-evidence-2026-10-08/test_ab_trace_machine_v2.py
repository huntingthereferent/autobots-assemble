from ab_family_all_minima import Occurrence
from ab_trace_machine_v2 import build_ab_model_all_sources,summarize

xs=[
 Occurrence("O",(("x",0),("y","L")),"A"),
 Occurrence("O",(("x",1),("y","R")),"B"),
]
m=build_ab_model_all_sources(xs)
print(summarize(m))
print(m.states["O"])
assert m.states["O"].minimal_sources==(("x",),("y",))
for o in xs:assert m.predict(o)==o.future

xor=[
 Occurrence("Q",(("x",0),("y",0)),"E"),
 Occurrence("Q",(("x",0),("y",1)),"O"),
 Occurrence("Q",(("x",1),("y",0)),"O"),
 Occurrence("Q",(("x",1),("y",1)),"E"),
]
q=build_ab_model_all_sources(xor)
assert q.states["Q"].minimal_sources==(("x","y"),)
print("PASS A/B all-sources trace machine")
