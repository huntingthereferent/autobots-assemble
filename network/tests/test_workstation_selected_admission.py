"""Evidence-pinned preferred edition can supply NEW bounded jobs, never auto-run."""
from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO

import json
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import unittest

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from runtime.examples.workstation_two_processes import populate, ORDER_ID
from systems.factory import FactorySystem, default_simulated_actors
from systems.workspace.workstation import ProcessWorkstation
from systems.workspace.controls import (
    admit_finite, admit_selected_finite, admit_selected_factory, prepare_preferred,
    promote_edition, run_job, main,
)
from systems.workspace.selected_admission import checked_selection
from systems.workspace.process_handoff import WORKER_ID as FINITE
from systems.workspace.factory_machine_bridge import (
    FactoryMachineSimulationBridge, WORKER_ID as FACTORY,
)
from systems.workspace.promotion import PreferredEditions

REPO = Path(__file__).resolve().parents[2]
INPUTS = {
    'old_phi': [0, 0, 1], 'new_phi': [0, 0, 0],
    'candidate_words': [['ABAA', 'ABBABA'], ['ABAA', 'AAABB', 'BAAAB']],
    'required_state': [0, 0, 0], 'required_action': 'B',
}


class PreferredJobAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.data = self.root / 'private'
        self.inputs_file = self.root / 'inputs.json'
        self.inputs_file.write_text(json.dumps(INPUTS))
        src = self.root / 'selected-source'
        src.mkdir()
        for name in ('finite_goal_priority.py', 'finite_required_edge_guard.py'):
            shutil.copyfile(REPO / 'work/arc_like_maze/chatbot' / name, src / name)
        self.desk = ProcessWorkstation(self.data / 'workstation')
        self.desk.copy_source(src, worker_id=FINITE, version_id='base')
        self.desk.branch(worker_id=FINITE, parent_version='base', version_id='fork')
        self.ledger = PreferredEditions(self.data / 'preferred_editions.jsonl')

    def runtime(self):
        return HandoffRuntime(event_store=RuntimeJournal(self.data / 'runtime.jsonl'))

    def promote(self, version='fork', job_id='support-a'):
        admit_finite(data_dir=self.data, version_id=version, inputs_file=self.inputs_file,
                     job_id=job_id, confirm_admit=job_id, from_actor='tester')
        run_job(data_dir=self.data, job_id=job_id, confirm_execute=job_id)
        fingerprint = self.desk.inspect(worker_id=FINITE, version_id=version)['current_fingerprint']
        return promote_edition(data_dir=self.data, worker_id=FINITE, version_id=version,
                               supporting_job_id=job_id, confirm_version=version,
                               confirm_fingerprint=fingerprint, actor_id='tester')

    def admit_selected(self, selection, job_id='future-a', confirm_selection=None):
        return admit_selected_finite(data_dir=self.data, inputs_file=self.inputs_file,
                                    job_id=job_id, confirm_admit=job_id,
                                    confirm_selection=confirm_selection or selection['event_id'],
                                    from_actor='tester', lane_id='finite-correspondence')

    def test_no_selected_edition_means_no_new_job(self):
        with self.assertRaisesRegex(ValueError, 'no preferred edition'):
            prepare_preferred(data_dir=self.data, worker_id=FINITE, inputs_file=self.inputs_file)
        self.assertFalse((self.data / 'runtime.jsonl').exists())

    def test_preparing_preferred_is_read_only(self):
        selection = self.promote()
        before = (self.data / 'runtime.jsonl').read_bytes()
        chosen = prepare_preferred(data_dir=self.data, worker_id=FINITE,
                                   inputs_file=self.inputs_file)
        self.assertEqual(chosen['selection_event_id'], selection['event_id'])
        self.assertEqual(chosen['version_id'], 'fork')
        self.assertTrue(chosen['supporting_job_reverified'])
        self.assertFalse(chosen['admitted'])
        self.assertFalse(chosen['executed'])
        self.assertEqual((self.data / 'runtime.jsonl').read_bytes(), before)

    def test_new_handoff_uses_selection_not_supporting_job_and_does_not_execute(self):
        selection = self.promote()
        before_events = len(self.runtime().event_store.all())
        row = self.admit_selected(selection)
        runtime = self.runtime()
        h = runtime.get('future-a')
        self.assertEqual(row['version_id'], 'fork')
        self.assertEqual(row['source_fingerprint'], selection['source_fingerprint'])
        self.assertEqual(row['status'], 'READY')
        self.assertFalse(row['executed'])
        self.assertEqual(h.metadata['preferred_selection_event'], selection['event_id'])
        self.assertIn('preferred-selection:' + selection['event_id'], h.provenance)
        self.assertEqual(h.metadata['edition_fingerprint'], selection['source_fingerprint'])
        self.assertNotEqual(h.handoff_id, selection['supporting_job_id'])
        self.assertEqual(len(runtime.event_store.all()), before_events + 1)
        self.assertEqual(runtime.state('support-a').status, 'COMPLETE')
        self.assertEqual(runtime.state('future-a').status, 'READY')
        result = run_job(data_dir=self.data, job_id='future-a', confirm_execute='future-a')
        self.assertTrue(result['reverified'])
        self.assertEqual(self.runtime().state('future-a').status, 'COMPLETE')

    def test_cli_preferred_admission_keeps_execution_separate(self):
        selected = self.promote()
        before = (self.data / 'runtime.jsonl').read_bytes()
        out = StringIO()
        with redirect_stdout(out):
            main(['--data-dir', str(self.data), 'prepare-preferred',
                  '--worker', FINITE, '--inputs-file', str(self.inputs_file)])
        self.assertEqual(json.loads(out.getvalue())['selection_event_id'], selected['event_id'])
        self.assertEqual((self.data / 'runtime.jsonl').read_bytes(), before)
        out = StringIO()
        with redirect_stdout(out):
            main(['--data-dir', str(self.data), 'admit-preferred-finite',
                  '--inputs-file', str(self.inputs_file), '--job-id', 'next-cli',
                  '--confirm-admit', 'next-cli', '--confirm-selection', selected['event_id'],
                  '--from-actor', 'tester'])
        self.assertEqual(json.loads(out.getvalue())['status'], 'READY')
        self.assertEqual(self.runtime().state('next-cli').status, 'READY')

    def test_selection_event_confirmation_blocks_stale_choice(self):
        old = self.promote()
        new = self.promote(version='base', job_id='support-b')
        self.assertNotEqual(old['event_id'], new['event_id'])
        before = (self.data / 'runtime.jsonl').read_bytes()
        with self.assertRaises(PermissionError):
            self.admit_selected(old)
        self.assertEqual((self.data / 'runtime.jsonl').read_bytes(), before)
        self.assertNotIn('future-a', self.runtime().snapshot())

    def test_changed_preferred_source_blocks_before_admission(self):
        selection = self.promote()
        target = self.data / 'workstation' / FINITE / 'fork' / 'finite_goal_priority.py'
        target.write_text(target.read_text() + '\n# local mutation\n')
        events_before = (self.data / 'runtime.jsonl').read_bytes()
        with self.assertRaisesRegex(ValueError, 'source changed'):
            self.admit_selected(selection)
        self.assertEqual((self.data / 'runtime.jsonl').read_bytes(), events_before)

    def test_missing_supporting_job_and_corrupt_ledger_fail_closed(self):
        selected = self.promote()
        path = self.data / 'runtime.jsonl'
        before = path.read_bytes()
        # A preference is not a substitute for native supporting history.
        selection_only = self.root / 'disconnected'
        (selection_only / 'workstation').mkdir(parents=True)
        with self.assertRaises((KeyError, ValueError)):
            checked_selection(data_dir=selection_only, worker_id=FINITE)
        ledger = self.data / 'preferred_editions.jsonl'
        ledger.write_text('{bad json\n')
        with self.assertRaises(ValueError):
            self.admit_selected(selected)
        self.assertEqual(path.read_bytes(), before)

    def test_confirmation_and_duplicate_job_guards(self):
        selected = self.promote()
        with self.assertRaises(PermissionError):
            admit_selected_finite(data_dir=self.data, inputs_file=self.inputs_file,
                job_id='future-a', confirm_admit='wrong', confirm_selection=selected['event_id'],
                from_actor='tester')
        self.admit_selected(selected)
        with self.assertRaises(ValueError):
            self.admit_selected(selected)

    def test_past_admitted_job_stays_pinned_after_selection_changes(self):
        old = self.promote()
        self.admit_selected(old)
        new = self.promote(version='base', job_id='support-b')
        self.assertNotEqual(new['event_id'], old['event_id'])
        self.assertEqual(self.runtime().get('future-a').metadata['worker_version'], 'fork')
        self.assertEqual(self.runtime().get('future-a').metadata['preferred_selection_event'], old['event_id'])
        self.assertTrue(run_job(data_dir=self.data, job_id='future-a',
                                confirm_execute='future-a')['reverified'])


class PreferredFactoryAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.data = Path(self.tmp.name) / 'state'
        populate(self.data, execute=True)
        self.desk = ProcessWorkstation(self.data / 'workstation')
        machine = self.desk.inspect(worker_id=FACTORY, version_id='machine-001')
        self.selected = promote_edition(data_dir=self.data, worker_id=FACTORY,
             version_id='machine-001', supporting_job_id=f'factory-{ORDER_ID}-02-machine',
             confirm_version='machine-001', confirm_fingerprint=machine['current_fingerprint'],
             actor_id='tester')

    def next_machine(self, order_id='NEW-DEMO-2'):
        fac = FactorySystem(self.data / 'factory_orders.jsonl')
        fac.create_order(order_id=order_id, product='demo-part', quantity=2,
                         material='demo-stock')
        runtime = HandoffRuntime(event_store=RuntimeJournal(self.data / 'runtime.jsonl'))
        bridge = FactoryMachineSimulationBridge(runtime=runtime, workstation=self.desk)
        supply = fac.next_handoff(order_id)
        runtime.submit(bridge.native.admit(supply))
        runtime.run(supply.handoff_id, default_simulated_actors()[supply.to_actor])
        fac.reconcile(order_id, handoff=supply, state=runtime.state(supply.handoff_id))
        machine = fac.next_handoff(order_id)
        return machine

    def test_preferred_factory_requires_actual_pending_machine_stage(self):
        with self.assertRaises(KeyError):
            admit_selected_factory(data_dir=self.data, order_id='nonexistent',
                 confirm_handoff='made-up', confirm_selection=self.selected['event_id'])
        pending = self.next_machine()
        with self.assertRaises(PermissionError):
            admit_selected_factory(data_dir=self.data, order_id='NEW-DEMO-2',
                 confirm_handoff='wrong', confirm_selection=self.selected['event_id'])
        result = admit_selected_factory(data_dir=self.data, order_id='NEW-DEMO-2',
                 confirm_handoff=pending.handoff_id, confirm_selection=self.selected['event_id'])
        self.assertEqual(result['status'], 'READY')
        self.assertFalse(result['executed'])
        h = HandoffRuntime(event_store=RuntimeJournal(self.data/'runtime.jsonl')).get(pending.handoff_id)
        self.assertEqual(h.metadata['preferred_selection_event'],self.selected['event_id'])
        self.assertIn('preferred-selection:'+self.selected['event_id'],h.provenance)
        out = run_job(data_dir=self.data, job_id=pending.handoff_id,
                      confirm_execute=pending.handoff_id)
        self.assertTrue(out['reverified'])
        self.assertEqual(FactorySystem(self.data/'factory_orders.jsonl').order('NEW-DEMO-2').stage_index, 2)

    def test_factory_changed_source_blocks_admission(self):
        pending = self.next_machine()
        file = self.data/'workstation'/FACTORY/'machine-001'/'factory_machine_worker.py'
        file.write_text(file.read_text() + '\n# edited\n')
        with self.assertRaisesRegex(ValueError, 'source changed'):
            admit_selected_factory(data_dir=self.data, order_id='NEW-DEMO-2',
                confirm_handoff=pending.handoff_id, confirm_selection=self.selected['event_id'])
        runtime = HandoffRuntime(event_store=RuntimeJournal(self.data/'runtime.jsonl'))
        self.assertNotIn(pending.handoff_id, runtime.snapshot())


if __name__ == '__main__':
    unittest.main()
