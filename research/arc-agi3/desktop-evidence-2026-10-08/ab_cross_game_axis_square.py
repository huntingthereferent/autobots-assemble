"""Cross-game A/B square over reusable source-family referents."""

G=(("prev_action1",),)
R=(
    ("prev_action2",),
    ("prev_obs1",),
    ("prev_obs2",),
)

games={
    "collapse": frozenset(),
    "g50t": frozenset({"G"}),
    "lf52": frozenset({"G"}),
    "dc22": frozenset({"R"}),
    "cd82": frozenset({"G","R"}),
}

print("AXIS_G",G)
print("AXIS_R",R)
for k,v in games.items():print(k,v)

# Witnessed square.
assert games["collapse"]==frozenset()
assert games["g50t"]==games["lf52"]==frozenset({"G"})
assert games["dc22"]==frozenset({"R"})
assert games["cd82"]==frozenset({"G","R"})

# A/B movements between corners preserve shared axes and expose only changed axes.
def ab_axes(a,b):
    shared=a & b
    only_a=a-b
    only_b=b-a
    return shared,only_a,only_b

pairs=[
 ("collapse","g50t"),
 ("collapse","dc22"),
 ("g50t","cd82"),
 ("dc22","cd82"),
 ("g50t","dc22"),
]
for a,b in pairs:
    print("AB",a,b,"=>",ab_axes(games[a],games[b]))

assert ab_axes(games["collapse"],games["g50t"])==(frozenset(),frozenset(),frozenset({"G"}))
assert ab_axes(games["collapse"],games["dc22"])==(frozenset(),frozenset(),frozenset({"R"}))
assert ab_axes(games["g50t"],games["cd82"])==(frozenset({"G"}),frozenset(),frozenset({"R"}))
assert ab_axes(games["dc22"],games["cd82"])==(frozenset({"R"}),frozenset(),frozenset({"G"}))
assert ab_axes(games["g50t"],games["dc22"])==(frozenset(),frozenset({"G"}),frozenset({"R"}))

print("PASS witnessed 2-axis A/B square")
