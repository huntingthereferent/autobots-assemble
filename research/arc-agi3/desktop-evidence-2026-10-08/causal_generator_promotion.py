"""Promote a causal affine relation into a geometric generator.

A discovered 1-D dependent relation
    q = source_gain * p + control_gain * a + c
with source_gain=-1 and control_gain=2
is an involutive reflection about coordinate a+c/2.
"""

from dataclasses import dataclass
from involution_discovery_kernel import AffineMap
from causal_affine_kernel import AffineRelation

@dataclass(frozen=True)
class LearnedGenerator:
    dimension: str
    source_gain: int
    control_gain: int
    constant: int

    def is_reflection_signature(self) -> bool:
        return self.source_gain == -1 and self.control_gain == 2

    def affine_map(self, control_value:int) -> AffineMap:
        if not self.is_reflection_signature():
            raise ValueError("relation is not the learned reflection signature")
        b=self.control_gain*control_value+self.constant
        if self.dimension=="x":
            return AffineMap(-1,0,0,1,b,0,"learned_x_involution")
        if self.dimension=="y":
            return AffineMap(1,0,0,-1,0,b,"learned_y_involution")
        raise ValueError(self.dimension)

def from_relation(dimension:str,relation:AffineRelation,control_name:str,source_name:str)->LearnedGenerator:
    gains=dict(relation.gains)
    return LearnedGenerator(
        dimension=dimension,
        source_gain=gains[source_name],
        control_gain=gains[control_name],
        constant=relation.constant,
    )
