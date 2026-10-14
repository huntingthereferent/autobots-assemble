"""Consume an already witnessed cross-pin join for a separate explicit task.

Zero novel observations: advancing this adapter calls CrossPinJoin.advance(0)
only. Every requirement is checked against that join's recorded paired states
and admitted labeled edges. The join and its owner pins remain authoritative.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any

from ab_chatbot_cross_pin_join import CrossPinJoin, JoinedCrossPinReport

ROOT = (0, 0, 0)


def _state(value):
    if (type(value) is not list or len(value) != 3 or
            any(type(i) is not int or i not in (0, 1, 2) for i in value)):
        raise ValueError('finite state must be a three-element F3 list')
    return tuple(value)


def _word(value):
    if (type(value) is not str or not 1 <= len(value) <= 12 or
            any(a not in 'AB' for a in value)):
        raise ValueError('required path must be a nonempty bounded A/B word')
    return value


@dataclass(frozen=True)
class ObligationResult:
    kind: str
    requirement: tuple
    admitted: bool
    witness: tuple
    explanation: str


@dataclass(frozen=True)
class JointTaskReport:
    status: str
    fingerprint: str | None
    joint: JoinedCrossPinReport
    obligations: tuple[ObligationResult, ...]
    goals_carried: tuple
    details: str


class JointEvidenceTask:
    """Immutable task declaration referencing a pre-existing joint observer.

    A goal is a witnessed original state within the joint pairing; unlike
    destination identity it does not predeclare an image. No task requirement
    can create a state correspondence or add a transition to the join.
    """
    def __init__(self, joint: CrossPinJoin, task_input: Any):
        self.joint = joint
        self.status = 'INVALID_TASK'
        self.fingerprint = None
        self.goals = ()
        self.edges = ()
        self.paths = ()
        self.destinations = ()
        self.description = 'A strict nonempty finite task declaration is required.'
        if not isinstance(joint, CrossPinJoin):
            return
        if type(task_input) is not dict or not task_input or set(task_input) - {
                'goals', 'required_edges', 'required_paths', 'required_destinations'}:
            return
        try:
            values = {}
            for key in ('goals', 'required_edges', 'required_paths', 'required_destinations'):
                raw = task_input.get(key, [])
                if type(raw) is not list or len(raw) > 8:
                    raise ValueError('each requirement collection must have <=8 entries')
                values[key] = raw
            if not any(values.values()):
                raise ValueError('empty task is not a completion question')
            goals = tuple(_state(g) for g in values['goals'])
            edges = []
            for item in values['required_edges']:
                if type(item) is not dict or set(item) != {'state', 'action'} or item['action'] not in ('A', 'B'):
                    raise ValueError('explicit source state and action required')
                edges.append((_state(item['state']), item['action']))
            paths = []
            for item in values['required_paths']:
                if type(item) is not dict or set(item) != {'word', 'old_end', 'new_end'}:
                    raise ValueError('explicit path and endpoints required')
                paths.append((_word(item['word']), _state(item['old_end']), _state(item['new_end'])))
            destinations = []
            for item in values['required_destinations']:
                if type(item) is not dict or set(item) != {'source', 'image'}:
                    raise ValueError('explicit source state and required image needed')
                destinations.append((_state(item['source']), _state(item['image'])))
            if any(len(set(seq)) != len(seq) for seq in (goals, edges, paths, destinations)):
                raise ValueError('duplicate obligation')
            # Contradictory declared identities are a task defect, not evidence of law impossibility.
            mapped = {}
            for s, t in list(destinations) + [(s, t) for _, s, t in paths]:
                if s in mapped and mapped[s] != t:
                    self.status = 'INCONSISTENT_TASK'
                    self.description = 'Task declares incompatible images of one source state.'
                    return
                mapped[s] = t
            reverse = {}
            for s, t in mapped.items():
                if t in reverse and reverse[t] != s:
                    self.status = 'INCONSISTENT_TASK'
                    self.description = 'Task declares different source states with the same image.'
                    return
                reverse[t] = s
        except (ValueError, TypeError, KeyError):
            return
        self.goals, self.edges, self.paths, self.destinations = goals, tuple(edges), tuple(paths), tuple(destinations)
        declared = {'join': joint.fingerprint,
                    'goals': self.goals, 'required_edges': self.edges,
                    'required_paths': self.paths, 'required_destinations': self.destinations}
        self.fingerprint = sha256(json.dumps(declared, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        self.status = 'TASK_ACCEPTED'
        self.description = 'Task accepted; no evidence admitted without an audited joint witness.'

    def advance(self) -> JointTaskReport:
        # No novel owner transitions are allowed on behalf of this task.
        joint = self.joint.advance(max_new_edges=0)
        if self.status != 'TASK_ACCEPTED':
            return JointTaskReport(self.status, self.fingerprint, joint, (), (), self.description)
        if joint.status != 'JOINT_PARTIAL_CORRESPONDENCE_WITNESSED':
            return JointTaskReport(joint.status, self.fingerprint, joint, (), (),
                                   'No task success without a current replayed compatible joint correspondence.')
        fwd = dict(joint.state_pairs)
        edges = {(s, action): (target, ns, nt)
                 for s, action, target, ns, nt in joint.admitted_edges}
        checks = []
        carried = []
        for goal in self.goals:
            good = goal in fwd
            if good:
                carried.append((goal, fwd[goal]))
            checks.append(ObligationResult('GOAL', (goal,), good,
                          (goal, fwd[goal]) if good else (),
                          'Goal paired through an admitted rooted history.' if good else
                          'Goal not witnessed in the joint state pairing.'))
        for source, action in self.edges:
            edge = edges.get((source, action))
            good = edge is not None
            checks.append(ObligationResult('EDGE', (source, action), good,
                          (source, action, *edge) if good else (),
                          'Labeled edge admitted in the joint history.' if good else
                          'Requested edge is not in the observed joint history.'))
        for word, old_end, new_end in self.paths:
            s, t = ROOT, ROOT
            visited = []
            valid = True
            for action in word:
                edge = edges.get((s, action))
                if edge is None or fwd.get(s) != t or edge[1] != t:
                    valid = False
                    break
                visited.append((s, action, *edge))
                s, t = edge[0], edge[2]
            good = valid and s == old_end and t == new_end
            checks.append(ObligationResult('PATH', (word, old_end, new_end), good,
                          tuple(visited) if good else (),
                          'Each step and both endpoints witnessed.' if good else
                          'Required exact path or endpoint pair not witnessed.'))
        for source, image in self.destinations:
            good = fwd.get(source) == image
            checks.append(ObligationResult('DESTINATION', (source, image), good,
                          (source, image) if good else (),
                          'Paired endpoint image witnessed.' if good else
                          'Specified destination image not in joint pairing.'))
        status = ('TASK_COMPLETED_ON_JOINT_WITNESS' if all(c.admitted for c in checks)
                  else 'TASK_REQUIREMENTS_UNPROVED')
        return JointTaskReport(status, self.fingerprint, joint, tuple(checks),
                               tuple(carried),
                               'Task checked against existing admitted edges only; no added owner observations.')
