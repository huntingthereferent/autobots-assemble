import {parse} from "@babel/parser";
import {runInNewContext} from "node:vm";
import {mkdirSync,writeFileSync} from "node:fs";
import {dirname} from "node:path";
import {describe,expect,it} from "vitest";
import {fingerprintJavaScriptAstScopedReferencesGuarded as previous,
  fingerprintJavaScriptAstCoercionGuarded as guarded} from "./javascriptAstFingerprint.js";
const t=String.fromCharCode(96);
const attacks=[
 ["String","function select(a){return String(select);}","function renamed(b){return String(renamed);}"],
 ["addition",'function select(a){return select+"";}','function renamed(b){return renamed+"";}'],
 ["template","function select(a){return "+t+"$"+"{select}"+t+";}","function renamed(b){return "+t+"$"+"{renamed}"+t+";}"],
 ["arrow","function select(a){const dog=(b)=>a+b;return String(dog);}","function select(x){const cat=(y)=>x+y;return String(cat);}"],
 ["join",'function select(a){return [select].join("|");}','function renamed(b){return [renamed].join("|");}']
] as const;
const benign=(mask:number,a="a",b="b",local="run")=>{
 const args=Array.from({length:4},(_,i)=>(mask&(1<<i))?b:a);
 return "function select("+a+"){const "+local+"=("+b+")=>["+args.join(",")+"];return "+local+"(29);}";
};
describe("REA A/B bounded implicit-coercion guard source candidate",()=>{
 it("refuses five reproducible coercion traps that the previous guard accepted",()=>{
  const witnesses=[];
  for(const [id,a,b] of attacks){
    const oldA=previous(parse(a)),oldB=previous(parse(b));
    expect(oldA).toMatch(/^[a-f0-9]{64}$/u);
    expect(oldA).toBe(oldB);
    expect(guarded(parse(a))).toBeNull();
    expect(guarded(parse(b))).toBeNull();
    witnesses.push({id,prior_collision:true,now_unknown:true});
  }
  expect(witnesses.length).toBe(5);
  const out=process.env.REA_AB_COERCION_GUARD_OUTPUT;
  if(out){
   mkdirSync(dirname(out),{recursive:true});
   writeFileSync(out,JSON.stringify({source:"real pinned REA TypeScript",
    limitation:"Known coercion sites rejected; NOT a general JavaScript equivalence guarantee",
    old_guard_unchanged:true,witnesses},null,2)+"\n");
  }
 });
 it("retains all 16 finite closure-reference partitions and 16 rename invariants",()=>{
  const classes=new Set<string>(),observations=new Set<string>();
  for(let mask=0;mask<16;mask++){
   const original=benign(mask),renamed=benign(mask,"outer","inner","callback");
   const a=guarded(parse(original));
   expect(a).toMatch(/^[a-f0-9]{64}$/u);
   expect(a).toBe(guarded(parse(renamed)));
   expect(a).toBe(previous(parse(original)));
   classes.add(a!);
   observations.add(JSON.stringify(runInNewContext(original+";select(11)",{}, {timeout:1000})));
  }
  expect(classes.size).toBe(16);
  expect(observations.size).toBe(16);
 });
 it("conservatively refuses operator and conversion sites regardless of primitive-only values",()=>{
   for(const code of ["function f(a){return a+1;}","function f(a){return [a].join(',');}",
       "function f(a){return String(a);}"]) expect(guarded(parse(code))).toBeNull();
 });
});
