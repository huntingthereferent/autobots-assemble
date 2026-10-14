"""Join *observed* rooted word histories from two separately pinned revisions.

The same action word is replayed against each owner-held snapshot by the
existing CrossPinComparison. No source state is identified off those histories,
and no unobserved A/B edge is admitted.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any

from ab_chatbot_cross_pin_comparison import CrossPinComparison
from ab_chatbot_owner_pin_contract import OwnerPinRegistry

ROOT = (0, 0, 0)

@dataclass(frozen=True)
class HistoryCollision:
    cause: str
    previous_word: str
    incoming_word: str
    old_endpoints: tuple
    new_endpoints: tuple
    old_equal: bool
    new_equal: bool

@dataclass(frozen=True)
class JoinedCrossPinReport:
    status: str
    fingerprint: str | None
    versions: tuple
    pins: tuple
    words: tuple[str, ...]
    state_pairs: tuple
    admitted_edges: tuple
    obstruction: HistoryCollision | None
    old_observed: int
    new_observed: int
    details: str

class CrossPinJoin:
    """Strictly task-declared finite rooted union, no automatic extension."""
    def __init__(self, old, new, task_input: Any, *, registry: OwnerPinRegistry):
        self.status = 'INVALID_TASK'
        self.fingerprint = None
        self.words = ()
        self._base = None
        self.old, self.new, self.registry = old, new, registry
        if type(task_input) is not dict or set(task_input) != {'required_owner_pins', 'join_words'}:
            return
        words = task_input.get('join_words')
        if (type(words) is not list or not 2 <= len(words) <= 8 or
                any(type(w) is not str or not 1 <= len(w) <= 12 or any(a not in 'AB' for a in w)
                    for w in words) or len(set(words)) != len(words)):
            return
        pins = task_input['required_owner_pins']
        if (type(pins) is not dict or set(pins) != {'old','new'} or
                any(type(token) is not str or len(token) != 48 for token in pins.values()) or
                pins['old'] == pins['new']):
            return
        self.words = tuple(words)
        compare_input = {'required_owner_pins': pins,
                         'compare_words': [['', word] for word in words]}
        self._base = CrossPinComparison(old, new, compare_input, registry=registry)
        self.status = self._base.status
        if self.status == 'TASK_ACCEPTED':
            self.fingerprint = sha256(json.dumps({
                'required_owner_pins': pins, 'join_words': self.words},
                sort_keys=True, separators=(',', ':')).encode()).hexdigest()

    def _out(self, status, baseline, *, state_pairs=(), admitted_edges=(), obstruction=None, detail=''):
        return JoinedCrossPinReport(status, self.fingerprint,
                (baseline.old_version, baseline.new_version),baseline.pins,
                self.words,tuple(state_pairs),tuple(admitted_edges),obstruction,
                baseline.old_observed,baseline.new_observed,detail)

    def advance(self, *, max_new_edges=108):
        if type(max_new_edges) is not int or not 0 <= max_new_edges <= 108:
            raise ValueError('edge cap must be integer 0..108')
        if self._base is None:
            return JoinedCrossPinReport(self.status,None,(None,None),(),self.words,(),(),
                                       None,0,0,'Invalid or unsupported exact join task.')
        baseline=self._base.advance(max_new_edges=max_new_edges)
        terminal={'RELATION_CHANGED_WITNESSED','DECLARED_EQUALITY_PRESERVED_WITNESSED',
                  'DECLARED_NONIDENTITY_PRESERVED_WITNESSED'}
        if baseline.status not in terminal:
            return self._out(baseline.status,baseline,detail=baseline.detail)
        if len(baseline.comparisons) != len(self.words):
            return self._out('WALL_OBSERVATION',baseline,detail='Missing independently replayed history.')
        forward = {}
        reverse = {}
        old_word = {}
        new_word = {}
        edges = {}
        for expected, relation in zip(self.words,baseline.comparisons):
            if relation.words != ('',expected):
                return self._out('WALL_OBSERVATION',baseline,detail='History order or identity changed.')
            op=relation.old_paths[1].states
            np=relation.new_paths[1].states
            if len(op)!=len(expected)+1 or len(np)!=len(expected)+1:
                return self._out('WALL_OBSERVATION',baseline,detail='Truncated history.')
            for i,(s,t) in enumerate(zip(op,np)):
                word=expected[:i]
                if s in forward and forward[s] != t:
                    first=old_word[s]
                    old_equal=True
                    new_equal=False
                    collision=HistoryCollision('SOURCE_STATE_CONFLICT',first,word,
                              (s,s),(forward[s],t),old_equal,new_equal)
                    return self._out('JOINT_RELATION_CONFLICT_WITNESSED',baseline,
                        obstruction=collision,detail='Two retained histories assign different new states to one old state.')
                if t in reverse and reverse[t] != s:
                    first=new_word[t]
                    collision=HistoryCollision('TARGET_STATE_CONFLICT',first,word,
                              (reverse[t],s),(t,t),False,True)
                    return self._out('JOINT_RELATION_CONFLICT_WITNESSED',baseline,
                        obstruction=collision,detail='Two retained histories assign the same new state to different old states.')
                forward[s]=t
                reverse[t]=s
                old_word.setdefault(s,word)
                new_word.setdefault(t,word)
                if i<len(expected):
                    k=(s,expected[i])
                    e=(s,expected[i],op[i+1],t,np[i+1])
                    if k in edges and edges[k]!=e:
                        return self._out('WALL_OBSERVATION',baseline,detail='Conflicting replay for one labeled source edge.')
                    edges[k]=e
        assert ROOT in forward and forward[ROOT]==ROOT
        # Explicit admission: every edge has already appeared in a word history.
        for s,a,u,t,v in edges.values():
            assert forward[s]==t and forward[u]==v
        return self._out('JOINT_PARTIAL_CORRESPONDENCE_WITNESSED',baseline,
               state_pairs=tuple(sorted(forward.items())),
               admitted_edges=tuple(sorted(edges.values())),
               detail='Consistent observed rooted word union only; no off-path edges or full-system transport.')
