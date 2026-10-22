"""Practice Lab produces checkable activities, never invented learning records."""
from pathlib import Path
import subprocess
import shutil
import unittest

ROOT = Path(__file__).resolve().parents[2] / "companies/online-school/app"


class PracticeLabTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "Node required for learner practice core")
    def test_math_phonics_and_answers(self):
        js = r'''
const assert=require("node:assert/strict");
const core=require(process.argv[1]);
let calls=0;
const fixed=()=>[.3,.1,.9,.2][(calls++)%4];
const starter=core.newProblem("numbers","starter",fixed);
assert.equal(starter.track,"numbers");
assert(starter.detail.includes("="));
assert(core.correct(starter,starter.answer));
assert(!core.correct(starter,"definitely wrong"));
for(const level of ["starter","builder","explorer"]){
 for(let i=0;i<75;i++){
  const p=core.newProblem("numbers",level);
  assert(/^[0-9]+ [×−+] [0-9]+ = \?$/.test(p.detail));
  assert(Number(p.answer)>=0);
 }
}
for(let i=0;i<30;i++){
 const p=core.newProblem("words","starter");
 assert.equal(p.track,"words");
 assert(core.correct(p,p.answer.toUpperCase()+" "));
 assert(!core.correct(p,p.answer+"z"));
 assert(p.hint.length>5);
}
assert.deepEqual(core.summary(3,7),{attempts:3,firstTry:3});
assert.deepEqual(core.summary(-1,-3),{attempts:0,firstTry:0});
'''
        r = subprocess.run(
            ["node", "-e", js, str(ROOT / "practice-core.js")],
            text=True, capture_output=True, timeout=12,
        )
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_page_owns_real_save_boundary(self):
        html = (ROOT / "practice.html").read_text()
        js = (ROOT / "practice.js").read_text()
        self.assertIn('src="./practice-core.js"', html)
        self.assertIn('src="./practice.js"', html)
        self.assertIn('fetch("/api/observations"', js)
        self.assertIn("learner_id:owner", js)
        self.assertIn("provenance:[", js)
        self.assertIn("does not", html.lower())


if __name__ == "__main__":
    unittest.main()
