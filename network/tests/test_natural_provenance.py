from __future__ import annotations

from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[2]


class NaturalProvenanceContractTests(unittest.TestCase):
    def test_cross_layer_link_schema_is_minimal_and_relational(self):
        schema = json.loads(
            (ROOT / "protocols" / "core" / "provenance-link.schema.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(schema["properties"]["schema_version"]["const"], 1)
        self.assertEqual(
            set(schema["required"]),
            {"schema_version", "provenance_id", "from", "relation", "to"},
        )
        self.assertIn("layer", schema["properties"]["from"]["required"])
        self.assertIn("ref", schema["properties"]["from"]["required"])
        self.assertIn("layer", schema["properties"]["to"]["required"])
        self.assertIn("ref", schema["properties"]["to"]["required"])

    def test_core_protocol_states_local_state_continuous_provenance(self):
        text = (
            ROOT / "protocols" / "core" / "provenance.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Local state, continuous provenance.", text)
        self.assertIn("Natural provenance", text)
        self.assertIn("State is not provenance", text)

    def test_visual_provenance_is_declared_as_specialization(self):
        text = (
            ROOT / "design" / "visual-provenance" / "README.md"
        ).read_text(encoding="utf-8")
        self.assertIn("specialization", text)
        self.assertIn("natural-provenance", text)

    def test_online_school_regrounds_without_erasing_prior_evidence(self):
        text = (
            ROOT / "companies" / "online-school" / "COMPANY.md"
        ).read_text(encoding="utf-8")
        self.assertIn("regrounds on what is actually evidenced now", text)
        self.assertIn("natural provenance", text)
        self.assertIn("Old state is not allowed to override stronger present evidence", text)


if __name__ == "__main__":
    unittest.main()
