"""Engine 2 boundary research: fifth-coordinate zero-trace correction shape.

Local independent finite-field experiment implementing the specified additive
triangular lift from ZERO_TRACE_LIFT.md. No Engine 1 calls; no claim of
universal centralizer classification, cross-grammar conjugacy, or ARC solving.

Important new principle: (world law, selected commuting correction, root mark)
are distinct witness-bearing inputs. An admitted world may have multiple
non-identical corrections with different cyclic orders.
"""
from __future__ import annotations
from collections import deque
from dataclasses import dataclass, field
from itertools import product

F3 = (0, 1, 2)
ZERO = (0,) * 9
VERTICES = tuple(product(F3, repeat=3))
INDEX = {vertex: index for index, vertex in enumerate(VERTICES)}
BASE = {
    1: (0, 1, 2, 0, 2, 1, 1, 1, 1),
    2: (0, 1, 2, 1, 0, 2, 1, 1, 1),
}
ALPHA = {1: (0, 1, 1), 2: (0, 0, 1)}


def _table(values: tuple[int, ...], size: int) -> None:
    if type(values) is not tuple or len(values) != size or any(type(v) is not int or v not in F3 for v in values):
        raise ValueError(f"expected {size} F3 entries")


@dataclass(frozen=True)
class ZeroTraceSpace:
    gain: int
    quotient: tuple[int, int, int]
    offsets: tuple[int, int, int]

    def __post_init__(self) -> None:
        if type(self.gain) is not int or self.gain not in (1, 2):
            raise ValueError("gain must be 1 or 2")
        _table(self.quotient, 3)
        _table(self.offsets, 3)
        if sum(self.quotient) % 3 != 0 or self.offsets[0] != 0:
            raise ValueError("requires zero-trace quotient and normalized offsets")

    def lower(self, s: tuple[int, int, int]) -> tuple[int, int, int]:
        v, z, y = s
        w = (z + ALPHA[self.gain][v]) % 3
        return (v, (z + 1) % 3, (y + self.quotient[w] - self.quotient[0]) % 3)

    def induced_B(self, s: tuple[int, int, int], u: int) -> tuple[int, int, int]:
        v, z, y = s
        w = (z + ALPHA[self.gain][v]) % 3
        return ((v + self.gain * (u + 1)) % 3,
                (z + BASE[self.gain][3*u+v]) % 3,
                (y + self.quotient[w] + self.offsets[v]) % 3)

    def step(self, state: tuple[int, ...], gen: str, fifth: tuple[int, ...]) -> tuple[int, ...]:
        _table(fifth, 9)
        if len(state) < 5 or any(type(x) is not int or x not in F3 for x in state):
            raise ValueError("fifth coordinate must be represented")
        moved = list(state)
        if gen == 'A':
            moved[0] = (state[0] + 1) % 3
        elif gen == 'B':
            u, v, z, y = state[:4]
            moved[1] = (v + self.gain * (u+1)) % 3
            moved[2] = (z + BASE[self.gain][3*u+v]) % 3
            moved[3] = (y + self.quotient[(z+ALPHA[self.gain][v])%3] + self.offsets[v]) % 3
            moved[4] = (state[4] + fifth[3*z+y]) % 3
        else:
            raise ValueError("generator must be A or B")
        return tuple(moved)


def _voltage(p: ZeroTraceSpace, q2: tuple[int, ...], s: tuple[int, int, int]) -> int:
    shifted = p.lower(s)
    return (q2[3*shifted[1] + shifted[2]] - q2[3*s[1] + s[2]]) % 3


@dataclass(frozen=True)
class VoltageEdge:
    start: tuple[int, int, int]
    end: tuple[int, int, int]
    u: int
    direction: int
    voltage: int

    def replay(self, p: ZeroTraceSpace, q2: tuple[int, ...]) -> bool:
        if self.direction == 1:
            return self.end == p.induced_B(self.start, self.u) and self.voltage == _voltage(p, q2, self.start)
        if self.direction == -1:
            return self.start == p.induced_B(self.end, self.u) and self.voltage == (-_voltage(p, q2, self.end))%3
        return False


