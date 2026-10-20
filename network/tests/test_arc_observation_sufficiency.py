"""Offline exhaustive finite checks for the A/B observation-quotient lemma."""
import unittest

from research.arc_native_runs.observation_sufficiency import (
    ExampleState,
    example_actions,
    example_states,
    finite_observation_quotient,
    visible_feedback,
)


class ObservationSufficiencyTests(unittest.TestCase):
    def setUp(self):
        self.states = example_states()
        self.actions = example_actions()

    def test_reachable_closed_domain_has_six_states(self):
        self.assertEqual(len(self.states), 6)
        self.assertEqual(set(self.actions), {"A", "B"})
        self.assertTrue(all(f(s) in self.states for f in self.actions.values() for s in self.states))

    def test_same_visible_frame_can_hide_distinct_next_outcomes(self):
        initial = ExampleState(0, 0, 0)
        prepared = self.actions["B"](initial)
        self.assertEqual(visible_feedback(initial), visible_feedback(prepared))
        self.assertNotEqual(
            visible_feedback(self.actions["B"](initial)),
            visible_feedback(self.actions["B"](prepared)),
        )

    def test_exact_refuting_witness_for_observation_only_AB(self):
        result = finite_observation_quotient(self.states, visible_feedback, self.actions)
        self.assertFalse(result["sufficient"])
        self.assertEqual(result["witness"]["action"], "B")
        self.assertEqual(result["witness"]["same_observation"], (0, 0))
        self.assertNotEqual(
            result["witness"]["first_successor_observation"],
            result["witness"]["second_successor_observation"],
        )

    def test_full_state_abstraction_satisfies_both_actions(self):
        result = finite_observation_quotient(self.states, lambda state: state, self.actions)
        self.assertTrue(result["sufficient"])
        self.assertEqual(result["observed_state_count"], len(self.states))
        for state in self.states:
            for label, action in self.actions.items():
                self.assertEqual(result["quotient_transitions"][(state, label)], action(state))

    def test_coarser_memory_with_history_and_win_but_no_position_works(self):
        result = finite_observation_quotient(
            self.states, lambda state: (state.interacted, state.win), self.actions
        )
        self.assertTrue(result["sufficient"])
        self.assertEqual(result["observed_state_count"], 3)

    def test_refuses_unsupported_or_incomplete_action_families(self):
        with self.assertRaisesRegex(ValueError, "exactly A and B"):
            finite_observation_quotient(self.states, visible_feedback, {"A": self.actions["A"]})
        with self.assertRaisesRegex(ValueError, "leaves declared state domain"):
            finite_observation_quotient(
                self.states, visible_feedback,
                {"A": self.actions["A"], "B": lambda state: ExampleState(7, 7, 7)},
            )


if __name__ == "__main__":
    unittest.main()
