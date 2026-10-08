from __future__ import annotations

import unittest

from runtime.ab_information import (
    ABOccurrence,
    apply_synthesized,
    information_closure,
    synthesize_continuation_relation,
)


class ABInformationTests(unittest.TestCase):
    def test_minimizes_distinction_not_relation_count(self):
        group = (
            ABOccurrence.create(
                referent="dc22-like",
                relations={"A2": 0, "O1": 0, "O2": "left"},
                continuation="X",
            ),
            ABOccurrence.create(
                referent="dc22-like",
                relations={"A2": 1, "O1": 1, "O2": "left"},
                continuation="X",
            ),
            ABOccurrence.create(
                referent="dc22-like",
                relations={"A2": 2, "O1": 2, "O2": "right"},
                continuation="Y",
            ),
            ABOccurrence.create(
                referent="dc22-like",
                relations={"A2": 3, "O1": 3, "O2": "right"},
                continuation="Y",
            ),
        )

        state = information_closure(group)

        self.assertEqual(
            state.continuation_partition,
            ((0, 1), (2, 3)),
        )
        self.assertEqual(len(state.proofs), 1)
        self.assertEqual(
            state.proofs[0].partition,
            ((0, 1), (2, 3)),
        )
        self.assertEqual(
            state.proofs[0].sources,
            (("O2",),),
        )

    def test_preserves_all_equally_minimal_source_aliases(self):
        group = (
            ABOccurrence.create(
                referent="alias-family",
                relations={"R1": 0, "R2": "a", "fine": 10},
                continuation="X",
            ),
            ABOccurrence.create(
                referent="alias-family",
                relations={"R1": 0, "R2": "a", "fine": 11},
                continuation="X",
            ),
            ABOccurrence.create(
                referent="alias-family",
                relations={"R1": 1, "R2": "b", "fine": 12},
                continuation="Y",
            ),
            ABOccurrence.create(
                referent="alias-family",
                relations={"R1": 1, "R2": "b", "fine": 13},
                continuation="Y",
            ),
        )

        state = information_closure(group)

        self.assertEqual(len(state.proofs), 1)
        self.assertEqual(
            state.proofs[0].sources,
            (("R1",), ("R2",)),
        )

    def test_synthesizes_continuation_relation_when_old_vocabulary_is_too_fine(self):
        group = (
            ABOccurrence.create(
                referent="cd82-like",
                relations={"old_proof": "p0"},
                continuation="A",
            ),
            ABOccurrence.create(
                referent="cd82-like",
                relations={"old_proof": "p1"},
                continuation="A",
            ),
            ABOccurrence.create(
                referent="cd82-like",
                relations={"old_proof": "p2"},
                continuation="B",
            ),
            ABOccurrence.create(
                referent="cd82-like",
                relations={"old_proof": "p3"},
                continuation="B",
            ),
        )

        state = information_closure(group)
        relation = synthesize_continuation_relation(state)

        self.assertIsNotNone(relation)
        self.assertEqual(
            state.proofs[0].partition,
            ((0,), (1,), (2,), (3,)),
        )
        self.assertEqual(
            state.continuation_partition,
            ((0, 1), (2, 3)),
        )
        self.assertEqual(apply_synthesized(relation, 0), apply_synthesized(relation, 1))
        self.assertEqual(apply_synthesized(relation, 2), apply_synthesized(relation, 3))
        self.assertNotEqual(apply_synthesized(relation, 0), apply_synthesized(relation, 2))

    def test_raises_when_available_relations_cannot_restore_closure(self):
        group = (
            ABOccurrence.create(
                referent="insufficient",
                relations={"same": 1},
                continuation="A",
            ),
            ABOccurrence.create(
                referent="insufficient",
                relations={"same": 1},
                continuation="B",
            ),
        )

        with self.assertRaisesRegex(ValueError, "witness contract insufficient"):
            information_closure(group)


if __name__ == "__main__":
    unittest.main()