@dataclass(frozen=True)
class VoltageObstruction:
    root: tuple[int, int, int]
    end: tuple[int, int, int]
    path_one: tuple[VoltageEdge, ...]
    path_two: tuple[VoltageEdge, ...]
    one: int
    two: int

    def replay(self, p: ZeroTraceSpace, q2: tuple[int, ...]) -> bool:
        def follow(path):
            at, voltage = self.root, 0
            for edge in path:
                if edge.start != at or not edge.replay(p, q2):
                    return None
                at, voltage = edge.end, (voltage+edge.voltage)%3
            return at, voltage
        return self.one != self.two and follow(self.path_one) == (self.end, self.one) and follow(self.path_two) == (self.end, self.two)


@dataclass(frozen=True)
class CorrectionEvidence:
    space: ZeroTraceSpace
    fifth: tuple[int, ...]
    admissible: bool
    normalized: tuple[int, ...] | None
    components: tuple[int, ...]
    obstruction: VoltageObstruction | None
    equations_verified: int

    @property
    def component_count(self) -> int:
        return len(set(self.components))


def _edges(p: ZeroTraceSpace, q2: tuple[int, ...]):
    links = {s: [] for s in VERTICES}
    for s, u in product(VERTICES, F3):
        t = p.induced_B(s, u)
        delta = _voltage(p, q2, s)
        links[s].append(VoltageEdge(s, t, u, 1, delta))
        links[t].append(VoltageEdge(t, s, u, -1, (-delta)%3))
    return links


def _component_labels(links) -> tuple[int, ...]:
    """Complete underlying graph components, even when a voltage is obstructed."""
    groups = {}
    for start in VERTICES:
        if start in groups:
            continue
        k = len(set(groups.values()))
        groups[start] = k
        pending = [start]
        for current in pending:
            for edge in links[current]:
                if edge.end not in groups:
                    groups[edge.end] = k
                    pending.append(edge.end)
    return tuple(groups[v] for v in VERTICES)


def solve_correction(p: ZeroTraceSpace, q2: tuple[int, ...]) -> CorrectionEvidence:
    """Solve the exact 81 signed-edge equations, retaining cycle obstruction."""
    _table(q2, 9)
    links = _edges(p, q2)
    complete_labels = _component_labels(links)
    values, labels, paths = {}, {}, {}
    components = 0
    for root in VERTICES:
        if root in values:
            continue
        values[root], labels[root], paths[root] = 0, components, ()
        components += 1
        queue = deque([root])
        while queue:
            s = queue.popleft()
            for edge in links[s]:
                t = edge.end
                new = (values[s] + edge.voltage) % 3
                if t in values:
                    if values[t] != new:
                        witness = VoltageObstruction(root, t, paths[t], paths[s]+(edge,), values[t], new)
                        if not witness.replay(p, q2):
                            raise AssertionError("failed to replay own signed path contradiction")
                        return CorrectionEvidence(p, q2, False, None,
                            complete_labels, witness, 0)
                else:
                    values[t], labels[t], paths[t] = new, components-1, paths[s]+(edge,)
                    queue.append(t)
    equations = sum((values[edge.end] - values[edge.start])%3 == edge.voltage
                    for s in VERTICES for edge in links[s] if edge.direction == 1)
    if equations != 81:
        raise AssertionError("admitted correction failed an exact equation")
    return CorrectionEvidence(p, q2, True, tuple(values[v] for v in VERTICES),
                              complete_labels, None, equations)


def trace(p: ZeroTraceSpace, correction: tuple[int, ...]) -> tuple[int, ...]:
    _table(correction, 27)
    result = []
    for s in VERTICES:
        t = p.lower(s)
        t2 = p.lower(t)
        if p.lower(t2) != s:
            raise AssertionError("zero-trace lower map must have order three")
        result.append((correction[INDEX[s]] + correction[INDEX[t]] + correction[INDEX[t2]]) % 3)
    return tuple(result)


