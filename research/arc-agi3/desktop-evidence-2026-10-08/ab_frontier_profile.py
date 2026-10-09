"""A/B the observed closure-frontier profiles."""

profiles={
    "CD82":{4:1,5:2,6:3},
    "DC22":{4:2,5:3},
    "SK48":{4:3,5:4},
}

for game,p in profiles.items():
    hs=sorted(p)
    deltas=[p[h+1]-p[h] for h in hs if h+1 in p]
    offsets={p[h]-h for h in hs}
    print(game,"PROFILE",p,"DELTAS",deltas,"OFFSETS",offsets)
    assert all(x==1 for x in deltas)
    assert len(offsets)==1

# A/B across profiles:
# preserve the common movement d(H+1)-d(H)=1;
# retain only the boundary offset.
common_step=1
offset={g:next(iter({d-h for h,d in p.items()})) for g,p in profiles.items()}
print("COMMON_STEP",common_step)
print("RETAINED_OFFSETS",offset)

assert offset=={"CD82":-3,"DC22":-2,"SK48":-1}
print("PASS A/B frontier profile: shared +1 movement, game-specific boundary offset")
