"""Execute actual Continuity card renderers with markup-shaped source metadata."""
from pathlib import Path
import shutil
import subprocess
import unittest

JS = Path(__file__).resolve().parents[2] / "runtime/http/app.js"


class ContinuityCardDomTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "Node required for rendered card boundary checks")
    def test_untrusted_card_values_are_only_dom_text_and_buttons_keep_handlers(self):
        script = r'''
const fs=require("node:fs");
const vm=require("node:vm");
const assert=require("node:assert/strict");
const source=fs.readFileSync(process.argv[1],"utf8");
function block(begin,end){
 const a=source.indexOf(begin), b=source.indexOf(end,a+begin.length);
 assert(a>=0&&b>a,"Missing source block: "+begin);
 return source.slice(a,b);
}
class Element {
 constructor(tag){
   this.tag=tag;this.children=[];this.className="";this.dataset={};
   this.handlers={};this.value="";this.type="";
   this.classList={add:(value)=>{this.className+=" "+value;}};
 }
 set textContent(value){this.value=String(value??"");this.children=[]}
 get textContent(){return this.value+this.children.map(x=>x.textContent).join("")}
 set innerHTML(_){throw Error("Untrusted markup construction attempted")}
 append(...elements){for(const element of elements){
   assert(element instanceof Element,"Card extras must be explicit DOM nodes");
   this.children.push(element);
 }}
 replaceChildren(...elements){this.children=elements;}
 addEventListener(kind,fn){this.handlers[kind]=fn;}
 querySelector(selector){
   const wanted=selector.slice(1);
   const nodes=[...this.children];
   while(nodes.length){
     const node=nodes.shift();
     if(node.className.split(/\s+/).includes(wanted))return node;
     nodes.push(...node.children);
   }
   return null;
 }
}
const ids=["#calendar-events","#tasks","#handoffs","#attention-tasks",
 "#attention-calendar","#attention-reminders"];
const roots=Object.fromEntries(ids.map(x=>[x,new Element("div")]));
const markup='<img src=x onerror=alert(1)>';
const fixture={
 "/api/calendar":{events:[{title:markup,starts_at:"now",movement_anchor:markup,referent:markup}]},
 "/api/tasks":{tasks:[
  {title:markup,task_id:markup,assignee:markup,referent:markup},
  {title:"Completed",task_id:"safe",assignee:"A",referent:"test",
   admitted_handoff_id:1,result:{status:markup}}
 ]},
 "/api/handoffs":{handoffs:[{metadata:{title:markup,source_system:markup},
  required_relation:markup,to_actor:markup,status:markup,from_actor:"A"}]}
};
const ctx={document:{createElement:tag=>new Element(tag)},
  $:id=>roots[id],
  api:async path=>fixture[path],
  refreshAll:async()=>{},
  activateOhayo:async()=>{},
  localDateKey:()=>"2026-10-22",
  showError:err=>{throw err},
  encodeURIComponent};
vm.createContext(ctx);
const extracted=[
 block("function cardChip(","function areaCard("),
 block("async function refreshCalendar()","async function refreshReminders()"),
 block("async function refreshTasks()","let liveFeedState"),
 block("async function refreshHandoffs()","function renderAttention("),
 block("function renderAttention(","async function refreshAttention()")
].join("\n");
vm.runInContext(extracted,ctx);
(async()=>{
 await ctx.refreshCalendar();
 await ctx.refreshTasks();
 await ctx.refreshHandoffs();
 ctx.renderAttention({
  tasks:[{title:markup,status:markup,referent:markup}],
  calendar:[{title:markup,movement_anchor:markup,referent:markup}],
  reminders:[{text:markup,id:markup,local_time:markup,referent:markup}]
 });
 const all=[],stack=Object.values(roots);
 while(stack.length){const el=stack.pop();all.push(el);stack.push(...el.children);}
 assert(!all.some(x=>x.tag==="img"),"Markup was treated as an actual DOM tag");
 assert(all.filter(x=>x.tag==="span").some(x=>x.textContent===markup));
 assert(all.filter(x=>x.tag==="div").some(x=>x.textContent.includes(markup)));
 assert(!all.some(x=>x.className.includes("<")), "Status became an unsafe class");
 const admit=all.find(x=>x.className==="admit");
 const ack=all.find(x=>x.className==="ack-reminder");
 assert(admit&&ack);
 assert.equal(admit.dataset.id,markup);
 assert.equal(ack.dataset.id,markup);
 assert.equal(admit.type,"button");
 assert.equal(ack.type,"button");
 assert.equal(typeof admit.handlers.click,"function");
 assert.equal(typeof ack.handlers.click,"function");
})().catch(err=>{console.error(err);process.exitCode=1});
'''
        result = subprocess.run(
            ["node", "-e", script, str(JS)],
            capture_output=True, text=True, timeout=12,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