@dataclass(frozen=True)
class SelectedCorrection:
    evidence: CorrectionEvidence
    values: tuple[int, ...]
    order: int

    def __post_init__(self) -> None:
        if not self.evidence.admissible:
            raise ValueError("cannot select correction from obstructed coupling")
        _table(self.values, 27)
        p, q2 = self.evidence.space, self.evidence.fifth
        for s,u in product(VERTICES,F3):
            dest = p.induced_B(s,u)
            if (self.values[INDEX[dest]] - self.values[INDEX[s]])%3 != _voltage(p,q2,s):
                raise ValueError("correction does not satisfy signed equations")
        if self.order != (9 if any(trace(p, self.values)) else 3):
            raise ValueError("selected cyclic order disagrees with native trace")

    def move_mark(self, state: tuple[int,...]) -> tuple[int,...]:
        if len(state) < 5:
            raise ValueError("pointed correction requires a fifth coordinate")
        moved = list(state)
        v,z,y = state[1:4]
        shifted = self.evidence.space.lower((v,z,y))
        moved[2],moved[3] = shifted[1],shifted[2]
        moved[4] = (state[4]+self.values[INDEX[(v,z,y)]])%3
        return tuple(moved)

    def audit_generators(self) -> int:
        p, q = self.evidence.space, self.evidence.fifth
        checked = 0
        for s in product(F3,repeat=5):
            mapped = self.move_mark(s)
            for gen in 'AB':
                if self.move_mark(p.step(s,gen,q)) != p.step(mapped,gen,q):
                    raise AssertionError("selected correction fails a full-state generator square")
                checked += 1
        return checked

    def mark_orbit(self, mark=(0,0,0,0,0)) -> tuple[tuple[int,...],...]:
        current, seen = mark, []
        for _ in range(self.order):
            if current in seen:
                break
            seen.append(current)
            current = self.move_mark(current)
        if current != mark:
            raise AssertionError("mark orbit did not close inside proved cyclic order")
        return tuple(seen)


def all_selected_corrections(evidence: CorrectionEvidence) -> dict[int, SelectedCorrection]:
    if not evidence.admissible:
        return {}
    components = evidence.component_count
    chosen = {}
    for constants in product(F3, repeat=components):
        values = tuple((x+constants[evidence.components[i]])%3 for i,x in enumerate(evidence.normalized))
        order = 9 if any(trace(evidence.space, values)) else 3
        if order not in chosen:
            chosen[order] = SelectedCorrection(evidence, values, order)
    return chosen


@dataclass(frozen=True)
class ResearchReading:
    watch: str
    status: str
    family: str
    relation: str
    evidence: CorrectionEvidence
    selected: tuple[SelectedCorrection, ...]
    checked_generator_squares: int
    parent_id: int | None
    notes: tuple[str, ...]

    def summary(self) -> dict:
        return {
            'watch':self.watch,'status':self.status,'family':self.family,'relation':self.relation,
            'space':{'gain':self.evidence.space.gain,'quotient':self.evidence.space.quotient,
                    'offsets':self.evidence.space.offsets,'fifth':self.evidence.fifth},
            'components':self.evidence.component_count,
            'admitted':self.evidence.admissible,
            'selected_orders':[s.order for s in self.selected],
            'selected_corrections':[s.values for s in self.selected],
            'selected_mark_orbits':[s.mark_orbit() for s in self.selected],
            'obstruction': None if self.evidence.obstruction is None else {
                'one':self.evidence.obstruction.one,'two':self.evidence.obstruction.two,
                'root':self.evidence.obstruction.root,'end':self.evidence.obstruction.end,
                'path_one':[vars(e) for e in self.evidence.obstruction.path_one],
                'path_two':[vars(e) for e in self.evidence.obstruction.path_two]},
            'equations_verified':self.evidence.equations_verified,
            'generator_squares_verified':self.checked_generator_squares,
            'parent_id':self.parent_id,'notes':self.notes,
        }


