"""PHY-OSCILLATOR-RESIDUAL-001: numerical damped oscillator vs analytic trace.

Synthetic deterministic numerical-method control only. The analytic curve is
the reference, not an independently measured physical signal.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

OMEGA = 2.0
ZETA = 0.15
T_END = 5.0
TIME_STEPS = (0.04, 0.02, 0.01)


def analytic_x(t: float) -> float:
    alpha = ZETA * OMEGA
    wd = OMEGA * math.sqrt(1.0 - ZETA * ZETA)
    return math.exp(-alpha * t) * (
        math.cos(wd * t) + (alpha / wd) * math.sin(wd * t)
    )


def euler_trace(dt: float) -> list[tuple[float, float]]:
    if dt <= 0 or abs(round(T_END / dt) * dt - T_END) > 1e-10:
        raise ValueError("dt must be positive and divide the fixed horizon exactly")
    x, v, t = 1.0, 0.0, 0.0
    trace = [(t, x)]
    steps = round(T_END / dt)
    for _ in range(steps):
        # Explicit Euler for x' = v; v' = -2*zeta*omega*v - omega^2*x.
        acceleration = -2.0 * ZETA * OMEGA * v - OMEGA * OMEGA * x
        x_next = x + dt * v
        v_next = v + dt * acceleration
        t += dt
        x, v = x_next, v_next
        trace.append((t, x))
    return trace


def rmse_against_analytic(trace: list[tuple[float, float]]) -> float:
    return math.sqrt(sum((x - analytic_x(t)) ** 2 for t, x in trace) / len(trace))


def build_receipt() -> dict:
    results = {}
    for dt in TIME_STEPS:
        trace = euler_trace(dt)
        results[str(dt)] = {
            "dt": dt,
            "samples": len(trace),
            "rmse_vs_analytic": rmse_against_analytic(trace),
            "trace_sha256": hashlib.sha256(
                json.dumps(trace, separators=(",", ":")).encode()
            ).hexdigest(),
        }
    errors = [results[str(dt)]["rmse_vs_analytic"] for dt in TIME_STEPS]
    converges = errors[0] > errors[1] > errors[2]
    return {
        "schema_version": 1,
        "experiment_id": "PHY-OSCILLATOR-RESIDUAL-001",
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "STEP_REFINEMENT_CONVERGES" if converges else "CONVERGENCE_CONTROL_FAILED",
        "model": "x'' + 2*zeta*omega*x' + omega^2*x = 0",
        "parameters": {"omega": OMEGA, "zeta": ZETA, "initial_position": 1.0,
                       "initial_velocity": 0.0, "horizon_seconds": T_END},
        "reference": "closed-form underdamped solution evaluated at Euler sample times",
        "method": "explicit Euler",
        "runs": results,
        "controls": {
            "errors_strictly_decrease_with_step_refinement": converges,
            "all_sample_counts_match_horizon": all(
                results[str(dt)]["samples"] == round(T_END / dt) + 1 for dt in TIME_STEPS
            ),
        },
        "limits": [
            "Synthetic analytic reference only; no independently measured physical signal was used.",
            "This validates a bounded numerical convergence behavior, not a physical model of a real system.",
            "No gravitational-wave event, laboratory trace, or external dataset was fetched.",
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    receipt = build_receipt()
    rendered = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    if receipt["status"] != "STEP_REFINEMENT_CONVERGES":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
