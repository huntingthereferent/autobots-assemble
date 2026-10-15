"""Third CP-native NIH worker: RDF temporal queries, without a second scheduler.

Exact parent ontology source and its scope ancestor are freshly reverified;
worker reads the parent's already-validated RDF; host checks each inference
independently from original scope observation tokens and explicit assumptions.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json, subprocess, sys
from uuid import uuid4

from runtime.engine import HandoffRuntime
from runtime.handoff import EvidenceRecord, ExecutionResult, Handoff
from .workstation import ProcessWorkstation
from .nih_ontology_bridge import NIHOntologyBridge, WORKER_ID as ONTO_ID
from .nih_ontology_native import CP_ID as ONTO_CP, VERIFIER as ONTO_VERIFIER
from .nih_reasoning_native import CP_ID, WORKER_ROLE, VERIFIER, validate_request, verify_reasoning_report

WORKER_ID='nih-temporal-reasoning'
SOURCE_FILE='reasoning_worker.py'
SOURCE_DIRECTORY=Path(__file__).resolve().parent/'nih_reasoning_worker_source'
LOCATOR='repo:systems/workspace/nih_reasoning_worker_source/reasoning_worker.py'
RELATION='verify as-known-at RDF queries with explicit contradiction constraints'
WITNESS='host-owned temporal queries match source-independent replay'
SOURCE='native synthetic multi-time RDF temporal query verifier'


def copy_reasoning_source(data_dir: str | Path, *, version_id:str, allow_copy:bool=False):
    if not allow_copy:raise PermissionError('explicit trusted source-copy required')
    return ProcessWorkstation(Path(data_dir)/'workstation').copy_source(
        SOURCE_DIRECTORY,worker_id=WORKER_ID,version_id=version_id,source_locator=LOCATOR)


def run_source(edition:Path,inputs:dict):
    try:
        proc=subprocess.run([sys.executable,'-I',str(edition/SOURCE_FILE)],cwd=edition,
                            input=json.dumps(inputs,sort_keys=True),text=True,
                            stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                            check=False,timeout=12)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError('temporal reasoning subprocess timed out') from exc
    if proc.returncode or len(proc.stdout)>24000 or len(proc.stderr)>8192:
        raise ValueError('reasoning worker failed bounded execution contract')
    try:value=json.loads(proc.stdout)
    except ValueError as exc:raise ValueError('reasoning worker returned invalid JSON') from exc
    if type(value) is not dict or set(value)!={'pid','report'} or type(value['pid']) is not int or value['pid']<=0:
        raise ValueError('reasoning worker output contract mismatch')
    return value


@dataclass(frozen=True)
class ReasoningWorker:
    bridge:'NIHReasoningBridge'
    job_id:str
    @property
    def actor_id(self):return self.bridge.runtime.get(self.job_id).to_actor
    def can_execute(self,handoff:Handoff):
        return handoff.handoff_id==self.job_id and handoff.to_actor==self.actor_id and handoff.required_relation==RELATION
    def execute(self,handoff:Handoff):
        if not self.can_execute(handoff):raise ValueError('incorrect reasoning worker task')
        folder=self.bridge._pinned(handoff)
        source=run_source(folder,handoff.inputs)
        fp=handoff.metadata['edition_fingerprint']
        return ExecutionResult(status='COMPLETE',output={
            'kind':'nih-synthetic-temporal-reasoning/v1','checkpoint_contract':CP_ID,
            'checkpoint_verdict':'PASS','checkpoint_worker_role':WORKER_ROLE,
            'native_verifier':VERIFIER,'report':source['report'],
            'ontology_job_id':handoff.inputs['request']['ontology_job_id'],
            'edition_fingerprint':fp,'worker_version':handoff.metadata['worker_version'],
            'child_pid':source['pid']},
            evidence=(EvidenceRecord(condition=WITNESS,kind='computation',source=SOURCE,
                                    ref=fp,depth='host-source-independent-temporal-replay'),))


class NIHReasoningBridge:
    def __init__(self,*,runtime:HandoffRuntime,workstation:ProcessWorkstation,
                 ontology_bridge:NIHOntologyBridge|None=None):
        self.runtime,self.workstation=runtime,workstation
        self.ontology_bridge=ontology_bridge or NIHOntologyBridge(runtime=runtime,workstation=workstation)
        runtime.register_evidence_verifier(VERIFIER,self._verify)

    def _parent(self,request:dict)->Handoff:
        h=self.runtime.get(request['ontology_job_id'])
        if (h.metadata.get('worker_id')!=ONTO_ID or h.metadata.get('checkpoint_contract')!=ONTO_CP
            or h.metadata.get('native_evidence_verifier')!=ONTO_VERIFIER):
            raise ValueError('exact CP-native ontology parent required')
        if self.runtime.state(h.handoff_id).status!='COMPLETE':
            raise ValueError('ontology parent has not completed')
        # Fresh ontology reverify recursively checks exact scope source and RDF.
        self.ontology_bridge.reverify(h.handoff_id)
        return h

    def _pinned(self,handoff:Handoff)->Path:
        meta=handoff.metadata
        if (meta.get('source_system')!='process-workstation' or meta.get('worker_id')!=WORKER_ID
            or meta.get('checkpoint_contract')!=CP_ID or meta.get('native_evidence_verifier')!=VERIFIER):
            raise ValueError('not a native NIH reasoning handoff')
        folder,record=self.workstation._read(WORKER_ID,meta.get('worker_version'))
        checked=self.workstation.inspect(worker_id=WORKER_ID,version_id=meta.get('worker_version'))
        if (record['source_locator']!=LOCATOR or checked['current_fingerprint']!=meta.get('edition_fingerprint')
            or SOURCE_FILE not in self.workstation._inventory_edition(folder)):
            raise ValueError('reasoning source changed or source provenance missing')
        req=validate_request(handoff.inputs['request'])
        h=self._parent(req)
        parent_result=self.runtime.state(h.handoff_id).output
        scope=h.inputs['scope']
        if handoff.inputs['ontology_turtle']!=parent_result['report']['turtle']:
            raise ValueError('reasoning RDF differs from native ontology parent')
        if handoff.inputs['scope']!=scope or handoff.inputs['mapping_id']!=h.inputs['request']['mapping_id']:
            raise ValueError('reasoning ancestor metadata differs from ontology job')
        if handoff.dependencies!=(h.handoff_id,):
            raise ValueError('reasoning dependency must name exact ontology job')
        return folder

    def admit(self,*,version_id:str,inputs:dict,from_actor:str,job_id:str|None=None,lane_id:str='nih')->Handoff:
        if type(from_actor) is not str or not from_actor.strip():
            raise ValueError('explicit operator required')
        req=validate_request(inputs)
        h=self._parent(req)
        parent_result=self.runtime.state(h.handoff_id).output
        checked=self.workstation.inspect(worker_id=WORKER_ID,version_id=version_id)
        fp=checked['current_fingerprint']
        handoff=Handoff(
            handoff_id=job_id or 'nih-reasoning-'+uuid4().hex,
            referent=f'NIH Phase 1 / synthetic RDF temporal reasoning / {version_id}',
            from_actor=from_actor.strip(),to_actor=f'nih-temporal-reasoning:{version_id}',
            required_relation=RELATION,
            inputs={'request':req,'scope':h.inputs['scope'],
                    'ontology_turtle':parent_result['report']['turtle'],
                    'mapping_id':h.inputs['request']['mapping_id']},
            expected_output={'kind':'nih-synthetic-temporal-reasoning/v1','clinical_verdict':'NOT_EVALUATED'},
            required_witnesses=(WITNESS,),admissible_evidence={WITNESS:('computation',)},
            dependencies=(h.handoff_id,),
            boundaries=('Synthetic RDF only, no patient facts or clinical conclusion.',
                        'Functional constraints apply only to explicitly named predicates.',
                        'RDF graph query and finite negative controls, not general OWL entailment.',
                        'COMPLETE is a bounded computation, not an NIH submission.',
                        'Copied Python is not OS-sandboxed.'),
            provenance=(f'worker-edition:{WORKER_ID}:{version_id}',
                       f'source-fingerprint:{fp}',f'ontology-job:{h.handoff_id}',
                       f'workspace-lane:{lane_id}'),
            metadata={'title':'NIH Phase 1 synthetic multi-time RDF reasoning',
                      'source_system':'process-workstation','worker_id':WORKER_ID,
                      'worker_version':version_id,'edition_fingerprint':fp,
                      'checkpoint_contract':CP_ID,'native_evidence_verifier':VERIFIER})
        self._pinned(handoff)
        self.runtime.submit(handoff)
        return handoff

    def _verify(self,handoff:Handoff,result:ExecutionResult):
        self._pinned(handoff)
        if result.status!='COMPLETE':raise ValueError('reasoning task not completed')
        fp=handoff.metadata['edition_fingerprint']
        expected_evidence=(EvidenceRecord(condition=WITNESS,kind='computation',source=SOURCE,
                                          ref=fp,depth='host-source-independent-temporal-replay'),)
        if result.evidence!=expected_evidence:
            raise ValueError('reasoning computation evidence/source mismatch')
        out=result.output
        keys={'kind','checkpoint_contract','checkpoint_verdict','checkpoint_worker_role','native_verifier',
              'report','ontology_job_id','edition_fingerprint','worker_version','child_pid'}
        if (type(out) is not dict or set(out)!=keys or out['kind']!='nih-synthetic-temporal-reasoning/v1'
            or (out['checkpoint_contract'],out['checkpoint_verdict'],out['checkpoint_worker_role'],out['native_verifier'])
                !=(CP_ID,'PASS',WORKER_ROLE,VERIFIER)
            or out['ontology_job_id']!=handoff.inputs['request']['ontology_job_id']
            or out['edition_fingerprint']!=fp or out['worker_version']!=handoff.metadata['worker_version']
            or type(out['child_pid']) is not int or out['child_pid']<=0):
            raise ValueError('reasoning native CP result contract mismatch')
        verify_reasoning_report(out['report'],request=handoff.inputs['request'],
            scope=handoff.inputs['scope'],ontology_report=self.runtime.state(handoff.dependencies[0]).output['report'],
            mapping_id=handoff.inputs['mapping_id'])

    def execute(self,job_id:str,*,allow_local_execution:bool=False):
        if not allow_local_execution:raise PermissionError('reasoning worker requires explicit execution')
        handoff=self.runtime.get(job_id)
        self._pinned(handoff)
        return self.runtime.run(job_id,ReasoningWorker(self,job_id))

    def reverify(self,job_id:str):
        state=self.runtime.state(job_id)
        if state.status!='COMPLETE':raise ValueError('only completed temporal jobs can be reverified')
        self._verify(self.runtime.get(job_id),ExecutionResult(
            status='COMPLETE',output=state.output,evidence=state.evidence))
        return True