@dataclass
class Engine2CorrectionResearch:
    """A separate native research space. No fake coupling_tower equivalence bridge."""
    findings: list[ResearchReading] = field(default_factory=list)

    def investigate(self, p: ZeroTraceSpace, q2: tuple[int,...], *, parent_id: int|None = None) -> ResearchReading:
        if parent_id is not None:
            if not (0<=parent_id<len(self.findings)):
                raise ValueError("unknown previous mathematical research witness")
            old=self.findings[parent_id]
            if (old.evidence.space,old.evidence.fifth)!=(p,q2) or not old.evidence.admissible:
                raise ValueError("cannot change research referent or inherit an obstruction without a bridge")
        evidence=solve_correction(p,q2)
        if not evidence.admissible:
            record=ResearchReading('COHOMOLOGICAL_ADMISSION','SIGNED_CYCLE_OBSTRUCTION',
                   'zero_trace_fifth_coordinate','two-path voltage contradiction',
                   evidence,(),0,parent_id,('rejected fifth-coupling table',))
        else:
            selections=all_selected_corrections(evidence)
            checked=sum(s.audit_generators() for s in selections.values())
            status='CORRECTION_ORDER_SPLIT' if len(selections)==2 else 'ADMITTED_SINGLE_ORDER'
            notes=("same world law can support multiple explicitly selected corrections; not new world classes",
                   "chosen correction and mark transport are part of the witness",
                   "no claimed bridge to one-input CouplingLaw class")
            record=ResearchReading('COHOMOLOGICAL_ORDER',status,'zero_trace_fifth_coordinate',
                'additive triangular correction and native third-iterate trace',
                evidence,tuple(selections[i] for i in sorted(selections)),checked,parent_id,notes)
        self.findings.append(record)
        return record

    def reenter(self, index:int) -> ResearchReading:
        if not 0 <= index < len(self.findings):
            raise ValueError("missing witness")
        before=self.findings[index]
        return self.investigate(before.evidence.space,before.evidence.fifth,parent_id=index)


def run_examples():
    cases=(
        ('order_three_only',ZeroTraceSpace(1,(0,0,0),(0,0,1)),ZERO),
        ('order_nine_only',ZeroTraceSpace(1,(0,1,2),(0,0,1)),(2,1,0)*3),
        ('both_orders',ZeroTraceSpace(1,(1,0,2),(0,0,0)),ZERO),
        ('signed_cycle_obstruction',ZeroTraceSpace(1,(0,0,0),(0,0,1)),(1,)+(0,)*8),
    )
    lab=Engine2CorrectionResearch()
    result={key:lab.investigate(p,q).summary() for key,p,q in cases}
    lab.reenter(2)
    result['reentered_parent']=lab.findings[-1].parent_id
    result['engine_one_calls']=0
    return result

if __name__ == '__main__':
    import json
    print(json.dumps(run_examples(),indent=2))


def _rref(rows: list[tuple[int, ...]], columns: int) -> tuple[list[list[int]],tuple[int,...]]:
    matrix=[list(row) for row in rows if any(row)]
    pivots=[]
    i=0
    for column in range(columns):
        p=next((j for j in range(i,len(matrix)) if matrix[j][column]),None)
        if p is None:continue
        matrix[i],matrix[p]=matrix[p],matrix[i]
        scale=pow(matrix[i][column],-1,3)
        matrix[i]=[(scale*x)%3 for x in matrix[i]]
        for j in range(len(matrix)):
            if j!=i and matrix[j][column]:
                t=matrix[j][column]
                matrix[j]=[(x-t*y)%3 for x,y in zip(matrix[j],matrix[i])]
        pivots.append(column)
        i+=1
    return matrix[:i],tuple(pivots)


