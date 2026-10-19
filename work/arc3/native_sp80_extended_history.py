"""Predeclared independent >9-step native SP80 falsification.

Freeze the held-out x>=44 spatial filter and the (11,63) 14->0
step-eight-to-nine timing shift exactly as observed in run 39184092845.
Do not refit the rule on these NEW 11-step words. Test both original
stage-0 and separately attained native stage-1 on two fresh resets
per word. Preserve every native frame, full changed-pixel/color map,
interruption and omission. F3 mathematical source remains unmapped.
"""
from . import native_sp80_history_condition as experiment
from .native_sp80_boundary_timing import boundary_condition

WORDS = (
    "44444445444",
    "44444454444",
    "44445444444",
    "54444444444",
)
assert len(set(WORDS)) == 4 and all(len(word) == 11 for word in WORDS)
assert all(set(word) <= {"4", "5"} for word in WORDS)

if __name__ == "__main__":
    experiment.WORDS = WORDS
    experiment.RESETS = 2
    experiment.CONDITION_DESCRIPTION = (
        "FROZEN prior x>=44 9->12 suppression and (11,63) "
        "14->0 step8-to-step9 shift, tested UNMODIFIED at 11 steps"
    )
    experiment.condition = boundary_condition
    experiment.main()
