"""Causal affine-relation discovery from intervention deltas.

Given a dependent coordinate q and controllable coordinates x_i, estimate
integer finite-difference gains dq/dx_i and recover q = sum_i gain_i*x_i + c.
"""

from dataclasses import dataclass
from typing import Mapping

@dataclass(frozen=True)
class AffineRelation:
    gains: tuple[tuple[str,int], ...]
    constant: int

    def predict(self, **values:int) -> int:
        return sum(g*values[name] for name,g in self.gains)+self.constant

def infer_integer_affine_relation(
    base_q:int,
    base_controls:Mapping[str,int],
    probes:Mapping[str,tuple[int,int]],
) -> AffineRelation:
    """probes[name] = (delta_control, delta_q)."""
    gains=[]
    for name,(dx,dq) in probes.items():
        if dx == 0:
            raise ValueError(f"zero intervention for {name}")
        if dq % dx:
            raise ValueError(f"non-integer gain for {name}: {dq}/{dx}")
        gains.append((name,dq//dx))
    constant=base_q-sum(g*base_controls[name] for name,g in gains)
    return AffineRelation(tuple(gains),constant)
