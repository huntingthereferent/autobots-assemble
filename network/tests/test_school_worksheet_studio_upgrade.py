"""Worksheet quick starts are real editable inputs, not static visual suggestions."""
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT=Path(__file__).resolve().parents[2]/"companies/online-school/app"


class WorksheetStudioUpgradeTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"),"Node required for the studio preset handlers")
    def test_starter_kits_configure_existing_generator(self):
        js=r'''
const fs=require("node:fs"),vm=require("node:vm"),assert=require("node:assert/strict");
const source=fs.readFileSync(process.argv[1],"utf8");
const fields=new Map(),buttons=[];
function field(id){if(!fields.has(id))fields.set(id,{id,value:"",textContent:"",dispatchEvent(evt){
 if(id==="template")fields.get("columns").value=this.value==="arithmetic"?"2":"1";
 }});return fields.get(id)}
let generated=0;
field("generate-worksheet").click=()=>generated++;
for(const [kit,name] of [["math","Math warm-up"],["words","Word practice"],["reflection","Think & write"]]){
 const b={dataset:{kit},attrs:{},handler:null,querySelector:()=>({textContent:name}),
 addEventListener(_event,handler){this.handler=handler},
 setAttribute(key,value){this.attrs[key]=value}};
 buttons.push(b);
}
const context={document:{getElementById:field,querySelectorAll:()=>buttons},Event:class{constructor(type){this.type=type}}};
vm.createContext(context);vm.runInContext(source,context);
const checks=[
 {type:"math",template:"arithmetic",field:"math-prompt"},
 {type:"words",template:"spelling",field:"words"},
 {type:"reflection",template:"custom",field:"custom-items"}
];
for(let i=0;i<checks.length;i++){
 const spec=checks[i];
 buttons[i].handler();
 assert.equal(field("template").value,spec.template);
 assert(field(spec.field).value.length>10,"Starter must populate usable content");
 assert(field("ws-title").value.length>5);
 assert.equal(buttons[i].attrs["aria-pressed"],"true");
}
assert.equal(generated,3,"Each starter invokes the real generator once");
'''
        r=subprocess.run(["node","-e",js,str(ROOT/"worksheet-presets.js")],
                         capture_output=True,text=True,timeout=12)
        self.assertEqual(r.returncode,0,r.stderr)

    def test_generation_order_and_saved_edit_feedback(self):
        src=(ROOT/"worksheet.js").read_text()
        html=(ROOT/"worksheet.html").read_text()
        self.assertIn("generationSerial",src)
        self.assertIn("if(serial!==generationSerial)return;",src)
        self.assertIn('editStatus("Unsaved question edits.")',src)
        self.assertIn('editStatus("Saved to the worksheet library.")',src)
        self.assertIn('data-kit="reflection"',html)
        self.assertIn('worksheet-refresh.css',html)


if __name__=="__main__":
    unittest.main()
