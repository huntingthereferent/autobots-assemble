"""Static repository contracts; these do not simulate assistant compliance."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


class SessionContinuityTests(unittest.TestCase):
    def read(self, path):
        return (ROOT / path).read_text(encoding="utf-8")

    def test_github_entry_reaches_standing_session_rules(self):
        self.assertIn("[ENTRY.md](ENTRY.md)", self.read("README.md"))
        entry = self.read("ENTRY.md")
        index = json.loads(self.read("protocols/index.json"))["protocols"]
        session_path = index["ai.session"]["path"]
        self.assertIn(f"[ai.session]({session_path})", entry)
        self.assertLess(entry.index(f"({session_path})"),
                        entry.index("## Entry sequence"))
        self.assertIn("Load it once per session", entry)
        self.assertTrue((ROOT / session_path).is_file())

    def test_current_referent_and_protocol_remain_resolvable(self):
        state = json.loads(self.read("state/current.json"))
        for field in ("preferred_referent", "goal", "next_movement"):
            self.assertTrue(state[field], field)
        index = json.loads(self.read("protocols/index.json"))["protocols"]
        self.assertIn(state["protocol"], index)
        self.assertTrue((ROOT / index[state["protocol"]]["path"]).is_file())
        self.assertIn("If the user gives a new explicit referent, that becomes primary",
                      self.read("ENTRY.md"))

    def test_recorded_continuity_clauses_are_preserved(self):
        # Deliberate text contracts: wording changes require reviewing these
        # assertions. Presence cannot establish runtime or model compliance.
        session = self.read("protocols/ai/session.md")
        clauses = {
            "workflow preference": "James's project/research work stays GitHub-centered.",
            "explicit override": "A current explicit request may override this preference.",
            "speaker independent of surface": "The application surface is not evidence of who is speaking.",
            "existing authority": "Preserve established speaker context and authorization",
            "mismatch disclosure": "state the mismatch once, plainly and early",
            "no silent transfer": "Do not silently redirect work to another mode, workspace, or project.",
            "mode boundary": "This protocol cannot enforce application routing.",
            "confirmed capability": "Never claim to switch the application mode without a capability and a confirmed result.",
            "same project": "A different code location does not establish a different project.",
            "parent correction": "revisit the parent referent before continuing the implementation detail",
            "correction survives": "Preserve the user's correction in the next movement.",
            "handoff continuity": "preserve the goal, repository, established authorization, findings and next movement",
            "continue work": "Continue useful authorized work in the current session",
        }
        for rule, clause in clauses.items():
            with self.subTest(rule=rule):
                self.assertIn(clause, session)
        index = json.loads(self.read("protocols/index.json"))["protocols"]
        self.assertIn("ai.james", session)
        self.assertTrue((ROOT / index["ai.james"]["path"]).is_file())

    def test_language_first_and_scalpel_precision_survive_entry(self):
        # Static source contract only: wording does not prove model behavior.
        entry = self.read("ENTRY.md")
        session = self.read("protocols/ai/session.md")
        self.assertIn("including language-first precision, drift control", entry)
        self.assertIn("At every reached layer, decompress the referent", entry)
        self.assertIn("Mathematics remains a human formal language.", entry)
        clauses = {
            "thought boundary": "This does **not** claim that language precedes thought.",
            "math is language": "**Mathematics is a human formal language.**",
            "scope of language first": "before choosing or expanding a formal representation",
            "every boundary": "at every layer and again at every boundary",
            "not one-way": 'Do not impose a one-way "language then mathematics" ontology.',
            "scoped mathematics": "objects, domains, operations,",
            "no grand declaration": "grand declarations",
            "witness categories": "physically",
            "no A/B recasting": "neither this session protocol nor Continuity software redefines it",
            "drift audit": "## Drift check before movement",
            "no invented external goal": "Have I added an unrequested destination",
            "human burden": "Do not place the repeated burden of",
            "correction constrains behavior": "as a constraint on subsequent behavior",
        }
        for rule, wording in clauses.items():
            with self.subTest(rule=rule):
                self.assertIn(wording, session)
        self.assertIn("Static repository contracts", self.read(
            "network/tests/test_session_continuity.py"))

    def test_ci_reports_focused_check_before_broad_suite(self):
        workflow = self.read(".github/workflows/tests.yml")
        focused = 'python -m unittest discover -s network/tests -p "test_session_continuity.py" -v'
        broad = 'python -m unittest discover -s network/tests -p "test_*.py"'
        self.assertLess(workflow.index(focused), workflow.index(broad))
        self.assertIn("pull_request:", workflow)
        self.assertIn("push:", workflow)


if __name__ == "__main__":
    unittest.main()
