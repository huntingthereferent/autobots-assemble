"""Goal-selected *alternative greedy extensions* of one witnessed path union.

The same pinned source snapshots are used for two independently growing
partial bijections. Edges are admitted only via UnionEdgeExtender's replay and
collision checks; no unobserved target is inferred. This compares two bounded
priorities, not all possible mathematical correspondences.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from ab_chatbot_discovered_correspondence import DOMAIN_SET, State
from ab_chatbot_path_union import PathUnionAgent
from ab_chatbot_union_extension import UnionEdgeExtender, ExtensionReport

ChoiceStatus = Literal[
    'CONTINUING', 'GOALS_CARRIED_WITNESSED', 'GOALS_CARRIED_REMOTE_REPORTED',
    'PARTIAL_GOALS_WITNESSED', 'PARTIAL_GOALS_REMOTE_REPORTED',
    'GOALS_OUTSIDE_TESTED_EXTENSIONS', 'UNKNOWN_BUDGET', 'UNKNOWN_VERSION',
    'WALL_OBSERVATION',
]

@dataclass(frozen=True)
class Alternative:
    order: str
    status: str
    goals: tuple[tuple[State, State, str], ...]  # old goal, target image, rooted word
    state_pairs: int
    admitted_edges: int
    excluded_edges: int

@dataclass(frozen=True)
class AlternativeReport:
    status: ChoiceStatus
    selected_order: str | None
    alternatives: tuple[Alternative, ...]
    possible_images: tuple[tuple[State, tuple[State,...]], ...]
    old_observations: int
    new_observations: int
    detail: str

class AlternativeExtensionChooser:
    """Test both AB and BA priorities, then choose for *declared* source goals.

    `advance` may be resumed after CONTINUING or UNKNOWN_BUDGET. A winner is
    never announced while another candidate is unfinished. The alternatives
    share read-only source identities and observed edge caches, not mappings.
    """

    def __init__(self, source: PathUnionAgent, goals: tuple[State,...]):
        if not goals or len(set(goals)) != len(goals) or any(g not in DOMAIN_SET for g in goals):
            raise ValueError('goals must be distinct valid finite states')
        self.goals = tuple(goals)
        self.extenders = {
            order: UnionEdgeExtender(source, action_order=order)
            for order in ('AB','BA')
        }
        self.last: dict[str,ExtensionReport] = {}

    def _result(self, status: ChoiceStatus, detail: str, *, chosen=None) -> AlternativeReport:
        alternatives=[]
        images={goal:set() for goal in self.goals}
        for order, e in self.extenders.items():
            r=self.last.get(order)
            if r is None: continue
            admitted = dict(r.state_pairs)
            carried=[]
            for goal in self.goals:
                if goal in admitted and goal in e.words:
                    carried.append((goal,admitted[goal],e.words[goal]))
                    if r.status in ('ROOTED_CLOSED_WITNESSED','ROOTED_CLOSED_REMOTE_REPORTED',
                                    'PARTIAL_EXTENSION_WITNESSED','PARTIAL_EXTENSION_REMOTE_REPORTED'):
                        images[goal].add(admitted[goal])
            alternatives.append(Alternative(order,r.status,tuple(carried),
                                len(r.state_pairs),len(r.admitted_edges),len(r.rejected)))
        snap=next(iter(self.extenders.values()))
        return AlternativeReport(status,chosen,tuple(alternatives),
            tuple((g,tuple(sorted(images[g]))) for g in self.goals),
            len(snap.old_snapshot.edges) if hasattr(snap.old_snapshot,'edges') else 0,
            len(snap.new_snapshot.edges) if hasattr(snap.new_snapshot,'edges') else 0,
            detail)

    def advance(self, *, max_new_edges_per_candidate: int=4) -> AlternativeReport:
        if type(max_new_edges_per_candidate) is not int or not 0<=max_new_edges_per_candidate<=108:
            raise ValueError('max_new_edges_per_candidate must be integer 0..108')
        for order, e in self.extenders.items():
            self.last[order]=e.advance(max_new_edges=max_new_edges_per_candidate)
        statuses=tuple(r.status for r in self.last.values())
        for problem in ('UNKNOWN_VERSION','WALL_OBSERVATION','UNKNOWN_BUDGET'):
            if problem in statuses:
                return self._result(problem,'At least one candidate cannot be verified; no winner declared.')
        if 'CONTINUING' in statuses:
            return self._result('CONTINUING','One or more candidate priorities are not fully examined.')
        # All completed and individually replay-audited. Score is an explicit
        # goal policy, not proof of mathematical maximality or unique mapping.
        choices=[]
        for order,e in self.extenders.items():
            r=self.last[order]
            matched=sum(g in e.words and g in e.forward for g in self.goals)
            choices.append((matched,len(r.admitted_edges),len(r.state_pairs),-len(r.rejected),order))
        maxscore=max(t[:4] for t in choices)
        chosen=next(order for n,edges,states,bad,order in choices
                    if (n,edges,states,bad)==maxscore)
        coverage=maxscore[0]
        if coverage==0:
            return self._result('GOALS_OUTSIDE_TESTED_EXTENSIONS',
                'Neither of the two fully checked greedy priorities carried a goal; other mappings remain unexamined.',
                chosen=chosen)
        local=all(self.last[order].status.endswith('WITNESSED') for order in self.last)
        status=(('GOALS_CARRIED_' if coverage==len(self.goals) else 'PARTIAL_GOALS_')+
                ('WITNESSED' if local else 'REMOTE_REPORTED'))
        return self._result(status,
            f'Selected {chosen} by verified {coverage}/{len(self.goals)} goal coverage, '
            'then admitted edge/state counts. Candidate set is AB vs BA only; '
            'no global maximality or unique target-image claim.',chosen=chosen)
