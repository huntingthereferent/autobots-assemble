from ab_source_divergence import SourcePath,ProvenanceState,refine_sources

p1=SourcePath(("prev_action2",),(4,))
p2=SourcePath(("prev_obs1",),("X",))
p3=SourcePath(("prev_obs2",),("Y",))
S=ProvenanceState("R","C",(p1,p2,p3))

# p1/p2 remain equivalent, p3 develops a different continuation.
res=refine_sources(S,{p1:"F",p2:"F",p3:"G"})
print("DIVERGE",res)
# A/B should retain only the source relation needed to distinguish the futures.
assert res.minimal_separator_sets in (
    (("source_names",),),
    (("source_values",),),
    (("source_names",),("source_values",)),
)
print("PASS former witness-source equivalence can itself be A/B-refined")
