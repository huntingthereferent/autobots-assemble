import runpy
ns=runpy.run_path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE\cn04_empirical_cycle_full_solver_v2.py")
r=ns["r"]
assert r.levels_completed == 6, r.levels_completed
assert r.state.name == "WIN", r.state.name
print("PASS CN04 empirical-cycle full solver",r.levels_completed,r.state.name)
