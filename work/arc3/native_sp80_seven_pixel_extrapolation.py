"""Prospective native SP80 seven-pixel spacing EXTRAPOLATION, not mechanism.

Previous actual original-game 17-action study identified recurring
single-pixel advances when a naive alternation predicts two:
  x=10 at step8; x=17 at step13.
Those are DISCOVERY coordinates and not validation samples.

New falsifiable extension: if the PRE-action row63 frontier reaches an
UNOBSERVED location x >= 24 with (x-10) mod 7 == 0, predict width1
instead of ALT's width2; otherwise leave the original ALT unchanged.
Run 26-step new public-game action words; freeze all old X3, ALT, ONE,
old absolute-position clock and 64x64 native stage-transfer comparators.
Score separately at previously unseen x >= 24. No native F3 mapping.
"""
from . import native_sp80_width_heldout as experiment

BASELINE = experiment.width_candidates
WORDS = (
    "44444444444444444444444444",
    "44444444445444444444444444",
    "44444444444444444544444444",
    "45454545454545454545454545",
    "44455444455444455444455444",
    "54444444445444444445444444",
)
assert len(WORDS) == len(set(WORDS)) == 6
assert all(len(w) == 26 and set(w) <= {"4", "5"} for w in WORDS)


def extrapolated_width_candidates(x, previous_width):
    candidate = BASELINE(x, previous_width)
    old_alt = candidate["ALT_previous_observed_width"]
    # The exceptional threshold begins AFTER the earlier 17-step sample,
    # so earlier discovery-site agreement is never counted as held-out proof.
    candidate["SEVEN_PIXEL_EXTRAPOLATION"] = (
        1 if old_alt == 2 and x >= 24 and (x - 10) % 7 == 0
        else old_alt
    )
    return candidate


if __name__ == "__main__":
    experiment.WORDS = WORDS
    experiment.RESETS = 2
    experiment.width_candidates = extrapolated_width_candidates
    experiment.main()
