"""Explicit composition of DISTINCT selected centralizer symmetries.

All results concern the declared two-generator triangular F3 systems.
Each selected lift commutes with generators A and B. Two DIFFERENT lifts
with the same coupling law need not commute WITH EACH OTHER.

The difference between two fifth-coordinate potentials is invariant
under B, hence constant on each connected component of the 27-vertex
compatibility graph. The lower centralizer C permutes those components.
Selected lifts commute precisely when their difference is invariant
under that component permutation. A noncommuting pair remains
composable as a WORD of explicit factors, and is a valid centralizer
map, but it is not silently identified with either cyclic subgroup.

Mixed arrows retain an underlying coupling law + distinguished point as
their objects and chosen symmetry/gauge factors as their morphisms.
Arrows between different coupling laws require a separate, genuinely
proved intertwining map; this module does not invent one.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from itertools import product

from .pointed_coupling_classification import (
    CouplingLaw, SelectedSymmetry, VERTICES, INDEX, F3, _field,
    _tuple_of, inspect_coupling, select_symmetry,
)

State=tuple[int,...]


def _state(value:State)->None:
    if type(value) is not tuple or len(value)<3:
        raise ValueError("state must have at least three F3 coordinates")
    for digit in value:
        _field(digit)


@dataclass(frozen=True)
class ComponentAction:
    """Exact permutation induced by the lower symmetry on B-components."""
    law:CouplingLaw
    component_of:tuple[int,...]
    permutation:tuple[int,...]

    @property
    def component_count(self)->int:
        return len(self.permutation)

    @property
    def action_type(self)->str:
        if self.component_count==1:return "CONNECTED"
        if self.permutation==tuple(range(self.component_count)):
            return "COMPONENTWISE_FIXED"
        return "COMPONENT_CYCLE"


@lru_cache(maxsize=8192)
def component_action(law:CouplingLaw)->ComponentAction:
    report=inspect_coupling(law)
    labels=report.component_index
    if labels is None or len(labels)!=27:
        raise AssertionError("the coupling law lost its full graph components")
    m=report.component_count
    target={}
    for state in VERTICES:
        i=labels[INDEX[state]]
        moved=law.lower_symmetry(state)
        j=labels[INDEX[moved]]
        if i in target and target[i]!=j:
            raise AssertionError("lower centralizer does not permute B-components")
        target[i]=j
    perm=tuple(target[i] for i in range(m))
    if set(perm)!=set(range(m)):
        raise AssertionError("component action is not a permutation")
    return ComponentAction(law,labels,perm)


@dataclass(frozen=True)
class GaugeTranslation:
    """A B-invariant vertical translation, with actual component constants."""
    law:CouplingLaw
    constants:tuple[int,...]

    def __post_init__(self)->None:
        _tuple_of(self.constants,component_action(self.law).component_count,
                  "B-component translation constants")

    def map_state(self,state:State)->State:
        _state(state)
        if len(state)<5:
            return state
        result=list(state)
        components=component_action(self.law).component_of
        result[4]=(result[4]+self.constants[components[INDEX[tuple(state[1:4])]]])%3
        return tuple(result)

    def inverse(self)->"GaugeTranslation":
        return GaugeTranslation(self.law,tuple((-a)%3 for a in self.constants))


@dataclass(frozen=True)
class CommutatorCertificate:
    """Literal pointwise fifth-coordinate difference between two compositions."""
    first:SelectedSymmetry
    second:SelectedSymmetry
    component_permutation:tuple[int,...]
    relative_gauge:tuple[int,...]
    differences:tuple[int,...]
    commutes:bool
    witness:State|None
    first_after_second:State|None
    second_after_first:State|None

    def replay(self)->bool:
        return compare_selected(self.first,self.second)==self


def compare_selected(first:SelectedSymmetry,
                     second:SelectedSymmetry)->CommutatorCertificate:
    if not isinstance(first,SelectedSymmetry) or not isinstance(second,SelectedSymmetry):
        raise TypeError("each compared operation must be a proved selected symmetry")
    if first.law!=second.law:
        raise ValueError("different coupling laws require a separate intertwining map")
    structure=component_action(first.law)
    differences=tuple((second.correction[i]-first.correction[i])%3
                      for i in range(27))
    constants=[None]*structure.component_count
    for j,group in enumerate(structure.component_of):
        value=differences[j]
        if constants[group] is None:
            constants[group]=value
        elif constants[group]!=value:
            raise AssertionError("the difference is not B-invariant")
    if any(value is None for value in constants):
        raise AssertionError("missing graph component")
    exact=tuple(
        (differences[INDEX[s]] -
         differences[INDEX[first.law.lower_symmetry(s)]])%3
        for s in VERTICES)
    perm=structure.permutation
    criterion=all(constants[i]==constants[perm[i]]
                  for i in range(len(perm)))
    commutes=not any(exact)
    if criterion!=commutes:
        raise AssertionError("component criterion and exact commutator disagree")
    example=next((s for s in VERTICES
                  if exact[INDEX[s]]!=0),None)
    witness=(0,)+example+(0,) if example is not None else None
    lhs=(first.centralizer(second.centralizer(witness))
         if witness is not None else None)
    rhs=(second.centralizer(first.centralizer(witness))
         if witness is not None else None)
    if witness is not None:
        if lhs[:4]!=rhs[:4] or (lhs[4]-rhs[4])%3!=exact[INDEX[example]]:
            raise AssertionError("the literal commutator witness failed")
    return CommutatorCertificate(first,second,perm,tuple(constants),exact,
                                commutes,witness,lhs,rhs)


@dataclass(frozen=True)
class SymmetryFactor:
    """Literal power of one specifically selected centralizer symmetry."""
    selected:SelectedSymmetry
    exponent:int

    def __post_init__(self)->None:
        if type(self.exponent) is not int or not 0<=self.exponent<self.selected.order:
            raise ValueError("exponent does not belong to this selected cyclic subgroup")

    @property
    def law(self)->CouplingLaw:
        return self.selected.law

    def map_state(self,state:State)->State:
        return self.selected.power(state,self.exponent)

    def inverse(self)->"SymmetryFactor":
        return SymmetryFactor(self.selected,(-self.exponent)%self.selected.order)


@dataclass(frozen=True)
class GaugeFactor:
    """Literal vertical gauge translation on the same underlying system."""
    translation:GaugeTranslation

    @property
    def law(self)->CouplingLaw:
        return self.translation.law

    def map_state(self,state:State)->State:
        return self.translation.map_state(state)

    def inverse(self)->"GaugeFactor":
        return GaugeFactor(self.translation.inverse())


Factor=SymmetryFactor|GaugeFactor


@dataclass(frozen=True)
class PointedLaw:
    """The law and point WITHOUT identifying different selected symmetries."""
    law:CouplingLaw
    mark:tuple[int,int,int,int,int]

    def __post_init__(self)->None:
        if not isinstance(self.law,CouplingLaw):
            raise TypeError("a law must be explicitly witnessed")
        _tuple_of(self.mark,5,"distinguished state")

    def at_depth(self,depth:int)->State:
        if type(depth) is not int or depth<5:
            raise ValueError("the witness requires five coordinates")
        return self.mark+(0,)*(depth-5)


@dataclass(frozen=True)
class MixedPointedArrow:
    """Compositional groupoid arrow retaining every selected factor."""
    source:PointedLaw
    target:PointedLaw
    factors:tuple[Factor,...]

    def __post_init__(self)->None:
        if type(self.factors) is not tuple or not self.factors:
            raise ValueError("a mixed arrow needs actual factors")
        if self.source.law!=self.target.law:
            raise ValueError("a conjugacy between different laws has not been proved")
        for factor in self.factors:
            if not isinstance(factor,(SymmetryFactor,GaugeFactor)):
                raise TypeError("unrecognized transformation factor")
            if factor.law!=self.source.law:
                raise ValueError("a factor has a different underlying coupling law")
        if self.map_state(self.source.mark)!=self.target.mark:
            raise ValueError("the composite does not carry the chosen source point")

    def map_state(self,state:State)->State:
        _state(state)
        for factor in self.factors:
            state=factor.map_state(state)
        return state

    def inverse(self)->"MixedPointedArrow":
        return MixedPointedArrow(
            self.target,self.source,
            tuple(factor.inverse() for factor in reversed(self.factors)))

    def then(self,after:"MixedPointedArrow")->"MixedPointedArrow":
        if self.target!=after.source:
            raise ValueError("the full intermediate pointed law does not match")
        return MixedPointedArrow(
            self.source,after.target,self.factors+after.factors)


def mixed_arrow(source:PointedLaw,
                factors:tuple[Factor,...])->MixedPointedArrow:
    if type(factors) is not tuple or not factors:
        raise ValueError("explicit nonempty factor tuple is required")
    point=source.mark
    for factor in factors:
        if not isinstance(factor,(SymmetryFactor,GaugeFactor)):
            raise TypeError("unknown transformation factor")
        if factor.law!=source.law:
            raise ValueError("different coupling laws have no declared alignment")
        point=factor.map_state(point)
    return MixedPointedArrow(source,PointedLaw(source.law,point),factors)


@dataclass(frozen=True)
class CompositionFamilyCertificate:
    configurations:int
    connected:int
    three_fixed:int
    three_cyclic:int
    ordered_gauge_pairs:int
    commuting_pairs:int
    noncommuting_pairs:int
    status:str


def certify_component_composition()->CompositionFamilyCertificate:
    """Exact component-permutation theorem across all 486 fourth laws.

    For an admitted q2, every compatible correction is the normalized
    solution + one arbitrary constant per graph component. Thus two
    selected symmetries differ by a component-constant gauge. Their
    commutator depends ONLY on the component action, not on q2.
    The counts below use ONE admissible q2=0 per fourth law and
    all pairs of component constant tuples, not different q2 laws.
    """
    from collections import Counter
    stats=Counter()
    for gain in (1,2):
        for Q in product(F3,repeat=3):
            for k1,k2 in product(F3,repeat=2):
                law=CouplingLaw(gain,Q,(0,k1,k2),(0,)*9)
                action=component_action(law)
                stats[action.action_type]+=1
                constants=list(product(F3,repeat=action.component_count))
                for first in constants:
                    for second in constants:
                        diff=tuple((b-a)%3 for a,b in zip(first,second))
                        commute=all(diff[j]==diff[action.permutation[j]]
                                    for j in range(action.component_count))
                        stats["commuting" if commute else "noncommuting"]+=1
                        stats["pairs"]+=1
    correct=(stats==Counter({
        "CONNECTED":468,"COMPONENTWISE_FIXED":6,"COMPONENT_CYCLE":12,
        "commuting":9558,"noncommuting":7776,"pairs":17334}))
    return CompositionFamilyCertificate(
        486,stats["CONNECTED"],stats["COMPONENTWISE_FIXED"],
        stats["COMPONENT_CYCLE"],stats["pairs"],stats["commuting"],
        stats["noncommuting"],
        "EXACT_SELECTED_CENTRALIZER_COMPOSITION" if correct
        else "UNKNOWN_COMPOSITION_COUNTS",
    )
