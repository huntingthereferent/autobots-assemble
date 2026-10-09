"""Intervention-derived affine operator model.

This layer is intentionally more general than reflection:
- controls are coordinates that can be intervened on;
- sources are coordinates of movable source objects;
- dependent observation coordinates are fitted from finite differences;
- affine relations are promoted to operators only after causal validation.

Reflection is one discovered signature:
    dq/dsource = -1
    dq/dcontrol = +2
or, for a fixed operator,
    dq/dsource = -1
with the constant locating the fixed parameter.
"""

from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class CausalAxisRelation:
    dimension: str
    source_gain: int
    control_gain: Optional[int]
    constant: float

    @property
    def movable(self)->bool:
        return self.control_gain is not None

    def dependent(self,source:float,control:Optional[float]=None)->float:
        q=self.source_gain*source+self.constant
        if self.control_gain is not None:
            if control is None:raise ValueError("control value required")
            q += self.control_gain*control
        return q

    def reflection_axis(self,control:Optional[float]=None)->float:
        if self.source_gain != -1:
            raise ValueError("not an involutive reflection signature")
        if self.control_gain is None:
            return self.constant/2
        if self.control_gain != 2:
            raise ValueError("not an involutive reflection signature")
        if control is None:raise ValueError("control value required")
        return control + self.constant/2

    def is_reflection_signature(self)->bool:
        return self.source_gain==-1 and self.control_gain in (None,2)

def infer_fixed_relation(
    dimension:str,
    base_source:float,
    base_dependent:float,
    delta_source:float,
    delta_dependent:float,
)->CausalAxisRelation:
    gain=delta_dependent/delta_source
    if abs(gain-round(gain))<1e-9:gain=int(round(gain))
    c=base_dependent-gain*base_source
    return CausalAxisRelation(dimension,gain,None,c)

def infer_controlled_relation(
    dimension:str,
    base_source:float,
    base_control:float,
    base_dependent:float,
    delta_source:float,
    dq_from_source:float,
    delta_control:float,
    dq_from_control:float,
)->CausalAxisRelation:
    gs=dq_from_source/delta_source
    gc=dq_from_control/delta_control
    if abs(gs-round(gs))<1e-9:gs=int(round(gs))
    if abs(gc-round(gc))<1e-9:gc=int(round(gc))
    c=base_dependent-gs*base_source-gc*base_control
    return CausalAxisRelation(dimension,gs,gc,c)
