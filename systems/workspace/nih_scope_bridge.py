"""One bounded NIH Phase 1 scope worker over the existing Process Workstation.

Source-copy, admission, execution and native verification remain separate.
The host verifier does not import the copied source. No clinical inference.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import subprocess
import sys
from uuid import uuid4

from runtime.engine import HandoffRuntime
from runtime.handoff import EvidenceRecord, ExecutionResult, Handoff
from .nih_scope_native import CP_ID, VERIFIER, WORKER_ROLE, validate_scope, expected_scope_report
from .workstation import ProcessWorkstation

WORKER_ID = 'nih-temporal-scope'
SOURCE_FILE = 'nih_scope_source.py'
SOURCE_DIRECTORY = Path(__file__).resolve().parent / 'nih_scope_worker_source'
RELATION = 'verify synthetic temporal knowledge cutoff scope'
WITNESS = 'host-owned temporal scope replay matched source result'
SOURCE = 'native synthetic as-known-at scope verifier'


def copy_scope_source(data_dir: str | Path, *, version_id: str, allow_copy: bool = False):
    if not allow_copy:
        raise PermissionError('explicit source-copy consent required')
    desk = ProcessWorkstation(Path(data_dir) / 'workstation')
    return desk.copy_source(SOURCE_DIRECTORY, worker_id=WORKER_ID, version_id=version_id,
                            source_locator='repo:systems/workspace/nih_scope_worker_source/nih_scope_source.py')


def run_source(edition: Path, inputs: dict) -> dict:
    try:
        child = subprocess.run([sys.executable,'-I',str(edition/SOURCE_FILE)],
                               cwd=edition,input=json.dumps(inputs,sort_keys=True),
                               stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                               text=True,check=False,timeout=8)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError('synthetic scope worker timed out') from exc
    if child.returncode or len(child.stdout) > 4096 or len(child.stderr) > 4096:
        raise ValueError('source edition failed synthetic scope contract')
    try:
        parsed = json.loads(child.stdout)
    except ValueError as exc:
        raise ValueError('scope worker output not JSON') from exc
    if type(parsed) is not dict or set(parsed) != {'report','pid'} or type(parsed['pid']) is not int or parsed['pid'] <= 0:
        raise ValueError('scope worker output shape incorrect')
    return parsed


@dataclass(frozen=True)
class ScopeWorker:
    bridge: 'NIHScopeBridge'
    job_id: str

    @property
    def actor_id(self):
        return self.bridge.runtime.get(self.job_id).to_actor

    def can_execute(self, handoff: Handoff):
        return (handoff.handoff_id == self.job_id and handoff.to_actor == self.actor_id
                and handoff.required_relation == RELATION)

    def execute(self, handoff: Handoff):
        if not self.can_execute(handoff):
            raise ValueError('incorrect scope worker')
        edition = self.bridge._pinned(handoff)
        observed = run_source(edition,handoff.inputs)
        fingerprint = handoff.metadata['edition_fingerprint']
        report = observed['report']
        return ExecutionResult(status='COMPLETE', output={
            'kind':'nih-synthetic-temporal-scope/v1',
            'checkpoint_contract':CP_ID, 'checkpoint_verdict':'PASS',
            'checkpoint_worker_role':WORKER_ROLE, 'native_verifier':VERIFIER,
            'report':report, 'worker_version':handoff.metadata['worker_version'],
            'edition_fingerprint':fingerprint,'child_pid':observed['pid']},
            evidence=(EvidenceRecord(condition=WITNESS,kind='computation',source=SOURCE,
                  ref=fingerprint,depth='independent-host-replay'),))


class NIHScopeBridge:
    def __init__(self, *, runtime: HandoffRuntime, workstation: ProcessWorkstation):
        self.runtime, self.workstation = runtime, workstation
        runtime.register_evidence_verifier(VERIFIER,self._verify)

    def _pinned(self, handoff: Handoff) -> Path:
        m=handoff.metadata
        if (m.get('source_system') != 'process-workstation'
            or m.get('worker_id') != WORKER_ID or m.get('checkpoint_contract') != CP_ID
            or m.get('native_evidence_verifier') != VERIFIER):
            raise ValueError('not a native NIH scope handoff')
        version=m.get('worker_version')
        folder, record=self.workstation._read(WORKER_ID,version)
        if record['source_locator'] != 'repo:systems/workspace/nih_scope_worker_source/nih_scope_source.py':
            raise ValueError('wrong scope worker source locator')
        report=self.workstation.inspect(worker_id=WORKER_ID,version_id=version)
        if report['current_fingerprint'] != m.get('edition_fingerprint') or SOURCE_FILE not in self.workstation._inventory_edition(folder):
            raise ValueError('NIH scope edition changed or missing source')
        return folder

    def admit(self, *, version_id: str, inputs: dict, from_actor: str, job_id: str | None = None, lane_id: str = 'nih') -> Handoff:
        if not isinstance(from_actor,str) or not from_actor.strip():
            raise ValueError('explicit admission actor required')
        canonical=validate_scope(inputs)
        inspected=self.workstation.inspect(worker_id=WORKER_ID,version_id=version_id)
        fp=inspected['current_fingerprint']
        handoff=Handoff(
            handoff_id=job_id or 'nih-scope-'+uuid4().hex,
            referent=f'NIH Phase 1 / synthetic temporal scope / {version_id}',
            from_actor=from_actor.strip(),to_actor=f'nih-temporal-scope:{version_id}',
            required_relation=RELATION,inputs=canonical,
            expected_output={'kind':'nih-synthetic-temporal-scope/v1','research_scope_only':True},
            required_witnesses=(WITNESS,),admissible_evidence={WITNESS:('computation',)},
            boundaries=('Only synthetic metadata; no protected health data.',
                'No biomedical ontology, clinical validation or NIH award claim.',
                'COMPLETE refers only to the finite as-known-at scope computation.',
                'Copied Python is not OS-sandboxed.'),
            provenance=(f'worker-edition:{WORKER_ID}:{version_id}',f'source-fingerprint:{fp}',
                        f'workspace-lane:{lane_id}'),
            metadata={'title':'NIH Phase 1 synthetic temporal scope',
                'source_system':'process-workstation','worker_id':WORKER_ID,
                'worker_version':version_id,'edition_fingerprint':fp,
                'native_evidence_verifier':VERIFIER,'checkpoint_contract':CP_ID})
        self._pinned(handoff)
        self.runtime.submit(handoff)
        return handoff

    def _verify(self, handoff: Handoff, result: ExecutionResult):
        self._pinned(handoff)
        if result.status != 'COMPLETE':
            raise ValueError('scope computation not completed')
        fingerprint=handoff.metadata['edition_fingerprint']
        if result.evidence != (EvidenceRecord(condition=WITNESS,kind='computation',source=SOURCE,
                                            ref=fingerprint,depth='independent-host-replay'),):
            raise ValueError('scope result evidence mismatch')
        value=result.output
        keys={'kind','checkpoint_contract','checkpoint_verdict','checkpoint_worker_role','native_verifier',
              'report','worker_version','edition_fingerprint','child_pid'}
        if (type(value) is not dict or set(value) != keys
            or value['kind'] != 'nih-synthetic-temporal-scope/v1'
            or (value['checkpoint_contract'],value['checkpoint_verdict'],value['checkpoint_worker_role'],value['native_verifier']) != (CP_ID,'PASS',WORKER_ROLE,VERIFIER)
            or value['worker_version'] != handoff.metadata['worker_version']
            or value['edition_fingerprint'] != fingerprint
            or type(value['child_pid']) is not int or value['child_pid'] <= 0):
            raise ValueError('scope worker contract mismatch')
        if value['report'] != expected_scope_report(handoff.inputs):
            raise ValueError('host verifier rejected scope report')

    def execute(self, job_id: str, *, allow_local_execution: bool = False):
        if not allow_local_execution:
            raise PermissionError('explicit scoped worker execution required')
        handoff=self.runtime.get(job_id)
        self._pinned(handoff)
        return self.runtime.run(job_id,ScopeWorker(self,job_id))

    def reverify(self, job_id: str):
        state=self.runtime.state(job_id)
        if state.status != 'COMPLETE':
            raise ValueError('only completed scope jobs can reverify')
        self._verify(self.runtime.get(job_id),ExecutionResult(status='COMPLETE',output=state.output,evidence=state.evidence))
        return True