"""True reuse: two unlike native computations, same workstation projection/journal."""
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from runtime.handoff import ExecutionResult
from runtime.examples.workstation_two_processes import populate, ORDER_ID, FCP_JOB
from systems.workspace.factory_machine_bridge import FactoryMachineSimulationBridge, WORKER_ID
from systems.workspace.workstation import ProcessWorkstation
from systems.workspace.monitor import workstation_snapshot


class TwoProcessWorkstationTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def runtime(self):
        return HandoffRuntime(event_store=RuntimeJournal(self.root / 'runtime.jsonl'))

    def test_opt_in_required_before_files_or_jobs(self):
        with self.assertRaises(PermissionError):
            populate(self.root)
        self.assertFalse((self.root / 'runtime.jsonl').exists())

    def test_two_very_different_processes_both_execute_and_render(self):
        view = populate(self.root, execute=True)
        self.assertEqual(view['counts']['workers'], 2)
        self.assertEqual(view['counts']['editions'], 3)
        experiment = next(e for e in view['editions'] if e['version_id'] == 'experiment-001')
        self.assertEqual(experiment['parent_version'], 'baseline-001')
        self.assertFalse(experiment['executed'])
        self.assertEqual(view['counts']['jobs'], 2)
        self.assertEqual(view['counts']['recorded_complete'], 2)
        self.assertEqual({x['realization'] for x in view['jobs']}, {'computed', 'simulated'})
        self.assertEqual({x['source_system'] for x in view['jobs']}, {'process-workstation', 'factory'})
        self.assertEqual(len(view['workspace']['lanes']), 2)
        for job in view['jobs']:
            self.assertEqual([e['event_type'] for e in job['events']],
                             ['CREATED', 'STARTED', 'RESULT'])
            self.assertEqual(job['source_state'], 'MATCHES_ADMISSION')
            self.assertEqual(job['verification'], 'recorded-not-reverified')
        factory_job = next(x for x in view['jobs'] if x['realization'] == 'simulated')
        self.assertTrue(factory_job['evidence'])
        self.assertTrue(all(e['kind'] == 'simulation' and e['depth'] == 'simulated'
                            for e in factory_job['evidence']))
        self.assertEqual(factory_job['result']['part_state'], 'machined')
        self.assertNotIn('physical', factory_job['source_state'].lower())

    def test_repeat_does_not_reexecute_or_append_any_events(self):
        first = populate(self.root, execute=True)
        original = (self.root / 'runtime.jsonl').read_bytes()
        ws_orig = (self.root / 'workspace.jsonl').read_bytes()
        factory_orig = (self.root / 'factory_orders.jsonl').read_bytes()
        second = populate(self.root, execute=True)
        self.assertEqual(first, second)
        self.assertEqual(original, (self.root / 'runtime.jsonl').read_bytes())
        self.assertEqual(ws_orig, (self.root / 'workspace.jsonl').read_bytes())
        self.assertEqual(factory_orig, (self.root / 'factory_orders.jsonl').read_bytes())

    def test_changed_factory_edition_invalidates_reverify(self):
        populate(self.root, execute=True)
        p = self.root / 'workstation' / WORKER_ID / 'machine-001' / 'factory_machine_worker.py'
        p.write_text(p.read_text() + '\n# changed\n')
        runtime = self.runtime()
        bridge = FactoryMachineSimulationBridge(runtime=runtime,
                                                  workstation=ProcessWorkstation(self.root / 'workstation'))
        with self.assertRaisesRegex(ValueError, 'source changed'):
            bridge.reverify(f'factory-{ORDER_ID}-02-machine')
        view = workstation_snapshot(root=self.root / 'workstation', runtime=runtime)
        machine = next(x for x in view['jobs'] if x['worker_id'] == WORKER_ID)
        self.assertEqual(machine['source_state'], 'SOURCE_CHANGED')

    def test_fabricated_factory_output_fails_native_verifier(self):
        populate(self.root, execute=True)
        runtime = self.runtime()
        bridge = FactoryMachineSimulationBridge(runtime=runtime,
                                                 workstation=ProcessWorkstation(self.root / 'workstation'))
        job = f'factory-{ORDER_ID}-02-machine'
        handoff = runtime.get(job)
        with self.assertRaisesRegex(ValueError, 'differs from native simulator'):
            runtime.return_result(job, actor_id='machine-sim',
                                  result=ExecutionResult(status='COMPLETE',
                                       output={'part': 'wrong', 'quantity': 3, 'part_state': 'machined'},
                                       evidence=runtime.state(job).evidence))

    def test_worker_source_is_not_implicitly_modified_or_reused_for_factory(self):
        populate(self.root, execute=True)
        desk = ProcessWorkstation(self.root / 'workstation')
        fcp = desk.inspect(worker_id='finite-correspondence-process', version_id='baseline-001')
        machine = desk.inspect(worker_id=WORKER_ID, version_id='machine-001')
        self.assertFalse(fcp['modified'] or machine['modified'])
        self.assertNotEqual(fcp['current_fingerprint'], machine['current_fingerprint'])
        self.assertEqual(self.runtime().state(FCP_JOB).status, 'COMPLETE')


if __name__ == '__main__':
    unittest.main()
