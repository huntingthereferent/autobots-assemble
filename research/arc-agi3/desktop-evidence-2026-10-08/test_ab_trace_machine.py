from ab_family_closure import Occurrence
from ab_trace_machine import build_ab_model,summarize

xs=[
 Occurrence("O",(("a",0),("b",0)),"F0"),
 Occurrence("O",(("a",0),("b",1)),"F1"),
 Occurrence("O",(("a",1),("b",0)),"F1"),
 Occurrence("O",(("a",1),("b",1)),"F0"),
 Occurrence("P",(("a",9),("b",9)),"G"),
]
m=build_ab_model(xs)
s=summarize(m)
print(s)
assert m.states["O"].retained_names==("a","b")
assert m.states["P"].retained_names==()
for x in xs:
 assert m.predict(x)==x.future
print("PASS generic trace -> A/B machine")
