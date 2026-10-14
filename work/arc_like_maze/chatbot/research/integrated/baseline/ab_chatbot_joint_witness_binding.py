"""Bind an explicit task to one exact audited joint witness; compare without merging.

A declared digest is only a selection handle. It never authenticates an owner
or substitutes for zero-read source/pin/transition replay on *every* use.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict, is_dataclass
from hashlib import sha256
import json
import re
from typing import Any

from ab_chatbot_cross_pin_join import CrossPinJoin, JoinedCrossPinReport
from ab_chatbot_joint_evidence_task import JointEvidenceTask, JointTaskReport

WITNESSED = 'JOINT_PARTIAL_CORRESPONDENCE_WITNESSED'
DIGEST_RE = re.compile(r'[0-9a-f]{64}\Z')
TASK_KEYS = {'goals','required_edges','required_paths','required_destinations'}


def _canonical_default(value):
    if is_dataclass(value):
        return asdict(value)
    raise TypeError('unsupported canonical evidence object')


def canonical_digest(report: JoinedCrossPinReport) -> str | None:
    """Hash exact relation + pinned referent, not ambient cache counters/details.

    Hashing any report does not make it true. Caller must obtain it from the
    live CrossPinJoin.advance(0); no reported digest can create owner proof.
    """
    if not isinstance(report, JoinedCrossPinReport) or report.status != WITNESSED:
        return None
    material = {
        'format': 'cross-pin-joined-witness/v1',
        'join_task_fingerprint': report.fingerprint,
        'pins': report.pins, 'versions': report.versions,
        'words': report.words,
        'state_pairs': report.state_pairs,
        'admitted_edges': report.admitted_edges,
    }
    return sha256(json.dumps(material, sort_keys=True,
                             separators=(',', ':'), ensure_ascii=True,
                             default=_canonical_default).encode()).hexdigest()


def current_digest(joint: CrossPinJoin) -> str | None:
    """Audit without admitting new transitions; unready/invalid has no digest."""
    if not isinstance(joint, CrossPinJoin):
        raise TypeError('verified cross-pin join object required')
    return canonical_digest(joint.advance(max_new_edges=0))


@dataclass(frozen=True)
class BoundTaskResult:
    status: str
    expected_digest: str | None
    observed_digest: str | None
    task_report: JointTaskReport | None
    detail: str


class BoundJointTask:
    """Task is immutable and pinned to an explicit audited join digest."""
    def __init__(self, joint: CrossPinJoin, declaration: Any):
        self.joint = joint
        self.status = 'INVALID_TASK'
        self.expected_digest = None
        self.task = None
        self.task_fingerprint = None
        self.declaration = None
        if not isinstance(joint, CrossPinJoin) or type(declaration) is not dict:
            return
        if set(declaration) - TASK_KEYS - {'witness_fingerprint'}:
            return
        digest = declaration.get('witness_fingerprint')
        if type(digest) is not str or DIGEST_RE.fullmatch(digest) is None:
            return
        contract = {k:v for k,v in declaration.items() if k != 'witness_fingerprint'}
        task = JointEvidenceTask(joint, contract)
        if task.status != 'TASK_ACCEPTED':
            self.status = task.status
            return
        self.task = task
        self.expected_digest = digest
        self.task_fingerprint = task.fingerprint
        self.declaration = (task.goals, task.edges, task.paths, task.destinations)
        self.status = 'TASK_ACCEPTED'

    def advance(self) -> BoundTaskResult:
        if self.status != 'TASK_ACCEPTED':
            return BoundTaskResult(self.status, self.expected_digest, None, None,
                                   'Invalid explicit witness/task declaration; no task observations requested.')
        report = self.joint.advance(max_new_edges=0)
        if report.status != WITNESSED:
            return BoundTaskResult(report.status, self.expected_digest, None, None,
                                   'Current join is not an audited compatible witness.')
        actual = canonical_digest(report)
        if actual != self.expected_digest:
            return BoundTaskResult('WITNESS_FINGERPRINT_MISMATCH', self.expected_digest,
                                   actual, None,
                                   'Task names a different join; cannot substitute observed or paired evidence.')
        task_report = self.task.advance()  # second live zero-read audit; no TOCTOU success.
        if task_report.joint.status != WITNESSED:
            return BoundTaskResult(task_report.joint.status, self.expected_digest, None,
                                   None, 'Joint witness invalidated during task consumption.')
        checked = canonical_digest(task_report.joint)
        if checked != self.expected_digest:
            return BoundTaskResult('WITNESS_FINGERPRINT_MISMATCH',self.expected_digest,
                                   checked,None,'Witness identity changed during consumption.')
        return BoundTaskResult(task_report.status,self.expected_digest,checked,task_report,
                               'Evaluated only the specifically bound replayed joint witness.')


@dataclass(frozen=True)
class ComparedCandidate:
    label: str
    status: str
    expected_digest: str | None
    observed_digest: str | None
    admitted_obligations: int
    total_obligations: int
    retained_obstruction: object | None


@dataclass(frozen=True)
class ComparisonResult:
    status: str
    task_contract_fingerprint: str | None
    candidates: tuple[ComparedCandidate,...]
    completed_by: tuple[str,...]
    detail: str


class JointWitnessTaskComparison:
    """Evaluate the same explicit contract against 2..8 disjoint audited joins.

    Never unions state-pairs, edges or individual obligation successes across
    candidates. All reports are revisited on every advance.
    """
    def __init__(self, candidates: tuple[tuple[str,BoundJointTask],...] ):
        self.status = 'INVALID_COMPARISON'
        self.candidates = ()
        self.contract_fingerprint = None
        if (type(candidates) is not tuple or not 2 <= len(candidates) <= 8 or
            any(type(pair) is not tuple or len(pair)!=2 or type(pair[0]) is not str or
                not pair[0] or not isinstance(pair[1], BoundJointTask) or
                pair[1].status!='TASK_ACCEPTED' for pair in candidates)):
            return
        if len({label for label,_ in candidates}) != len(candidates):
            return
        # Semantic tasks must match; each candidate's join identifier is intentionally different.
        contracts=[task.declaration for _,task in candidates]
        encoded=[json.dumps(c, sort_keys=True,separators=(',',':')) for c in contracts]
        if len(set(encoded)) != 1:
            return
        if len({id(task.joint) for _,task in candidates}) != len(candidates):
            return
        self.candidates = candidates
        self.contract_fingerprint = sha256(encoded[0].encode()).hexdigest()
        self.status = 'COMPARISON_ACCEPTED'

    def advance(self) -> ComparisonResult:
        if self.status != 'COMPARISON_ACCEPTED':
            return ComparisonResult(self.status,None,(),(),
                                    'Provide distinct joins with the identical declared task.')
        results=[]; finished=[]; ready=0
        for label,task in self.candidates:
            result = task.advance()
            tr=result.task_report
            checks = tr.obligations if tr else ()
            obstruction=None
            if tr:
                obstruction=tr.joint.obstruction
            elif isinstance(task.joint,CrossPinJoin):
                # Keep a collision certificate when live join replay returns one.
                witness=task.joint.advance(max_new_edges=0)
                obstruction=witness.obstruction
            candidate=ComparedCandidate(label,result.status,result.expected_digest,
                   result.observed_digest, sum(x.admitted for x in checks),len(checks),obstruction)
            results.append(candidate)
            if result.status=='TASK_COMPLETED_ON_JOINT_WITNESS':
                finished.append(label)
            if result.status in {'TASK_COMPLETED_ON_JOINT_WITNESS','TASK_REQUIREMENTS_UNPROVED'}:
                ready+=1
        if finished:
            status='TASK_COMPLETED_BY_INDEPENDENT_WITNESS'
        elif ready == len(results):
            status='TASK_UNPROVED_ACROSS_TESTED_WITNESSES'
        else:
            status='COMPARISON_WITH_UNAVAILABLE_EVIDENCE'
        return ComparisonResult(status,self.contract_fingerprint,tuple(results),tuple(finished),
                    'Per-join results are independent; no states, transitions or obligations are combined.')
