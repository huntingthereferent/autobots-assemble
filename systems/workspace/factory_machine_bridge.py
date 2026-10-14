"""Version-pinned workstation execution of one native Factory *simulation* stage.

Uses FactorySystem's source-owned machine handoff and native simulator replay,
shared HandoffRuntime/RuntimeJournal, and the reusable ProcessWorkstation.
No physical production or autonomous scheduler is connected.
"""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import json
import subprocess
import sys
from typing import Any

from runtime.engine import HandoffRuntime
from runtime.handoff import ExecutionResult, Handoff, SimulatedActor
from systems.factory.simulated import (FactorySimulationAdmission,
                                       FACTORY_SIMULATION_VERIFIER,
                                       default_simulated_actors)
from .workstation import ProcessWorkstation

WORKER_ID = 'factory-machine-simulation-process'
VERIFIER = 'workstation.factory.machine.simulation.v1'
_FILE = 'factory_machine_worker.py'


class FactoryMachineSimulationBridge:
    def __init__(self, *, runtime: HandoffRuntime, workstation: ProcessWorkstation):
        self.runtime = runtime
        self.workstation = workstation
        self.native = FactorySimulationAdmission(runtime)
        runtime.register_evidence_verifier(VERIFIER, self._verify)
        self.last_child_pid: int | None = None

    def _edition(self, handoff: Handoff) -> Path:
        md = handoff.metadata
        if (md.get('native_evidence_verifier') != VERIFIER or
                md.get('worker_id') != WORKER_ID or
                md.get('source_system') != 'factory' or
                md.get('stage') != 'machine' or
                md.get('workstation_worker') is not True):
            raise ValueError('not a workstation Factory machine-stage simulation')
        info = self.workstation.inspect(worker_id=WORKER_ID,
                                        version_id=md['worker_version'])
        if info['current_fingerprint'] != md.get('edition_fingerprint'):
            raise ValueError('machine worker source changed since admission')
        root = Path(info['path'])
        if _FILE not in self.workstation._inventory_edition(root):
            raise ValueError('required machine simulator source unavailable')
        return root

    def admit(self, handoff: Handoff, *, version_id: str,
              selection_event_id: str | None = None) -> Handoff:
        """Accept only an actual emitted Factory machine stage, never an arbitrary job."""
        self.native._check_handoff(handoff)
        if handoff.metadata.get('stage') != 'machine':
            raise ValueError('workstation currently supports only the Factory machine stage')
        info = self.workstation.inspect(worker_id=WORKER_ID, version_id=version_id)
        if _FILE not in self.workstation._inventory_edition(Path(info['path'])):
            raise ValueError('selected edition does not contain the Factory worker')
        marked = self.native.admit(handoff)
        marked = replace(marked, metadata={
            **marked.metadata,
            'native_evidence_verifier': VERIFIER,
            'workstation_worker': True,
            'worker_id': WORKER_ID,
            'worker_version': version_id,
            'edition_fingerprint': info['current_fingerprint'],
            **({'preferred_selection_event': selection_event_id} if selection_event_id else {}),
        }, provenance=(*marked.provenance,
                      f'worker-edition:{WORKER_ID}:{version_id}',
                      f'source-fingerprint:{info["current_fingerprint"]}',
                      *((f'preferred-selection:{selection_event_id}',) if selection_event_id else ()),
                      'workspace-lane:factory-simulation'))
        self.runtime.submit(marked)
        return marked

    def _verify(self, handoff: Handoff, result: ExecutionResult) -> None:
        """Require unchanged edition AND Factory's native simulation replay."""
        self._edition(handoff)
        native_handoff = replace(handoff, metadata={
            **handoff.metadata, 'native_evidence_verifier': FACTORY_SIMULATION_VERIFIER})
        self.native._verify(native_handoff, result)

    def execute(self, handoff_id: str, *, allow_local_execution: bool = False):
        if not allow_local_execution:
            raise PermissionError('machine worker needs explicit local execution approval')
        handoff = self.runtime.get(handoff_id)
        self._edition(handoff)
        if self.runtime.state(handoff_id).status != 'READY':
            raise ValueError('machine stage not READY')
        actor = SimulatedActor(actor_id=handoff.to_actor,
                               capabilities=(handoff.required_relation,),
                               handler=self._run_selected_edition)
        return self.runtime.run(handoff_id, actor)

    def _run_selected_edition(self, handoff: Handoff) -> ExecutionResult:
        edition = self._edition(handoff)
        source = edition / _FILE
        try:
            proc = subprocess.run([sys.executable, '-I', str(source)],
                                  cwd=edition, input=json.dumps(handoff.inputs), text=True,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  timeout=10, check=False)
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError('machine simulation child timed out') from exc
        if proc.returncode or len(proc.stdout) > 16384:
            raise RuntimeError('machine simulation child failed; no result admitted')
        try:
            reply = json.loads(proc.stdout)
        except ValueError as exc:
            raise ValueError('machine simulation returned invalid JSON') from exc
        if (not isinstance(reply, dict) or set(reply) != {'output', 'child_pid'} or
                not isinstance(reply['output'], dict) or
                type(reply['child_pid']) is not int or reply['child_pid'] <= 0):
            raise ValueError('machine simulation output contract mismatch')
        self.last_child_pid = reply['child_pid']
        expected = default_simulated_actors()[handoff.to_actor].execute(handoff)
        result = ExecutionResult(status='COMPLETE', output=reply['output'],
                                 evidence=expected.evidence)
        # The existing runtime admits the RESULT only after native verification.
        return result

    def reverify(self, handoff_id: str) -> bool:
        handoff = self.runtime.get(handoff_id)
        state = self.runtime.state(handoff_id)
        if state.status != 'COMPLETE':
            raise ValueError('only a completed simulation may be reverified')
        self._verify(handoff, ExecutionResult(status='COMPLETE',
                     output=state.output, evidence=state.evidence))
        return True
