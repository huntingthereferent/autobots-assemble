"""Native fixture and negative-boundary checks for trial 01."""
import tempfile
import unittest
from pathlib import Path
from tracework_imports import inspect


class Trial01Tests(unittest.TestCase):
    def test_fixture(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "main.js").write_text('import { answer } from "./lib.js";\n')
            (root / "lib.js").write_text("export const answer = 42;\n")
            (root / "unused.js").write_text("export const unused = true;\n")
            result = inspect(root)
            self.assertEqual(result["modules"], ["lib.js", "main.js", "unused.js"])
            self.assertEqual(result["edges"], [
                {"from": "main.js", "to": "lib.js", "specifier": "./lib.js"}
            ])

    def test_outside_root_not_admitted(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "app"
            root.mkdir()
            (root / "main.js").write_text('import "../secret.js";\n')
            self.assertEqual(inspect(root)["edges"], [])

    def test_no_phantom_edge(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "a.js").write_text('export const x = "import from ./b.js";\n')
            (root / "b.js").write_text("export const b = 1;\n")
            self.assertEqual(inspect(root)["edges"], [])


if __name__ == "__main__":
    unittest.main()
