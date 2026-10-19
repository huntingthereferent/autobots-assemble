"""Predeclared held-out boundary timing test; empirical candidate, not mechanism.
Freeze spatial x>=44 suppression. At step 8 omit (11,63):14->0;
at step 9 add that transition. New native words below, two fresh level
pairs each. Preserve unmodified baseline and all errors. No F3 changes.
"""
from . import native_sp80_history_condition as experiment
from .native_sp80_spatial_condition import spatial_condition

def boundary_condition(predicted, step):
    candidate = spatial_condition(predicted, step)
    if step == 8 and candidate.get((11,63)) == (14,0):
        del candidate[(11,63)]
    if step == 9:
        candidate[(11,63)] = (14,0)
    return candidate

if __name__ == "__main__":
    experiment.WORDS = ("444444454", "444454444", "454444444", "544444444")
    experiment.CONDITION_DESCRIPTION = "spatial suppression plus (11,63):14->0 shifted from step8 to step9"
    experiment.condition = boundary_condition
    experiment.main()
