"""The public school starts with play and actually retains creative work."""
from pathlib import Path
import re
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]
LIVE = ROOT / "docs" / "live"


class SchoolPlaySpaceTests(unittest.TestCase):
    def test_play_first_navigation_and_real_destinations(self):
        html = (LIVE / "school.html").read_text(encoding="utf-8")
        js = (LIVE / "school.js").read_text(encoding="utf-8")
        for marker in (
            'id="panel-play"', 'id="panel-create"', 'id="panel-pattern"',
            'data-page="play" aria-current="page"', 'id="creation-form"',
            'id="pattern-beats"', 'href="pony-trail.html"',
            'href="cat-keyboard.html"', 'href="work.html"',
            'id="creation-library"', 'id="play-creations"',
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, html)
        for marker in ('saveCreation(', 'renderCreations(', 'playPattern(',
                       'creations:safeArray(data.creations)', 'practiceSolved'):
            self.assertIn(marker, js)
        self.assertNotIn('fetch(', js)
        self.assertTrue((LIVE / "pony-trail.html").is_file())
        self.assertTrue((LIVE / "cat-keyboard.html").is_file())
        defined = set(re.findall(r'\bid="([^"]+)"', html))
        referenced = set(re.findall(r'\$\("([^"]+)"\)', js))
        self.assertFalse(referenced - defined, "JS refers to missing HTML IDs: " + repr(referenced - defined))

    @unittest.skipUnless(shutil.which("node"), "Node needed for browser-script smoke tests")
    def test_bare_dom_exercises_creation_pattern_and_learning_saves(self):
        harness = r"""
const fs=require("fs"),assert=require("node:assert/strict"),path=require("path");
const html=fs.readFileSync(path.join(process.cwd(),"docs/live/school.html"),"utf8");
const source=fs.readFileSync(path.join(process.cwd(),"docs/live/school.js"),"utf8");
class E {
 constructor(id){
  this.id=id;this.children=[];this.listeners={};this.value="";this.dataset={};
  this.style={};this.attributes={};this.className="";this.textContent="";
  this.disabled=false;this.hidden=false;this.classList={
   toggle:(name,on)=>{const a=this.className.split(" ").filter(Boolean);
    const wanted=on===undefined?!a.includes(name):on;
    this.className=[...a.filter(x=>x!==name),...(wanted?[name]:[])].join(" ")},
   remove:name=>{this.className=this.className.split(" ").filter(x=>x!==name).join(" ")}
  };
 }
 addEventListener(event,fn){(this.listeners[event]??=[]).push(fn)}
 async fire(event){for(const fn of this.listeners[event]||[])await fn({preventDefault(){},target:this})}
 append(...items){this.children.push(...items)}
 replaceChildren(...items){this.children=items}
 setAttribute(k,v){this.attributes[k]=v}
 removeAttribute(k){delete this.attributes[k]}
 add(x){this.children.push(x)}
 reset(){this.value=""}
 focus(){}
 querySelectorAll(q){return q===".pattern-beat"?this.children.filter(x=>x.className.includes("pattern-beat")):[]}
}
const ids=[...html.matchAll(/\bid="([^"]+)"/g)].map(x=>x[1]);
const els=Object.fromEntries(ids.map(id=>[id,new E(id)]));
for(const [id,v] of Object.entries({
 "practice-mode":"numbers","practice-level":"starter","passage":"seed",
 "text-size":"1","investigation":"shadow","creation-kind":"story","task-subject":"Math"
}))els[id].value=v;
const panels=[...html.matchAll(/\bid="(panel-[^"]+)"/g)].map(x=>els[x[1]]);
const pages=[...html.matchAll(/<button[^>]*data-page="([^"]+)"[^>]*>/g)].map(m=>{const e=new E("page");e.dataset.page=m[1];return e});
const opens=[...html.matchAll(/<button[^>]*data-open="([^"]+)"[^>]*>/g)].map(m=>{const e=new E("open");e.dataset.open=m[1];e.dataset.kind=m[0].match(/data-kind="([^"]+)"/)?.[1];return e});
const document={
 getElementById:id=>{assert(els[id],"Missing HTML ID "+id);return els[id]},
 querySelectorAll:q=>q===".panel"?panels:q==="[data-page]"?pages:q==="[data-open]"?opens:q===".pattern-beat"?els["pattern-beats"].children:[],
 createElement:tag=>new E(tag),body:new E("body")
};
const mem=new Map(),storage={getItem:k=>mem.get(k)||null,setItem:(k,v)=>mem.set(k,v)};
new Function("window","document","localStorage","Option","confirm",source)(
 {},document,storage,function(text,value){return{text,value}},()=>true
);
const state=()=>JSON.parse(mem.get("online-school-browser-v1"));
(async()=>{
 assert.match(document.body.className,/is-play/);
 assert.equal(els["pattern-beats"].children.length,8);
 els.nickname.value="Explorer";
 await els["new-learner"].fire("submit");
 assert.equal(state().learners.length,1);
 els["creation-title"].value="Bridge to the Clouds";
 els["creation-body"].value="My pony invents a bridge.";
 await els["creation-form"].fire("submit");
 assert.equal(state().creations.length,1);
 assert.equal(els["play-creations"].children.length,1);
 const card=els["creation-library"].children[0];
 await card.children[3].children[0].fire("click");
 els["creation-body"].value="My pony invents an even better bridge.";
 await els["creation-form"].fire("submit");
 assert.equal(state().creations.length,1);
 assert.match(state().creations[0].body,/better bridge/);
 await els["pattern-beats"].children[0].fire("click");
 await els["pattern-save"].fire("click");
 assert.equal(state().creations[1].tones[0],1);
 const patternCard=els["creation-library"].children[0];
 await patternCard.children[3].children[0].fire("click");
 assert.equal(els["pattern-beats"].children[0].dataset.tone,"1");
 els.retell.value="A little seed grew.";
 await els["reading-note"].fire("submit");
 assert.equal(state().creations[2].kind,"reading");
 els.tried.value="Folded paper";els.observed.value="It held an eraser";
 await els["science-note"].fire("submit");
 assert.equal(state().creations[3].kind,"experiment");
 const match=els.question.textContent.match(/(\d+)\s*([+−×])\s*(\d+)\s*=\s*\?/);
 assert(match,"Expected a math problem");
 const a=+match[1],b=+match[3],value=match[2]==="+"?a+b:match[2]==="×"?a*b:a-b;
 els.answer.value=String(value);
 await els["practice-answer"].fire("submit");
 assert.equal(els["check-answer"].disabled,true);
 const attempts=state().attempts.length;
 await els["practice-answer"].fire("submit");
 assert.equal(state().attempts.length,attempts,"One solved problem must not count twice");
 const backup=state();
 els["import-data"].files=[{size:1000,text:async()=>JSON.stringify(backup)}];
 await els["import-data"].fire("change");
 assert.equal(state().creations.length,4,"All creations survive an export/import round trip");
 process.stdout.write("Play-first browser behavior passed\n");
})().catch(err=>{console.error(err);process.exitCode=1});
"""
        result = subprocess.run(
            ["node", "-e", harness], cwd=ROOT, capture_output=True,
            text=True, timeout=20
        )
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)


if __name__ == "__main__":
    unittest.main()
