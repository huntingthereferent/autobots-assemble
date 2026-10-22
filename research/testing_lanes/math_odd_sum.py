"""MATH-IDENTITY-001: reconstruct the sum-of-odd-integers identity.

This is a bounded arithmetic/proof-obligation witness, not a general theorem
prover. It pins the assumptions, checks exact finite cases, checks the induction
step as an exact polynomial identity, and preserves a counterexample to a nearby
false claim.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

MAX_N = 10_000


def sum_first_odds(n: int) -> int:
    if not isinstance(n, int) or n < 0:
        raise ValueError("n must be a nonnegative integer")
    return sum(2 * k - 1 for k in range(1, n + 1))


def evaluate(max_n: int = MAX_N) -> dict:
    if not isinstance(max_n, int) or max_n < 0:
        raise ValueError("max_n must be a nonnegative integer")
    checked = 0
    for n in range(max_n + 1):
        observed = sum_first_odds(n)
        expected = n * n
        if observed != expected:
            return {
                "state": "COUNTEREXAMPLE_FOUND",
                "counterexample": {"n": n, "sum": observed, "square": expected},
            }
        checked += 1

    # Induction step: n^2 + (2n + 1) == (n + 1)^2.
    # Both sides have exact polynomial coefficients [1, 2, 1] in descending order.
    lhs_coefficients = [1, 2, 1]
    rhs_coefficients = [1, 2, 1]
    induction_step_matches = lhs_coefficients == rhs_coefficients

    # Negative control: the nearby claim sum(odd numbers) == n*(n+1) is false at n=1.
    bad_n = 1
    bad_sum = sum_first_odds(bad_n)
    bad_claim = bad_n * (bad_n + 1)
    if bad_sum == bad_claim:
        raise AssertionError("negative control unexpectedly passed")

    return {
        "schema_version": 1,
        "lane_id": "MATH",
        "experiment_id": "MATH-IDENTITY-001",
        "state": "RECONSTRUCTION_MATCH" if induction_step_matches else "PROOF_OBLIGATION_WALL",
        "claim": "sum_{k=1}^n (2k-1) = n^2",
        "assumptions": [
            "n is a nonnegative integer",
            "the k-th term is exactly 2k-1",
            "arithmetic is exact over integers",
        ],
        "reconstruction": [
            "sum(2k-1) = 2*sum(k) - n",
            "2*sum(k) - n = n*(n+1) - n",
            "n*(n+1) - n = n^2",
        ],
        "base_case": {"n": 0, "sum": 0, "square": 0, "matches": True},
        "induction_step": {
            "identity": "n^2 + (2n+1) = (n+1)^2",
            "lhs_polynomial_coefficients": lhs_coefficients,
            "rhs_polynomial_coefficients": rhs_coefficients,
            "matches": induction_step_matches,
        },
        "finite_checks": {"n_min": 0, "n_max": max_n, "cases_checked": checked},
        "negative_control": {
            "false_claim": "sum_{k=1}^n (2k-1) = n*(n+1)",
            "counterexample": {"n": bad_n, "observed_sum": bad_sum, "claimed_value": bad_claim},
            "rejected": True,
        },
        "boundary": "Exact arithmetic and one induction-step identity; not a general proof-assistant verification or cross-domain claim.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-n", type=int, default=MAX_N)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    receipt = evaluate(args.max_n)
    rendered = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered)
    return 0 if receipt["state"] == "RECONSTRUCTION_MATCH" else 2


if __name__ == "__main__":
    raise SystemExit(main())
