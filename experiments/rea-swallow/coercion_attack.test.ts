import {parse} from "@babel/parser";
import {runInNewContext} from "node:vm";
import {mkdirSync,writeFileSync} from "node:fs";
import {dirname} from "node:path";
import {describe,expect,it} from "vitest";
import {fingerprintJavaScriptAstScopedReferences as scoped,
  fingerprintJavaScriptAstScopedReferencesGuarded as guarded} from "./javascriptAstFingerprint.js";
const t=String.fromCharCode(96);
const pairs=[
  {id:"function-String",a:"function select(a){return String(select);}",b:"function renamed(b){return String(renamed);}",ca:"select(11)",cb:"renamed(11)"},
  {id:"function-plus-string",a:'function select(a){return select+"";}',b:'function renamed(b){return renamed+"";}',ca:"select(11)",cb:"renamed(11)"},
  {id:"function-template",a:"function select(a){return "+t+"$"+"{select}"+t+";}",b:"function renamed(b){return "+t+"$"+"{renamed}"+t+";}",ca:"select(11)",cb:"renamed(11)"},
  {id:"inferred-arrow-name",a:"function select(a){const dog=(b)=>a+b;return String(dog);}",b:"function select(x){const cat=(y)=>x+y;return String(cat);}",ca:"select(11)",cb:"select(11)"},
  {id:"array-join",a:'function select(a){return [select].join("|");}',b:'function renamed(b){return [renamed].join("|");}',ca:"select(11)",cb:"renamed(11)"}
] as const;
describe("A/B native REA implicit function-stringification counterexamples",()=>{
 it("witnesses identical fingerprints with distinct real outputs",()=>{
  const rows=[];
  for(const p of pairs){
    const la=parse(p.a),rb=parse(p.b);
    const s=scoped(la),g=guarded(la);
    const left=runInNewContext(p.a+";"+p.ca,{}, {timeout:1000});
    const right=runInNewContext(p.b+";"+p.cb,{}, {timeout:1000});
    expect(s).toMatch(/^[a-f0-9]{64}$/u);
    expect(scoped(rb)).toBe(s);
    expect(g).toBe(s);
    expect(guarded(rb)).toBe(g);
    expect(left).not.toBe(right);
    rows.push({id:p.id,source_a:p.a,source_b:p.b,digest:g,
      observed_a:left,observed_b:right,meaning_changed:true});
  }
  expect(rows).toHaveLength(5);
  const path=process.env.REA_AB_COERCION_OUTPUT;
  if(path){
    mkdirSync(dirname(path),{recursive:true});
    writeFileSync(path,JSON.stringify({upstream:"morluto/rea@f0b9ef34c404c1c65f8167502db972b0bd708403",
      subject:"A/B experimental guarded scoped fingerprint, not upstream production REA",
      observation:"implicit conversion of function values reveals changed source spelling",
      collisions:rows.length, cases:rows},null,2)+"\n");
  }
 });
});
