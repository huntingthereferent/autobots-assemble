"""Cyclic Action Engine research entry/exit: re-enter a bounded B-continuation witness.

This integrates the previously local continuation protocol with the
ACTUAL WindowProcess.step and ConstructedEngine handoff. No manual copy
of the transition rule is used. Engine 1's inverse-construction search
is NOT enlarged: these WindowProcess laws must be explicitly supplied
in ConstructedEngine objects, not inferred to have been built by
InverseConstructionEngine.

Current proven scope: all 81 states of x0=2 in F3^5, generator B ONLY,
two-predecessor WindowProcess laws with exactly three coupling tables
and a zero higher tail. A does not preserve this fiber. Return UNKNOWN
at an exhausted budget, DISTINGUISHED for a periodic-count mismatch,
or EQUIVALENT_FOR_B_ONLY after an exact B-intertwining bijection is
constructed and verified. No simultaneous A/B claim is admitted.

Snapshots keep law tables, engine version/history provenance, declared
fiber, fixed-state INDEX sets, continuation budgets and exact conclusion.
Replay recomputes the original observations from actual WindowProcess,
not from stale snapshots. The SHA-256 check catches incidental changes;
it is not an adversarial authentication scheme.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from hashlib import sha256
from itertools import product
import json

from .window_two import WindowProcess
from .engine_one import ConstructedEngine

F3=(0,1,2)
ZERO=(0,)*9
FIBER=tuple((2,*tail) for tail in product(F3,repeat=4))
RELATION="B_ONLY_ON_x0_EQ_2"
OUTCOMES=("UNKNOWN","DISTINGUISHED","EQUIVALENT_FOR_B_ONLY")


def _digest(data:object)->str:
    return sha256(json.dumps(data,sort_keys=True,separators=(",",":")).encode()).hexdigest()


def _encode_process(process:WindowProcess)->dict:
    if not isinstance(process,WindowProcess):
        raise TypeError("continuation requires an actual two-input WindowProcess")
    if len(process.stem)!=3 or process.period!=(ZERO,):
        raise ValueError("admitted five-coordinate grammar is a three-table zero-tail WindowProcess")
    return {"gain":process.gain,
            "stem":[list(row) for row in process.stem],
            "period":[list(row) for row in process.period]}


def _decode_process(data:dict)->WindowProcess:
    if type(data) is not dict or set(data)!= {"gain","stem","period"}:
        raise ValueError("invalid serialized WindowProcess law")
    try:
        world=WindowProcess(data["gain"],tuple(tuple(r) for r in data["stem"]),
                            tuple(tuple(r) for r in data["period"]))
        _encode_process(world)
        return world
    except (TypeError,KeyError,IndexError) as err:
        raise ValueError("invalid source law") from err


def _provenance(engine:ConstructedEngine)->dict:
    if not isinstance(engine,ConstructedEngine):
        raise TypeError("entry requires a real ConstructedEngine handoff")
    _encode_process(engine.law)
    if type(engine.version) is not int or engine.version<0:
        raise ValueError("engine version must be a nonnegative integer")
    if type(engine.phase) is not int or engine.phase<0:
        raise ValueError("invalid engine phase")
    return {"version":engine.version,"history":repr(engine.history),
            "cycle":repr(engine.cycle),"phase":engine.phase}


def _permutation(process:WindowProcess)->tuple[int,...]:
    _encode_process(process)
    indices={state:i for i,state in enumerate(FIBER)}
    images=[process.step(state,"B") for state in FIBER]
    if any(state not in indices for state in images):
        raise ValueError("declared watched fiber is not B-invariant")
    result=tuple(indices[s] for s in images)
    if set(result)!=set(range(81)):
        raise ValueError("B is not bijective on the watched fiber")
    return result


def _cycles(permutation:tuple[int,...])->tuple[tuple[int,...],...]:
    seen=set()
    cycles=[]
    for i in range(len(permutation)):
        if i in seen:continue
        orbit=[]
        state=i
        while state not in seen:
            seen.add(state)
            orbit.append(state)
            state=permutation[state]
        if state!=i:
            raise AssertionError("declared B action is not a permutation")
        cycles.append(tuple(orbit))
    return tuple(cycles)


def _fixed(permutation:tuple[int,...],depth:int)->tuple[int,...]:
    action=tuple(range(len(permutation)))
    for _ in range(depth):
        action=tuple(permutation[i] for i in action)
    return tuple(i for i,x in enumerate(action) if i==x)


def _intertwiner(left:tuple[int,...],right:tuple[int,...])->tuple[int,...]|None:
    by_left:dict[int,list[tuple[int,...]]]=defaultdict(list)
    by_right:dict[int,list[tuple[int,...]]]=defaultdict(list)
    for orbit in _cycles(left):
        by_left[len(orbit)].append(orbit)
    for orbit in _cycles(right):
        by_right[len(orbit)].append(orbit)
    if {n:len(v) for n,v in by_left.items()}!={
            n:len(v) for n,v in by_right.items()}:
        return None
    values=[None]*len(left)
    for length in sorted(by_left):
        for a,b in zip(sorted(by_left[length]),sorted(by_right[length])):
            for original,target in zip(a,b):
                values[original]=target
    h=tuple(values)
    if set(h)!=set(range(81)) or any(
            h[left[i]]!=right[h[i]] for i in range(81)):
        raise AssertionError("constructed map does not intertwine B")
    return h


def _identity(left:WindowProcess,right:WindowProcess,
              left_ref:dict,right_ref:dict)->str:
    return _digest({"scope":RELATION,"generator":"B","domain":FIBER,
                    "left":_encode_process(left),"right":_encode_process(right),
                    "left_source":left_ref,"right_source":right_ref,
                    "left_permutation":_permutation(left),
                    "right_permutation":_permutation(right)})


@dataclass(frozen=True)
class PeriodObservation:
    depth:int
    left_fixed:tuple[int,...]
    right_fixed:tuple[int,...]

    def to_dict(self)->dict:
        return {"depth":self.depth,"left_fixed":list(self.left_fixed),
                "right_fixed":list(self.right_fixed)}


@dataclass(frozen=True)
class ContinuationWitness:
    left:WindowProcess
    right:WindowProcess
    left_ref:dict
    right_ref:dict
    source_identity:str
    observations:tuple[PeriodObservation,...]=()
    budgets:tuple[int,...]=()
    status:str="UNKNOWN"
    bijection:tuple[int,...]|None=None
    distinguishing_depth:int|None=None

    @classmethod
    def enter(cls,left_engine:ConstructedEngine,
              right_engine:ConstructedEngine)->"ContinuationWitness":
        left_ref=_provenance(left_engine)
        right_ref=_provenance(right_engine)
        a,b=left_engine.law,right_engine.law
        result=cls(a,b,left_ref,right_ref,
                   _identity(a,b,left_ref,right_ref))
        return result.verify()

    def verify(self)->"ContinuationWitness":
        for ref in (self.left_ref,self.right_ref):
            if (type(ref) is not dict or set(ref)!={
                    "version","history","cycle","phase"} or
                    type(ref["version"]) is not int or ref["version"]<0 or
                    type(ref["phase"]) is not int or ref["phase"]<0 or
                    type(ref["history"]) is not str or
                    type(ref["cycle"]) is not str):
                raise ValueError("source engine provenance was lost or malformed")
        if self.source_identity!=_identity(self.left,self.right,
                                            self.left_ref,self.right_ref):
            raise ValueError("source, generator, invariant fiber or engine provenance changed")
        a,b=_permutation(self.left),_permutation(self.right)
        if self.budgets and (tuple(sorted(set(self.budgets)))!=self.budgets
                             or any(type(n) is not int or n<1 for n in self.budgets)):
            raise ValueError("continuation budgets changed or are nonmonotone")
        if self.observations:
            if not self.budgets or self.budgets[-1]!=len(self.observations):
                raise ValueError("saved continuation budget does not match observations")
        elif self.budgets:
            raise ValueError("a budget exists without observations")
        first_mismatch=None
        for depth,o in enumerate(self.observations,1):
            if type(o.depth) is not int or o.depth!=depth:
                raise ValueError("a continuation depth was skipped or reordered")
            if (type(o.left_fixed) is not tuple or type(o.right_fixed) is not tuple
                    or o.left_fixed!=_fixed(a,depth)
                    or o.right_fixed!=_fixed(b,depth)):
                raise ValueError("retained observation does not replay")
            if first_mismatch is None and len(o.left_fixed)!=len(o.right_fixed):
                first_mismatch=depth
        if self.status=="DISTINGUISHED":
            if (self.distinguishing_depth is None or
                    type(self.distinguishing_depth) is not int or
                    self.distinguishing_depth!=first_mismatch or
                    self.bijection is not None):
                raise ValueError("distinction is missing its earliest invariant witness")
        elif self.status=="EQUIVALENT_FOR_B_ONLY":
            if (self.distinguishing_depth is not None or first_mismatch is not None
                    or self.bijection is None or
                    set(self.bijection)!=set(range(81)) or
                    any(self.bijection[a[i]]!=b[self.bijection[i]]
                        for i in range(81)) or
                    not self.observations or
                    len(self.observations[-1].left_fixed)!=81 or
                    len(self.observations[-1].right_fixed)!=81):
                raise ValueError("B-only equivalence requires a complete verified bijection")
        elif self.status=="UNKNOWN":
            if (self.bijection is not None or self.distinguishing_depth is not None
                    or first_mismatch is not None):
                raise ValueError("UNKNOWN cannot contain a promoted conclusion")
        else:
            raise ValueError("unsupported mathematical outcome")
        return self

    def advance(self,budget:int,*,audit_after_distinction:bool=False
                )->"ContinuationWitness":
        self.verify()
        if type(budget) is not int or budget<1:
            raise ValueError("budget must be a positive integer")
        prior=len(self.observations)
        if budget<prior:
            raise ValueError("cannot rewind the stored continuation")
        if budget==prior:
            return self
        if self.status!="UNKNOWN" and not (
                self.status=="DISTINGUISHED" and audit_after_distinction):
            raise ValueError("terminal result cannot be silently continued")
        a,b=_permutation(self.left),_permutation(self.right)
        records=list(self.observations)
        status=self.status
        first=self.distinguishing_depth
        h=self.bijection
        for depth in range(prior+1,budget+1):
            o=PeriodObservation(depth,_fixed(a,depth),_fixed(b,depth))
            records.append(o)
            if len(o.left_fixed)!=len(o.right_fixed):
                if first is None:first=depth
                status="DISTINGUISHED"
                h=None
                if not audit_after_distinction:break
            elif (status=="UNKNOWN" and len(o.left_fixed)==81
                  and len(o.right_fixed)==81):
                candidate=_intertwiner(a,b)
                if candidate is not None:
                    h=candidate
                    status="EQUIVALENT_FOR_B_ONLY"
                    break
        final=len(records)
        result=ContinuationWitness(
            self.left,self.right,self.left_ref,self.right_ref,
            self.source_identity,tuple(records),self.budgets+(final,),
            status,h,first)
        return result.verify()

    def summary(self)->dict:
        self.verify()
        return {
            "generator":"B","watched_scope":RELATION,"state_count":81,
            "A_preserves_fiber":False,
            "source_engine_versions":(self.left_ref["version"],
                                      self.right_ref["version"]),
            "observed_through":len(self.observations),
            "budgets":self.budgets,
            "status":self.status,
            "distinguishing_depth":self.distinguishing_depth,
            "bijection_verified":self.bijection is not None,
            "does_not_establish":"simultaneous A/B conjugacy",
        }

    def to_dict(self)->dict:
        self.verify()
        return {
            "schema":"engine2.window_continuation.v1",
            "relation":RELATION,
            "generator":"B",
            "domain":[list(s) for s in FIBER],
            "left":_encode_process(self.left),
            "right":_encode_process(self.right),
            "left_source":dict(self.left_ref),
            "right_source":dict(self.right_ref),
            "source_identity":self.source_identity,
            "observations":[o.to_dict() for o in self.observations],
            "budgets":list(self.budgets),
            "status":self.status,
            "bijection":list(self.bijection) if self.bijection is not None else None,
            "distinguishing_depth":self.distinguishing_depth,
        }

    def snapshot(self)->str:
        return json.dumps(self.to_dict(),sort_keys=True,indent=2)

    @classmethod
    def reenter(cls,snapshot:str, *,
                left_engine:ConstructedEngine|None=None,
                right_engine:ConstructedEngine|None=None
                )->"ContinuationWitness":
        data=json.loads(snapshot)
        if (type(data) is not dict or
                data.get("schema")!="engine2.window_continuation.v1" or
                data.get("relation")!=RELATION or
                data.get("generator")!="B" or
                data.get("domain")!=[list(s) for s in FIBER]):
            raise ValueError("the watched relation, domain or schema was changed")
        try:
            left=_decode_process(data["left"])
            right=_decode_process(data["right"])
            witness=cls(
                left,right,data["left_source"],data["right_source"],
                data["source_identity"],
                tuple(PeriodObservation(o["depth"],tuple(o["left_fixed"]),
                                        tuple(o["right_fixed"]))
                      for o in data["observations"]),
                tuple(data["budgets"]),data["status"],
                None if data["bijection"] is None else tuple(data["bijection"]),
                data["distinguishing_depth"],
            ).verify()
        except (KeyError,TypeError,IndexError) as err:
            raise ValueError("incomplete or malformed saved continuation") from err
        if left_engine is not None:
            if (_provenance(left_engine)!=witness.left_ref or
                    _encode_process(left_engine.law)!=_encode_process(left)):
                raise ValueError("current left engine does not match the recorded source")
        if right_engine is not None:
            if (_provenance(right_engine)!=witness.right_ref or
                    _encode_process(right_engine.law)!=_encode_process(right)):
                raise ValueError("current right engine does not match the recorded source")
        return witness


class CyclicActionContinuation:
    """Actual research entry / replay / exit over witnessed WindowProcess laws."""

    @staticmethod
    def enter(left_engine:ConstructedEngine,
              right_engine:ConstructedEngine)->ContinuationWitness:
        return ContinuationWitness.enter(left_engine,right_engine)

    @staticmethod
    def reenter(snapshot:str, *,
                left_engine:ConstructedEngine|None=None,
                right_engine:ConstructedEngine|None=None)->ContinuationWitness:
        return ContinuationWitness.reenter(snapshot,
            left_engine=left_engine,right_engine=right_engine)

    @staticmethod
    def exit(witness:ContinuationWitness)->dict:
        if not isinstance(witness,ContinuationWitness):
            raise TypeError("an exit must carry an actual continuation witness")
        return witness.summary()
