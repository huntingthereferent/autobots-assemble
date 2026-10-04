from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[2]


class ProtocolRegistryTests(unittest.TestCase):
    def test_osint_is_absorbed_into_source_research(self):
        index = json.loads((ROOT / "protocols" / "index.json").read_text(encoding="utf-8"))
        protocols = index["protocols"]
        self.assertNotIn("work.osint", protocols)
        self.assertIn("research.source", protocols)
        self.assertEqual(protocols["research.source"]["path"], "protocols/research/source.md")

    def test_osint_compatibility_document_remains(self):
        text = (ROOT / "protocols" / "work" / "osint.md").read_text(encoding="utf-8")
        self.assertIn("research.source", text)
        self.assertIn("Compatibility", text)


if __name__ == "__main__":
    unittest.main()