def _kernel(rows: list[tuple[int, ...]], columns: int) -> tuple[tuple[int, ...], ...]:
    reduced,pivots=_rref(rows,columns)
    result=[]
    for free in range(columns):
        if free in pivots:continue
        vec=[0]*columns
        vec[free]=1
        for pivot,row in zip(pivots,reduced):
            vec[pivot]=(-row[free])%3
        result.append(tuple(vec))
    return tuple(result)


def _rank(rows: list[tuple[int, ...]], columns: int) -> int:
    return len(_rref(rows,columns)[1])


def _constraint_vectors(p:ZeroTraceSpace):
    """Independent linear signed-path constraints on the nine q2 coefficients.

    This does NOT call solve_correction or classify: it transports symbolic
    9-vectors rather than evaluating any one q2 table numerically.
    """
    links={s:[] for s in VERTICES}
    for s,u in product(VERTICES,F3):
        t=p.induced_B(s,u)
        shifted=p.lower(s)
        row=[0]*9
        row[3*shifted[1]+shifted[2]]+=1
        row[3*s[1]+s[2]]-=1
        row=tuple(x%3 for x in row)
        links[s].append((t,row))
        links[t].append((s,tuple((-x)%3 for x in row)))
    path={}
    component={}
    constraints=[]
    for s in VERTICES:
        if s in path:continue
        k=len(set(component.values()))
        path[s]=(0,)*9
        component[s]=k
        queue=deque([s])
        while queue:
            v=queue.popleft()
            for dest,delta in links[v]:
                next_vec=tuple((a+b)%3 for a,b in zip(path[v],delta))
                if dest in path:
                    constraints.append(tuple((a-b)%3 for a,b in zip(next_vec,path[dest])))
                else:
                    path[dest]=next_vec
                    component[dest]=k
                    queue.append(dest)
    return constraints, tuple(path[v] for v in VERTICES), tuple(component[v] for v in VERTICES)


def _trace_vectors(p:ZeroTraceSpace, correction:tuple[int,...])->tuple[int,...]:
    """Separate independent trace computation from the selected map machinery."""
    return tuple(sum(correction[INDEX[v]] for v in (s,p.lower(s),p.lower(p.lower(s))))%3 for s in VERTICES)


def count_whole_zero_trace_family() -> dict:
    """Exact matrix-kernel count over all declared 162 zero-trace systems."""
    from collections import Counter
    histogram=Counter()
    total=Counter()
    for gain in (1,2):
        for Q in product(F3,repeat=3):
            if sum(Q)%3:continue
            for a,b in product(F3,repeat=2):
                p=ZeroTraceSpace(gain,Q,(0,a,b))
                equations,path_vectors,group=_constraint_vectors(p)
                constraint_rank=_rank(equations,9)
                component_count=len(set(group))
                histogram[(component_count,constraint_rank)]+=1
                q_basis=_kernel(equations,9)
                gauge=[]
                for component in range(component_count):
                    gauge.append(tuple(int(g==component) for g in group))
                q_trace=[]
                for vec in q_basis:
                    selected=tuple(sum(a*b for a,b in zip(path_row,vec))%3 for path_row in path_vectors)
                    q_trace.append(_trace_vectors(p,selected))
                gauge_traces=[_trace_vectors(p,g) for g in gauge]
                gauge_rank=_rank(gauge_traces,27)
                union_rank=_rank(gauge_traces+q_trace,27)
                relative=union_rank-gauge_rank
                admitted=3**len(q_basis)
                order_three=admitted//3**relative
                order_nine=admitted if gauge_rank else admitted-order_three
                both=order_three if gauge_rank else 0
                total['admitted']+=admitted
                total['order_three_possible']+=order_three
                total['order_nine_possible']+=order_nine
                total['both']+=both
                total['multi_component_gauge']+=int(gauge_rank>0)
    return {'configurations':sum(histogram.values()),
            'histogram':{f'{c} components, rank {r}':n for (c,r),n in sorted(histogram.items())},
            **total}