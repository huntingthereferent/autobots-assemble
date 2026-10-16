import unittest
from systems.workspace.main_referent_selector import Capability, Witness, continue_referent


class ContinuationTests(unittest.TestCase):
    def test_local_pass_does_not_close_unobserved_boundary(self):
        result = continue_referent(('native_ci',), (), attempt=lambda c: None,
                                   observe=lambda c, x: None, local_passed=True)
        self.assertEqual((result.status, result.unresolved), ('OPEN', ('native_ci',)))
        self.assertTrue(result.local_pass_assumed)

    def test_picks_main_referent_not_unrelated_polish(self):
        calls = []
        choices = [Capability('local-polish', 'v1', ('better_readme',), True),
                   Capability('native-test', 'v1', ('native_ci',), True)]
        result = continue_referent(('native_ci',), choices,
            attempt=lambda c: calls.append(c.name) or 'real-run',
            observe=lambda c, output: Witness('SUPPORTED', c.edition, ('native_ci',), 'source://result', True))
        self.assertEqual(calls, ['native-test'])
        self.assertEqual(result.status, 'CROSSED')

    def test_cannot_run_unapproved_capability(self):
        calls = []
        result = continue_referent(('native_ci',), [Capability('ci', 'v1', ('native_ci',))],
            attempt=lambda c: calls.append(c.name), observe=lambda c, x: None)
        self.assertEqual(calls, [])
        self.assertEqual(result.status, 'OPEN')

    def test_real_failure_is_preserved_and_next_provider_attempted(self):
        calls = []
        def run(c):
            calls.append(c.name)
            if c.name == 'first':
                raise RuntimeError('native subprocess actually failed')
            return 'real-receipt'
        caps = [Capability('first', 'v1', ('boundary',), True), Capability('second', 'v1', ('boundary',), True)]
        result = continue_referent(('boundary',), caps, attempt=run,
            observe=lambda c, output: Witness('SUPPORTED', c.edition, ('boundary',), 'real://log', True),
            local_passed=True)
        self.assertEqual(calls, ['first', 'second'])
        self.assertEqual([m.observed for m in result.movements], ['ATTEMPT_ERROR', 'SUPPORTED'])
        self.assertEqual(result.status, 'CROSSED')

    def test_unverified_report_cannot_close(self):
        cap = Capability('ci', 'v1', ('native_ci',), True)
        result = continue_referent(('native_ci',), [cap], attempt=lambda c: 'pass',
            observe=lambda c, x: Witness('SUPPORTED', c.edition, ('native_ci',), 'fixture://log', False))
        self.assertEqual(result.status, 'OPEN')
        self.assertEqual(result.movements[0].observed, 'UNKNOWN')

    def test_missing_evidence_is_not_admitted(self):
        cap = Capability('ci', 'v1', ('native_ci',), True)
        result = continue_referent(('native_ci',), [cap], attempt=lambda c: 'pass',
            observe=lambda c, x: Witness('SUPPORTED', c.edition, ('native_ci',), '', True))
        self.assertEqual(result.status, 'OPEN')

    def test_observer_exception_preserved_not_a_pass(self):
        cap = Capability('ci', 'v1', ('native_ci',), True)
        result = continue_referent(('native_ci',), [cap], attempt=lambda c: 'pass',
            observe=lambda c, x: (_ for _ in ()).throw(OSError('log unreadable')))
        self.assertEqual(result.movements[0].observed, 'OBSERVATION_ERROR')
        self.assertEqual(result.status, 'OPEN')

    def test_source_edition_drift_rejected(self):
        cap = Capability('ci', 'v1', ('native_ci',), True)
        result = continue_referent(('native_ci',), [cap], attempt=lambda c: 'pass',
            observe=lambda c, x: Witness('SUPPORTED', 'v2', ('native_ci',), 'real://log', True))
        self.assertEqual(result.movements[0].observed, 'OBSERVATION_ERROR')
        self.assertEqual(result.status, 'OPEN')

    def test_can_continue_through_successive_boundaries(self):
        calls = []
        caps = [Capability('step-a', 'v1', ('a',), True), Capability('step-b', 'v1', ('b',), True)]
        result = continue_referent(('a', 'b'), caps, attempt=lambda c: calls.append(c.name) or c.name,
            observe=lambda c, x: Witness('SUPPORTED', c.edition, c.claims, 'real://' + c.name, True))
        self.assertEqual((calls, result.status), (['step-a', 'step-b'], 'CROSSED'))
        self.assertEqual(result.admitted, ('a', 'b'))

    def test_contradiction_leaves_boundary_open(self):
        cap = Capability('ci', 'v1', ('native_ci',), True)
        result = continue_referent(('native_ci',), [cap], attempt=lambda c: 'fail',
            observe=lambda c, x: Witness('CONTRADICTED', c.edition, (), 'real://fail', True))
        self.assertEqual((result.status, result.movements[0].observed), ('OPEN', 'CONTRADICTED'))

    def test_no_infinite_retry_on_same_edition(self):
        calls = []
        cap = Capability('ci', 'v1', ('native_ci',), True)
        result = continue_referent(('native_ci',), [cap], attempt=lambda c: calls.append(1) or None,
            observe=lambda c, x: Witness('UNKNOWN', c.edition, (), 'real://pending', True), max_attempts=10)
        self.assertEqual(len(calls), 1)
        self.assertEqual(result.status, 'OPEN')

    def test_attempt_bound_does_not_fake_completion(self):
        caps = [Capability('a', 'v1', ('a',), True), Capability('b', 'v1', ('b',), True)]
        result = continue_referent(('a','b'), caps, attempt=lambda c: None,
            observe=lambda c, x: Witness('SUPPORTED', c.edition, c.claims, 'real://ok', True), max_attempts=1)
        self.assertEqual(result.status, 'OPEN')
        self.assertEqual(len(result.movements), 1)

    def test_invalid_input_rejected(self):
        with self.assertRaises(ValueError):
            continue_referent(('a', 'a'), (), attempt=lambda c: None, observe=lambda c, x: None)
        with self.assertRaises(ValueError):
            continue_referent(('a',), (), attempt=lambda c: None, observe=lambda c, x: None, max_attempts=0)

    def test_out_of_scope_support_is_not_admitted(self):
        cap = Capability('ci', 'v1', ('ci',), True)
        result = continue_referent(('ci',), [cap], attempt=lambda c: None,
            observe=lambda c, x: Witness('SUPPORTED', c.edition, ('other',), 'real://ok', True))
        self.assertEqual(result.status, 'OPEN')
        self.assertEqual(result.movements[0].observed, 'OBSERVATION_ERROR')

if __name__ == '__main__':
    unittest.main()
