"""CP-native NIH ontology mapping through EXISTING workstation and HandoffRuntime.

The independent host verifier parses RDF/Turtle and checks its graph against the
freshly reverified parent scope's synthetic observations, not worker assertions.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json
import subprocess
import sys
from uuid import uuid4

from runtime.engine import HandoffRuntime
from runtime.handoff import EvidenceRecord, ExecutionResult, Handoff
from .nih_scope_bridge import NIHScopeBridge, WORKER_ID as SCOPE_ID
from .nih_scope_native import CP_ID as SCOPE_CP, VERIFIER as SCOPE_VERIFIER, validate_scope
from .nih_ontology_native import CP_ID, WORKER_ROLE, VERIFIER, validate_request, verify_report
from .workstation import ProcessWorkstation

WORKER_ID='nih-temporal-ontology'
SOURCE_FILE='ontology_worker.py'
SOURCE_DIRECTORY=Path(__file__).resolve().parent/'nih_ontology_worker_source'
LOCATOR='repo:systems/workspace/nih_ontology_worker_source/ontology_worker.py'
RELATION='map verified synthetic temporal scope to OWL-Time PROV-O Biolink RDF'
WITNESS='host-owned RDF graph equivalence after parent scope reverification'
SOURCE='native synthetic ontology graph comparison'


def copy_ontology_source(data_dir: str | Path, *, version_id: str, allow_copy: bool=False):
    if not allow_copy: raise PermissionError('explicit ontology source-copy consent required')
    desk=ProcessWorkstation(Path(data_dir)/'workstation')
    return desk.copy_source(SOURCE_DIRECTORY,worker_id=WORKER_ID,version_id=version_id,source_locator=LOCATOR)


def run_source(edition:Path, inputs:dict)->dict:
    try:
        proc=subprocess.run([sys.executable,'-I',str(edition/SOURCE_FILE)],cwd=edition,
             input=json.dumps(inputs,sort_keys=True),text=True,stdout=subprocess.PIPE,
             stderr=subprocess.PIPE,check=False,timeout=10)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError('ontology worker timed out') from exc
    if proc.returncode or len(proc.stdout)>70000 or len(proc.stderr)>8192:
        raise ValueError('source edition did not produce valid bounded ontology output')
    try: result=json.loads(proc.stdout)
    except ValueError as exc:raise ValueError('ontology worker output not JSON') from exc
    if type(result) is not dict or set(result)!={'report','pid'} or type(result['pid']) is not int or result['pid']<=0:
        raise ValueError('ontology subprocess output shape mismatch')
    return result


@dataclass(frozen=True)
class OntologyWorker:
    bridge:'NIHOntologyBridge'
    job_id:str
    @property
    def actor_id(self):return self.bridge.runtime.get(self.job_id).to_actor
    def can_execute(self,handoff:Handoff):
        return handoff.handoff_id==self.job_id and handoff.to_actor==self.actor_id and handoff.required_relation==RELATION
    def execute(self,handoff:Handoff)->ExecutionResult:
        if not self.can_execute(handoff):raise ValueError('ontology task mismatch')
        location=self.bridge._pinned(handoff)
        report=run_source(location,handoff.inputs)
        fp=handoff.metadata['edition_fingerprint']
        return ExecutionResult(status='COMPLETE',output={
            'kind':'nih-synthetic-rdf-mapping/v1','checkpoint_contract':CP_ID,
            'checkpoint_verdict':'PASS','checkpoint_worker_role':WORKER_ROLE,
            'native_verifier':VERIFIER,'report':report['report'],
            'scope_job_id':handoff.inputs['request']['scope_job_id'],
            'worker_version':handoff.metadata['worker_version'],
            'edition_fingerprint':fp,'child_pid':report['pid']},
            evidence=(EvidenceRecord(condition=WITNESS,kind='computation',source=SOURCE,
                                     ref=fp,depth='host-rdf-parse-and-graph-comparison'),))


class NIHOntologyBridge:
    def __init__(self, *, runtime:HandoffRuntime, workstation:ProcessWorkstation,
                 scope_bridge:NIHScopeBridge | None=None):
        self.runtime=runtime
        self.workstation=workstation
        self.scope_bridge=scope_bridge if scope_bridge is not None else NIHScopeBridge(runtime=runtime,workstation=workstation)
        runtime.register_evidence_verifier(VERIFIER,self._verify)

    def _parent(self,request:dict)->Handoff:
        parent=self.runtime.get(request['scope_job_id'])
        m=parent.metadata
        if (m.get('worker_id')!=SCOPE_ID or m.get('checkpoint_contract')!=SCOPE_CP
             or m.get('native_evidence_verifier')!=SCOPE_VERIFIER or parent.handoff_id!=request['scope_job_id']):
            raise ValueError('ontology parent must be an exact native Phase 1 scope job')
        if self.runtime.state(parent.handoff_id).status!='COMPLETE':
            raise ValueError('parent scope job has not completed')
        # CRITICAL: fresh host-owned scope recheck; a historical COMPLETE is insufficient.
        self.scope_bridge.reverify(parent.handoff_id)
        validate_scope(parent.inputs)
        return parent

    def _pinned(self,handoff:Handoff)->Path:
        m=handoff.metadata
        if (m.get('worker_id')!=WORKER_ID or m.get('checkpoint_contract')!=CP_ID
           or m.get('source_system')!='process-workstation' or m.get('native_evidence_verifier')!=VERIFIER):
            raise ValueError('not native NIH ontology handoff')
        version=m.get('worker_version')
        folder,record=self.workstation._read(WORKER_ID,version)
        current=self.workstation.inspect(worker_id=WORKER_ID,version_id=version)
        if (record['source_locator']!=LOCATOR or current['current_fingerprint']!=m.get('edition_fingerprint')
            or SOURCE_FILE not in self.workstation._inventory_edition(folder)):
            raise ValueError('NIH ontology edition changed or source missing')
        request=validate_request(handoff.inputs['request'])
        parent=self._parent(request)
        if validate_scope(handoff.inputs['scope'])!=validate_scope(parent.inputs):
            raise ValueError('parent scope differs from admitted ontology inputs')
        if handoff.dependencies!=(parent.handoff_id,):
            raise ValueError('ontology dependency must name exact scope job')
        return folder

    def admit(self, *, version_id:str, inputs:dict, from_actor:str,
              job_id:str|None=None,lane_id:str='nih')->Handoff:
        if type(from_actor) is not str or not from_actor.strip():
            raise ValueError('explicit ontology operator required')
        req=validate_request(inputs)
        parent=self._parent(req)
        scope=validate_scope(parent.inputs)
        info=self.workstation.inspect(worker_id=WORKER_ID,version_id=version_id)
        fingerprint=info['current_fingerprint']
        h=Handoff(handoff_id=job_id or ('nih-ontology-'+uuid4().hex),
            referent=f'NIH Phase 1 / synthetic RDF temporal ontology / {version_id}',
            from_actor=from_actor.strip(),to_actor=f'nih-temporal-ontology:{version_id}',
            required_relation=RELATION, inputs={'request':req,'scope':scope},
            expected_output={'kind':'nih-synthetic-rdf-mapping/v1','clinical_verdict':'NOT_EVALUATED'},
            required_witnesses=(WITNESS,),admissible_evidence={WITNESS:('computation',)},
            dependencies=(parent.handoff_id,),
            boundaries=('Only synthetic metadata, no patient identifiers or PHI.',
                       'RDF/Turtle structural mapping, not OWL entailment or clinical reasoning.',
                       'COMPLETE means this specific graph was checked; not NIH Phase 1 success.',
                       'Source child process is not an operating-system sandbox.'),
            provenance=(f'worker-edition:{WORKER_ID}:{version_id}',
                f'source-fingerprint:{fingerprint}',f'scope-job:{parent.handoff_id}',
                f'workspace-lane:{lane_id}'),
            metadata={'title':'NIH Phase 1 synthetic temporal ontology mapping',
                'source_system':'process-workstation','worker_id':WORKER_ID,
                'worker_version':version_id,'edition_fingerprint':fingerprint,
                'checkpoint_contract':CP_ID,'native_evidence_verifier':VERIFIER})
        self._pinned(h)
        self.runtime.submit(h)
        return h

    def _verify(self,handoff:Handoff,result:ExecutionResult):
        self._pinned(handoff)
        if result.status!='COMPLETE':raise ValueError('ontology computation not completed')
        fp=handoff.metadata['edition_fingerprint']
        expected=(EvidenceRecord(condition=WITNESS,kind='computation',source=SOURCE,
                   ref=fp,depth='host-rdf-parse-and-graph-comparison'),)
        if result.evidence!=expected:raise ValueError('ontology worker witness mismatch')
        out=result.output
        keys={'kind','checkpoint_contract','checkpoint_verdict','checkpoint_worker_role',
              'native_verifier','report','scope_job_id','worker_version','edition_fingerprint','child_pid'}
        req=handoff.inputs['request']
        if (type(out) is not dict or set(out)!=keys or out['kind']!='nih-synthetic-rdf-mapping/v1'
             or (out['checkpoint_contract'],out['checkpoint_verdict'],out['checkpoint_worker_role'],out['native_verifier'])!=(CP_ID,'PASS',WORKER_ROLE,VERIFIER)
             or out['scope_job_id']!=req['scope_job_id']
             or out['worker_version']!=handoff.metadata['worker_version']
             or out['edition_fingerprint']!=fp
             or type(out['child_pid']) is not int or out['child_pid']<=0):
            raise ValueError('ontology worker exact source/proof contract mismatch')
        verify_report(out['report'],scope=handoff.inputs['scope'],mapping_id=req['mapping_id'])

    def execute(self,job_id:str,*,allow_local_execution:bool=False):
        if not allow_local_execution:raise PermissionError('ontology execution requires exact operator confirmation')
        h=self.runtime.get(job_id)
        self._pinned(h)
        return self.runtime.run(job_id,OntologyWorker(self,job_id))

    def reverify(self,job_id:str)->bool:
        state=self.runtime.state(job_id)
        if state.status!='COMPLETE':raise ValueError('only completed ontology jobs can reverify')
        self._verify(self.runtime.get(job_id),ExecutionResult(status='COMPLETE',output=state.output,evidence=state.evidence))
        return True