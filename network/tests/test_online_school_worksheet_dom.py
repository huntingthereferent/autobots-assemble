"""Browser-DOM boundary for saved worksheet metadata, evaluated with the actual JS function."""
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]
JS = ROOT / "companies" / "online-school" / "app" / "worksheet.js"


class WorksheetLibraryDomTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "Node required for DOM boundary replay")
    def test_saved_titles_are_rendered_as_literal_text_not_html(self):
        js = r'''
const fs = require("node:fs");
const vm = require("node:vm");
const assert = require("node:assert/strict");
const source = fs.readFileSync(process.argv[1], "utf8");
const begin = source.indexOf("async function loadLibrary()");
const end = source.indexOf("function hydrate()", begin);
assert(begin >= 0 && end > begin);

class FakeElement {
  constructor(tag) { this.tag = tag; this.children = []; this.value = ""; }
  set textContent(v) { this.value = String(v); this.children = []; }
  get textContent() { return this.value + this.children.map(x => x.textContent).join(""); }
  set innerHTML(_) { throw new Error("Potential untrusted HTML insertion"); }
  append(...items) { this.children.push(...items); }
  replaceChildren(...items) { this.children = items; }
}
const title = '<img src=x onerror=alert(1)>';
const template = '<svg onload=alert(1)>';
const library = new FakeElement("div");
const document = { createElement: tag => new FakeElement(tag) };
const context = {
  library, document, worksheet: null,
  fetch: async () => ({
    ok: true,
    json: async () => ({worksheets: [{title, template, level: "3", items: [1,2]}]})
  }),
  hydrate: () => {}, renderAll: () => {}
};
vm.createContext(context);
vm.runInContext(source.slice(begin, end), context);
context.loadLibrary().then(() => {
  assert.equal(library.children.length, 1);
  const button = library.children[0];
  assert.equal(button.className, "library-item");
  assert.equal(button.type, "button");
  assert.equal(button.children[0].tag, "strong");
  assert.equal(button.children[0].textContent, title);
  assert.equal(button.children[1].textContent, template + " · 3 · 2 items");
}).catch(error => {console.error(error);process.exitCode=1});
'''
        result = subprocess.run(
            ["node", "-e", js, str(JS)],
            text=True, capture_output=True, timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
