import runpy
ns=runpy.run_path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE\ar25_end_to_end_geometry_solver.py")
assert ns["r"].levels_completed == 8, ns["r"].levels_completed
assert ns["r"].state.name == "WIN", ns["r"].state.name
assert len(ns["actions"]) <= 268, len(ns["actions"])
print("PASS AR25 geometry promotion",ns["r"].levels_completed,ns["r"].state.name,len(ns["actions"]))
