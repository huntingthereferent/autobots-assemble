import runpy
from itertools import combinations
from collections import defaultdict

ns=runpy.run_path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE\test_ab_trace_machine_bp35_dc22.py")
m=ns["m"]  # last built model = dc22

# Recover witness occurrences by rebuilding dc22 helper.
build_game=ns["build_game"]
# existing model hides original occurrences, so independently inspect each split
# via the shallow-tree script namespace instead.
tree=runpy.run_path(r"C:\Users\teepa\arc3\AB_ARC_EVIDENCE\ab_cross_game_shallow_tree.py")
# That script stops at dc22 but doesn't expose occurrence list reliably per game.
print("DC22_SPLITS",[(r,s.retained_names) for r,s in m.states.items() if s.retained_names])
