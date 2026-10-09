import runpy
ns=runpy.run_path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE\ar25_causal_family_full_solver.py")
r=ns["r"]
assert r.levels_completed == 8, r.levels_completed
assert r.state.name == "WIN", r.state.name
print("PASS causal-family full solver",r.levels_completed,r.state.name)
