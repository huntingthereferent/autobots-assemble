"""Science Notebook admits actual learner observations, not prediction-only claims."""
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT=Path(__file__).resolve().parents[2]/"companies/online-school/app"


class ScienceNotebookTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"),"Node required")
    def test_templates_and_actual_observation_boundary(self):
        js=r'''
const assert=require("node:assert/strict");
const x=require(process.argv[1]);
assert(x.CHALLENGES.length>=3);
for(const c of x.CHALLENGES){
 assert(x.choose(c.id).id===c.id);
 assert(c.title&&c.question&&c.materials&&c.method);
}
assert.throws(()=>x.buildObservation({learner:"a",question:"Why?",method:"I tried"}),/actually observed/);
assert.throws(()=>x.buildObservation({question:"Why?",method:"I tried",observed:"It changed"}),/learner/);
const saved=x.buildObservation({
 learner:"learner_123",question:"What changes?",prediction:"Maybe nothing",
 method:"I compared two shapes",observed:"The folded one held a light eraser.",
 next:"Try a wider fold"
});
assert.equal(saved.learner_id,"learner_123");
assert(saved.observed.includes("Method tried:"));
assert(saved.observed.includes("Observation:"));
assert(saved.observed.includes("Prediction:"));
assert(saved.observed.includes("Next step:"));
assert.equal(saved.provenance[0],"online-school:science-notebook:v1");
assert.deepEqual(saved.supports,[]);
'''
        constr = subprocess.run(["node", "-e", js, str(ROOT/"science-core.js")],
                                text=True, capture_output=True, timeout=12)
        self.assertEqual(constr.returncode, 0, constr.stderr)

    def test_explicit_save_uses_existing_api(self):
        src=(ROOT/"science.js").read_text()
        html=(ROOT/"science.html").read_text()
        self.assertIn('fetch("/api/observations"',src)
        self.assertIn("core.buildObservation",src)
        self.assertIn("not mean you performed it",html)
        self.assertNotIn("innerHTML",src)


if __name__=="__main__":
    unittest.main()
