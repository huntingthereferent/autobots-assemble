"""Predeclared spatial hypothesis derived from retained native counterexamples.

Earlier absent 9->12 block: x=44..47. Later real blocks at word steps
7/8: x=28..35. Test suppression at x>=44, independent of word position.
This threshold is exploratory and frozen before this new native run.
Baseline geometry, occupancy and bottom-row completion stay unchanged;
bottom-row errors remain errors. New words vary ACTION4 count and position.
No game implementation inspection, F3 modification or autonomous policy.
"""
from . import native_sp80_history_condition as experiment


def spatial_condition(predicted, step):
    return {p: colors for p, colors in predicted.items()
            if not (p[0] >= 44 and colors == (9, 12))}


if __name__ == "__main__":
    experiment.WORDS = ("444445444", "445444444", "554444444", "444554444")
    experiment.CONDITION_DESCRIPTION = "suppress predicted native 9->12 at target x>=44"
    experiment.condition = spatial_condition
    experiment.main()
