"""Family board date selection and counts preserve source/task identity."""
from pathlib import Path
import subprocess
import shutil
import unittest

ROOT=Path(__file__).resolve().parents[2]/"companies/online-school/app"


class FamilyBoardTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"),"Node needed")
    def test_seven_day_math_and_shared_task_filtering(self):
        js=r'''
const assert=require("node:assert/strict");
const family=require(process.argv[1]);
assert.deepEqual(family.week("2026-10-22"),[
"2026-10-19","2026-10-20","2026-10-21","2026-10-22",
"2026-10-23","2026-10-24","2026-10-25"]);
assert.equal(family.monday("2026-10-25"),"2026-10-19");
assert.equal(family.monday("2026-01-01"),"2025-12-29");
assert.throws(()=>family.week("2026-02-30"),/Invalid/);
const tasks=[
 {id:"a",learner_ids:["rose"],scope:"individual",planned_minutes:45,status:"done"},
 {id:"b",learner_ids:["myla"],scope:"individual",planned_minutes:30,status:"todo"},
 {id:"c",learner_ids:[],scope:"shared",planned_minutes:25,status:"done"},
 {id:"c",learner_ids:[],scope:"shared",planned_minutes:25,status:"done"}
];
assert.deepEqual((({total,done,remaining,plannedMinutes})=>({total,done,remaining,plannedMinutes}))(family.metrics(tasks,"rose")),
 {total:2,done:2,remaining:0,plannedMinutes:70});
assert.deepEqual((({total,done,remaining,plannedMinutes})=>({total,done,remaining,plannedMinutes}))(family.metrics(tasks,"myla")),
 {total:2,done:1,remaining:1,plannedMinutes:55});
assert.deepEqual((({total,done,remaining,plannedMinutes})=>({total,done,remaining,plannedMinutes}))(family.metrics(tasks,"all")),
 {total:3,done:2,remaining:1,plannedMinutes:100});
'''
        r=subprocess.run(["node","-e",js,str(ROOT/"family-core.js")],capture_output=True,text=True,timeout=12)
        self.assertEqual(r.returncode,0,r.stderr)

    def test_persisted_task_and_planned_time_boundaries(self):
        page=(ROOT/"family.html").read_text()
        js=(ROOT/"family.js").read_text()
        self.assertIn('src="./family-core.js"',page)
        self.assertIn('json("/api/tasks")',js)
        self.assertIn('method:"PATCH"',js)
        self.assertIn('method:"POST"',js)
        self.assertIn("not verified instruction hours",page.lower())


if __name__=="__main__":
    unittest.main()
