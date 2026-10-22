"""Reading Room keeps original passage source, user text and optional evidence separate."""
from pathlib import Path
import subprocess
import shutil
import unittest

ROOT=Path(__file__).resolve().parents[2]/"companies/online-school/app"


class ReadingRoomTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"),"Node required")
    def test_original_passages_and_tokenization(self):
        script=r'''
const assert=require("node:assert/strict");
const read=require(process.argv[1]);
assert(read.PASSAGES.length>=3);
for(const story of read.PASSAGES){
 assert(story.id&&story.label&&story.title&&story.text&&story.question);
 assert(read.words(story.text).filter(x=>/\S/.test(x)).length>=15);
 assert(!story.text.includes("<script"));
 assert.equal(read.get(story.id).id,story.id);
}
assert.deepEqual(read.words("A cat!\nI see."),["A"," ","cat!","\n","I"," ","see."]);
assert.equal(read.cleanWord("“moon!”"),"moon");
assert.equal(read.speakable("yes\u0000\nno"),"yes no");
assert.equal(read.speakable("x".repeat(4200)).length,4000);
'''
        r=subprocess.run(["node","-e",script,str(ROOT/"reading-core.js")],capture_output=True,text=True,timeout=12)
        self.assertEqual(r.returncode,0,r.stderr)

    def test_user_content_is_inserted_as_text_and_save_is_explicit(self):
        script=(ROOT/"reading.js").read_text(encoding="utf-8")
        page=(ROOT/"reading.html").read_text(encoding="utf-8")
        self.assertIn("document.createTextNode(part)",script)
        self.assertIn("button.textContent=part",script)
        self.assertNotIn(".innerHTML",script)
        self.assertIn('fetch("/api/observations"',script)
        self.assertIn('learner_id:owner',script)
        self.assertIn('if(!note&&!reflection)',script)
        self.assertIn('aria-live="polite"',page)
        self.assertIn('src="./reading-core.js"',page)


if __name__=="__main__":
    unittest.main()
