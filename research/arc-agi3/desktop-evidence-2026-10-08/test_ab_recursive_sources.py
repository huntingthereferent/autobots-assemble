from ab_recursive_sources import PriorAB,lift_prior,recursive_family

# First A/B result: one continuation class witnessed by three equivalent minimal sources.
P=PriorAB(
    referent="R",
    continuation_class="C",
    sources=(("prev_action2",),("prev_obs1",),("prev_obs2",)),
)

# Later evidence reuses the SAME prior A/B state twice, but futures diverge.
A=lift_prior(P,(("new_relation","L"),),"F_left")
B=lift_prior(P,(("new_relation","R"),),"F_right")

s=recursive_family([A,B])[P]
print("SECOND_LAYER",s)
assert s.minimal_separator_sets==( ("new_relation",), )

# The earlier source family survives only as provenance in the referent.
assert s.referent.sources==P.sources
print("PASS recursive A/B preserves prior closure and adds only the new surviving distinction")
