"""W13 game worker over the EXISTING source-pinned Process Workstation.

Executes a concrete multi-world game composition against preserved W12 rules.
Not a generative coding agent, autonomous scheduler, or browser-origin witness.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import json
import subprocess
import sys
from uuid import uuid4

from runtime.engine import HandoffRuntime
from runtime.handoff import EvidenceRecord, ExecutionResult, Handoff
from .workstation import ProcessWorkstation
from .game_w13_native import (CP_ID, VERIFIER, WORKER_ROLE, W12_SHA256,
                               canonical, check_preserved_reference,
                               expected_report, validate_request)

WORKER_ID='game-w13-world-builder'
SOURCE_FILE='w13_worker.py'
FILES={'game_w12_reference.py','w13_engine.py',SOURCE_FILE}
SOURCE_DIRECTORY=Path(__file__).resolve().parent/'game_w13_worker_source'
LOCATOR='repo:systems/workspace/game_w13_worker_source'
RELATION='compose a bounded W13 multi-world game over W12 rules'
WITNESS='W13 multi-world replay matches preserved W12 native rules'
SOURCE='source-independent W13 native replay of W12 worlds'


def copy_game_source(data_dir: str|Path, *, version_id: str, allow_copy: bool=False):
    if not allow_copy:
        raise PermissionError('W13 source copy requires explicit permission')
    check_preserved_reference()
    if sha256((SOURCE_DIRECTORY/'game_w12_reference.py').read_bytes()).hexdigest()!=W12_SHA256:
        raise ValueError('W12 source embedded in W13 worker changed')
    return ProcessWorkstation(Path(data_dir)/'workstation').copy_source(
        SOURCE_DIRECTORY,worker_id=WORKER_ID,version_id=version_id,source_locator=LOCATOR)


def run_source(edition: Path, request: dict) -> dict:
    try:
        child=subprocess.run([sys.executable,'-I',str(edition/SOURCE_FILE)],
                             cwd=edition,input=canonical(request),text=True,
                             capture_output=True,timeout=10,check=False)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError('W13 worker timed out') from exc
    if child.returncode or len(child.stdout)>150000 or len(child.stderr)>4096:
        raise ValueError('W13 source edition failed or exceeded output limit')
    try:
        result=json.loads(child.stdout)
    except ValueError as exc:
        raise ValueError('W13 output not JSON') from exc
    if type(result) is not dict or set(result)!={'report','pid'} or type(result['pid']) is not int or result['pid']<=0:
        raise ValueError('W13 source return shape invalid')
    return result


@dataclass(frozen=True)
class GameW13Worker:
    bridge: 'GameW13Bridge'
    job_id: str

    @property
    def actor_id(self):
        return self.bridge.runtime.get(self.job_id).to_actor

    def can_execute(self, handoff: Handoff):
        return (handoff.handoff_id==self.job_id and handoff.to_actor==self.actor_id
                and handoff.required_relation==RELATION)

    def execute(self, handoff: Handoff):
        if not self.can_execute(handoff):
            raise ValueError('wrong W13 worker')
        edition=self.bridge._pinned(handoff)
        result=run_source(edition,handoff.inputs)
        fp=handoff.metadata['edition_fingerprint']
        return ExecutionResult(status='COMPLETE',output={
            'kind':'game-w13-multiworld-build/v1',
            'checkpoint_contract':CP_ID,'checkpoint_verdict':'CANDIDATE',
            'checkpoint_worker_role':WORKER_ROLE,'native_verifier':VERIFIER,
            'report':result['report'],'worker_version':handoff.metadata['worker_version'],
            'edition_fingerprint':fp,'child_pid':result['pid']},
            evidence=(EvidenceRecord(condition=WITNESS,kind='computation',source=SOURCE,
                                    ref=fp,depth='native-W12-replay'),))


class GameW13Bridge:
    def __init__(self, *, runtime: HandoffRuntime, workstation: ProcessWorkstation):
        self.runtime,self.workstation=runtime,workstation
        runtime.register_evidence_verifier(VERIFIER,self._verify)

    def _pinned(self, handoff: Handoff) -> Path:
        meta=handoff.metadata
        if (meta.get('source_system')!='process-workstation'
            or meta.get('worker_id')!=WORKER_ID
            or meta.get('native_evidence_verifier')!=VERIFIER
            or meta.get('checkpoint_contract')!=CP_ID):
            raise ValueError('not a valid W13 source-pinned handoff')
        version=meta.get('worker_version')
        folder,edition=self.workstation._read(WORKER_ID,version)
        if edition['source_locator']!=LOCATOR:
            raise ValueError('wrong W13 source locator')
        state=self.workstation.inspect(worker_id=WORKER_ID,version_id=version)
        if state['current_fingerprint']!=meta.get('edition_fingerprint'):
            raise ValueError('W13 worker source changed after admission')
        if not FILES <= set(self.workstation._inventory_edition(folder)):
            raise ValueError('W13 worker edition missing files')
        check_preserved_reference()
        if sha256((folder/'game_w12_reference.py').read_bytes()).hexdigest()!=W12_SHA256:
            raise ValueError('preserved W12 rule source modified')
        return folder

    def admit(self, *, version_id: str, inputs: dict, from_actor: str,
              job_id: str|None=None, lane_id: str='game') -> Handoff:
        if type(from_actor) is not str or not from_actor.strip():
            raise ValueError('actor required for explicit W13 admission')
        payload=validate_request(inputs)
        check_preserved_reference()
        expected_report(payload)  # reject impossible completion before source admission
        info=self.workstation.inspect(worker_id=WORKER_ID,version_id=version_id)
        fp=info['current_fingerprint']
        handoff=Handoff(
            handoff_id=job_id or 'game-w13-'+uuid4().hex,
            referent=f'GAME W13 bounded multi-world composition / {version_id}',
            from_actor=from_actor.strip(),to_actor=f'game-w13-worker:{version_id}',
            required_relation=RELATION,inputs=payload,
            expected_output={'kind':'game-w13-multiworld-build/v1','rules':'unchanged-W12'},
            required_witnesses=(WITNESS,),admissible_evidence={WITNESS:('computation',)},
            boundaries=('Only deterministic multi-world composition is witnessed; full W13 stays open.',
                        'No AI-generated game implementation or autonomous follow-on jobs.',
                        'W12 strict verifier, native rules and receipts are unchanged.',
                        'Child Python subprocess is not a security sandbox.'),
            provenance=(f'worker-edition:{WORKER_ID}:{version_id}',f'source-fingerprint:{fp}',
                        f'workspace-lane:{lane_id}',f'W12-original-sha256:{W12_SHA256}'),
            metadata={'source_system':'process-workstation','title':'W13 multi-world build',
                      'worker_id':WORKER_ID,'worker_version':version_id,
                      'edition_fingerprint':fp,'native_evidence_verifier':VERIFIER,
                      'checkpoint_contract':CP_ID})
        self._pinned(handoff)
        self.runtime.submit(handoff)
        return handoff

    def _verify(self, handoff: Handoff, result: ExecutionResult):
        self._pinned(handoff)
        if result.status!='COMPLETE':
            raise ValueError('W13 worker did not complete')
        fp=handoff.metadata['edition_fingerprint']
        witness=(EvidenceRecord(condition=WITNESS,kind='computation',source=SOURCE,
                                ref=fp,depth='native-W12-replay'),)
        if result.evidence!=witness:
            raise ValueError('W13 witness shape or source mismatch')
        value=result.output
        fields={'kind','checkpoint_contract','checkpoint_verdict','checkpoint_worker_role',
                'native_verifier','report','worker_version','edition_fingerprint','child_pid'}
        if (type(value)is not dict or set(value)!=fields
            or value['kind']!='game-w13-multiworld-build/v1'
            or (value['checkpoint_contract'],value['checkpoint_verdict'],value['checkpoint_worker_role'],value['native_verifier'])!=(CP_ID,'CANDIDATE',WORKER_ROLE,VERIFIER)
            or value['worker_version']!=handoff.metadata['worker_version']
            or value['edition_fingerprint']!=fp
            or type(value['child_pid'])is not int or value['child_pid']<=0):
            raise ValueError('W13 native contract metadata mismatch')
        if canonical(value['report']) != canonical(expected_report(handoff.inputs)):
            raise ValueError('native verifier rejects W13 multi-world trace')

    def execute(self, job_id: str, *, allow_local_execution: bool=False):
        if not allow_local_execution:
            raise PermissionError('W13 worker requires explicit execution')
        handoff=self.runtime.get(job_id)
        self._pinned(handoff)
        return self.runtime.run(job_id,GameW13Worker(self,job_id))

    def reverify(self, job_id: str):
        state=self.runtime.state(job_id)
        if state.status!='COMPLETE':
            raise ValueError('only COMPLETE W13 native job can reverify')
        self._verify(self.runtime.get(job_id),ExecutionResult(
            status='COMPLETE',output=state.output,evidence=state.evidence))
        return True