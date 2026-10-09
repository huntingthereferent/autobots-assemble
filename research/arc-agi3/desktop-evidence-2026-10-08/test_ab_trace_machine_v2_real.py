import runpy
from ab_trace_machine_v2 import build_ab_model_all_sources,summarize

for name,path in [
 ("DC22",r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE\dc22_ab_all_minima.py"),
 ("CD82",r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE\cd82_ab_all_minima.py"),
]:
 ns=runpy.run_path(path)
 occ=ns["occ"]
 m=build_ab_model_all_sources(occ)
 print(name,summarize(m))
 for ref,s in m.states.items():
  if s.minimal_sources!=((),):
   print(" ",ref,"SOURCES",s.minimal_sources)
 # all training witnesses must be predicted consistently across every source path
 for o in occ:
  assert m.predict(o)==o.future
print("PASS real all-sources A/B prediction on DC22 and CD82")
