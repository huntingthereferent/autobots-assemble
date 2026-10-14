"""Read-only entry verification for the two-coupling mathematical certificate.

Referent: repository entry -> declared origin-rooted class rotation.
Evidence: README.md, ENTRY.md, project README and coupling_family.py.
Witness: resolved links, bounded claims, every rooted edge, exact permutation order.
Movement: verification only; no source-world, routing-state or ARC mutation.
Boundary: documentation presence cannot enforce assistant compliance; no live ARC
execution or universal/full-state closure is inferred.
Next: keep this entry check alongside the focused coupling-family suite.
"""
from pathlib import Path
import re
import unittest

from work.arc_like_maze.alignment import discover_alignment
from work.arc_like_maze.coupling_family import rotate_within_class

ROOT = Path(__file__).resolve().parents[2]


class CouplingEntryTests(unittest.TestCase):
    def read(self, path):
        return (ROOT / path).read_text(encoding="utf-8")

    def test_readme_entry_and_project_links_resolve(self):
        readme = self.read("README.md")
        for path in ("ENTRY.md", "work/arc_like_maze/README.md"):
            self.assertRegex(readme, re.escape(f"]({path})"))
            self.assertTrue((ROOT / path).is_file())
        project = self.read("work/arc_like_maze/README.md")
        self.assertIn("](coupling_family.py)", project)
        self.assertTrue((ROOT / "work/arc_like_maze/coupling_family.py").is_file())
        self.assertIn("network.tests.test_arc_like_coupling_family", project)
        entry = self.read("ENTRY.md")
        self.assertIn("If the user gives a new explicit referent, that becomes primary", entry)
        for field in ("current referent", "goal / definition of solved",
                      "evidence actually used", "witness conditions checked",
                      "movement made", "wall / unknown / partial state",
                      "artifacts or changes produced", "next referent / next movement"):
            self.assertIn(field, entry)

    def test_entry_claims_keep_rooted_and_execution_boundaries(self):
        project_text = self.read("work/arc_like_maze/README.md")
        section = project_text.split(
            "### Rooted A/B classifications: 81 constructions, 21 classes", 1
        )[1].split("## Third independent coupling", 1)[0]
        section = " ".join(section.split())
        for claim in ("**81** parameter worlds", "**21** equivalence classes",
                      "origin-reachable", "36 turns", "chosen construction rule",
                      "not a claim that all pairs are conjugate",
                      "not an assertion that every world individually has 36 distinct forms"):
            self.assertIn(claim, section)
        project = " ".join(project_text.split())
        for boundary in ("origin-reachable", "chosen construction rule",
                         "not an assertion that every world individually has 36 distinct forms"):
            self.assertIn(boundary, project)

    def test_reachable_certificate_checks_every_edge_and_exact_order(self):
        successors = rotate_within_class()
        self.assertEqual(len(successors), 81)
        self.assertEqual(set(successors), set(successors.values()))
        lengths = []
        unseen = set(successors)
        while unseen:
            start = next(iter(unseen))
            world = start
            length = 0
            while True:
                self.assertIn(world, unseen)
                unseen.remove(world)
                target = successors[world]
                witness = discover_alignment(world, target)
                self.assertTrue(witness.aligned)
                self.assertIn((world.origin, target.origin), witness.pairs)
                world = target
                length += 1
                if world == start:
                    break
            lengths.append(length)
        self.assertEqual(sorted(lengths), [2] * 4 + [4] * 16 + [9])
        # Directly reject every earlier simultaneous return, rather than only
        # trusting a certificate's reported least common multiple.
        for turns in range(1, 37):
            returned = True
            for start in successors:
                world = start
                for _ in range(turns):
                    world = successors[world]
                returned = returned and world == start
            self.assertEqual(returned, turns == 36)


if __name__ == "__main__":
    unittest.main()
