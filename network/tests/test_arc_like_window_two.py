"""The two-predecessor schema expresses shear without declaring new equivalence."""
import unittest
from itertools import product

from work.arc_like_maze.window_two import (
    WindowProcess, compile_native, compile_shear, lift_native,
    all_state_fixed_B, certify_window_construction,
)
from work.arc_like_maze.root_transport import Process, ZERO, IDENTITY, NONLINEAR, find
from work.arc_like_maze.marked_operator_system import MarkedObject, MarkedArrow
from work.arc_like_maze.nondiagonal_transport import (
    ShearedMarkedWorld, ShearedMarkedArrow,
)


class WindowTwoTests(unittest.TestCase):
    def test_native_embedding_matches_full_transitions_on_varied_streams(self):
        processes = (
            Process.repeat(ZERO),
            Process.repeat(IDENTITY, NONLINEAR),
            Process((IDENTITY, ZERO), (NONLINEAR, ZERO, IDENTITY)),
        )
        for p in processes:
            for gain in (1, 2):
                obj = MarkedObject(p, gain)
                compiled = compile_native(obj)
                self.assertEqual(compiled.gain, gain)
                self.assertIsNotNone(compiled.native())
                for depth in range(3, 7):
                    for state in product(range(3), repeat=depth):
                        for action in ("A", "B"):
                            self.assertEqual(compiled.step(state, action),
                                             obj.world().step(state, action))

    def test_all_sheared_transition_laws_compile_exactly(self):
        processes = (
            Process.repeat(ZERO),
            Process.repeat(IDENTITY, NONLINEAR),
            Process((ZERO, IDENTITY), (NONLINEAR, ZERO)),
        )
        for process in processes:
            for gain in (1, 2):
                obj = MarkedObject(process, gain)
                for c in (0, 1, 2):
                    compiled = compile_shear(obj, c)
                    world = ShearedMarkedWorld(obj, c)
                    for depth in range(3, 7):
                        for state in product(range(3), repeat=depth):
                            for action in ("A", "B"):
                                self.assertEqual(compiled.step(state, action),
                                                 world.step(state, action))

    def test_inverse_is_exact_on_all_states(self):
        p = Process((IDENTITY,), (ZERO, NONLINEAR))
        for gain in (1, 2):
            obj = MarkedObject(p, gain)
            for c in (0, 1, 2):
                world = compile_shear(obj, c)
                for depth in range(3, 7):
                    for state in product(range(3), repeat=depth):
                        for action in ("A", "B"):
                            out = world.step(state, action)
                            self.assertEqual(world.inverse(out, action), state)
                            self.assertEqual(world.step(world.inverse(state, action),
                                                        action), state)

    def test_projection_commutes_with_all_depths(self):
        for c in (0, 1, 2):
            world = compile_shear(
                MarkedObject(Process.repeat(IDENTITY, NONLINEAR), 2), c)
            for depth in range(4, 8):
                for state in product(range(3), repeat=depth):
                    for action in ("A", "B"):
                        self.assertEqual(
                            world.step(state, action)[:-1],
                            world.step(state[:-1], action))

    def test_native_reverse_compilation_distinguishes_schema_from_alignment(self):
        obj = MarkedObject(Process.repeat(ZERO), 1)
        native = compile_shear(obj, 0)
        self.assertIsNotNone(native.native())
        for c in (1, 2):
            expanded = compile_shear(obj, c)
            self.assertIsNone(expanded.native())
            self.assertEqual(expanded.step((0, 0, 0), "B")[2], c)
            self.assertEqual(obj.world().step((0, 0, 0), "B")[2], 0)

    def test_eigen_invariant_fixed_B_counts_separate_independent_edit(self):
        source = compile_native(MarkedObject(Process.repeat(ZERO), 1))
        changed = source.edit(0, 2, 0, 1)
        self.assertEqual(all_state_fixed_B(source, 3), 9)
        self.assertEqual(all_state_fixed_B(changed, 3), 6)
        self.assertEqual(changed.step((2, 0, 0), "B"), (2, 0, 1))
        self.assertEqual(source.step((2, 0, 0), "B"), (2, 0, 0))
        # Fixed-point cardinality is preserved by ALL bijective
        # action-label conjugacies, not merely diagonal ones.
        for c in (0, 1, 2):
            sheared = compile_shear(MarkedObject(Process.repeat(ZERO), 1), c)
            self.assertEqual(all_state_fixed_B(sheared, 3), 9)

    def test_edit_at_periodic_index_preserves_every_other_rule_phase(self):
        obj = MarkedObject(Process.repeat(IDENTITY, NONLINEAR), 1)
        initial = compile_native(obj)
        modified = initial.edit(5, 2, 1, 2)
        self.assertEqual(modified.rule(5)[7],
                         (initial.rule(5)[7] + 2) % 3)
        for i in range(16):
            if i != 5:
                self.assertEqual(modified.rule(i), initial.rule(i))

    def test_witnessed_marked_arrow_transports_in_compiled_schema(self):
        source = Process.repeat(ZERO, (0, 0, 1))
        target = Process.repeat(ZERO, (0, 1, 0))
        arrow = MarkedArrow(MarkedObject(source, 1),
                            MarkedObject(target, 1), find(source, target))
        nonlinear = ShearedMarkedArrow(arrow, 1, 2)
        compiled_source = compile_shear(arrow.source, 1)
        compiled_target = compile_shear(arrow.target, 2)
        for depth in range(3, 8):
            for state in product(range(3), repeat=depth):
                mapped = nonlinear.map_state(state)
                for action in ("A", "B"):
                    self.assertEqual(
                        nonlinear.map_state(compiled_source.step(state, action)),
                        compiled_target.step(mapped, action))

    def test_window_coupling_can_depend_on_both_previous_coordinates(self):
        world = compile_native(MarkedObject(Process.repeat(ZERO), 1))
        other = world.edit(0, 2, 0, 1)
        # Unlike p0(x1), q0(x0,x1) detects x0 at fixed x1.
        self.assertEqual(world.rule(0)[0], other.rule(0)[0])
        self.assertNotEqual(other.rule(0)[0], other.rule(0)[6])
        self.assertIsNone(other.native())

    def test_arbitrary_two_input_rule_can_be_a_reversible_law(self):
        odd = tuple((2*left + right*right) % 3
                    for left in range(3) for right in range(3))
        world = WindowProcess(2, (odd,), (odd,))
        for depth in range(3, 7):
            for state in product(range(3), repeat=depth):
                for action in ("A", "B"):
                    self.assertEqual(world.inverse(world.step(state, action), action),
                                     state)

    def test_certificate_separates_closed_law_and_new_relation(self):
        result = certify_window_construction(depth=5)
        self.assertEqual(result.status,
                         "CLOSED_WINDOW_LAWS_WITH_DISTINCT_B_FIXED_INVARIANT")
        self.assertEqual((result.original_fixed, result.independent_fixed), (9, 6))
        self.assertEqual(result.compiled_same_steps, 2*3**5)
        self.assertEqual(result.checked_projection_edges, 2*3**5)

    def test_input_boundary_rejects_invalid_rules_and_states(self):
        with self.assertRaises(ValueError):
            WindowProcess(0, (), ((0,)*9,))
        with self.assertRaises(ValueError):
            WindowProcess(1, (), ())
        with self.assertRaises(ValueError):
            WindowProcess(1, (), ((0,)*8,))
        with self.assertRaises(ValueError):
            lift_native((1, 1, 2))
        with self.assertRaises(ValueError):
            compile_shear(MarkedObject(Process.repeat(ZERO), 1), 3)
        with self.assertRaises(ValueError):
            WindowProcess(1, (), ((0,)*9,)).step((0, 0, 0), "C")
        with self.assertRaises(ValueError):
            WindowProcess(1, (), ((0,)*9,)).edit(1, 3, 0, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
