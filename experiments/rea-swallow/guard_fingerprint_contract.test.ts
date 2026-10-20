import { parse } from "@babel/parser";
import { runInNewContext } from "node:vm";
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname } from "node:path";
import { describe, it, expect } from "vitest";
import {
  fingerprintJavaScriptAstScopedReferences,
  fingerprintJavaScriptAstScopedReferencesGuarded
} from "./javascriptAstFingerprint.js";
const v5=(s:string)=>fingerprintJavaScriptAstScopedReferences(parse(s));
const guarded=(s:string)=>fingerprintJavaScriptAstScopedReferencesGuarded(parse(s));

const traps=[
  ["self-name","function select(a){return select.name;}","function renamed(b){return renamed.name;}"],
  ["direct-eval",'function select(a){return eval("a");}','function select(b){return eval("a");}'],
  ["arguments-callee","function select(a){return arguments.callee.name;}","function renamed(b){return arguments.callee.name;}"],
  ["inferred-arrow-name","function select(a){const dog=()=>a;return dog.name;}","function select(b){const cat=()=>b;return cat.name;}"],
  ["computed-function-name",'function select(a){return select["name"];}','function renamed(b){return renamed["name"];}'],
  ["reflective-name-descriptor",'function select(a){return Object.getOwnPropertyDescriptor(select,"name")?.value;}','function renamed(b){return Object.getOwnPropertyDescriptor(renamed,"name")?.value;}']
] as const;
const benign=(mask:number,a="a",b="b",f="run")=>{
  const words=Array.from({length:4},(_,i)=>(mask&(1<<i))?b:a);
  return "function select("+a+"){const "+f+"=("+b+")=>["+words.join(",")+"];return "+f+"(29);}";
};
describe("REA source A/B reflection-aware conservative fingerprint",()=>{
  it("refuses all known same-fingerprint/different-behavior witnesses",()=>{
    const rows=[];
    for(const [id,left,right] of traps){
      const original=v5(left), renamed=v5(right);
      expect(original).not.toBeNull();
      expect(original).toBe(renamed);
      const controlLeft=guarded(left), controlRight=guarded(right);
      expect(controlLeft).toBeNull();
      expect(controlRight).toBeNull();
      rows.push({id,original_same_digest:original===renamed,guarded_left:controlLeft,guarded_right:controlRight});
    }
    const out=process.env.REA_AB_GUARD_OUTPUT;
    if(out){
      mkdirSync(dirname(out),{recursive:true});
      writeFileSync(out,JSON.stringify({
        upstream_original_fingerprint_untouched:true,
        previous_lexical_fingerprint_untouched:true,
        reason:"Runtime name reflection and eval expose lexical spellings not represented by alpha-renaming.",
        traps:rows
      },null,2)+"\n");
    }
  });
  it("still classifies 16 closure choices and preserves 16 harmless consistent renames",()=>{
    const digests=new Set<string>();
    const observations=new Set<string>();
    for(let mask=0;mask<16;mask++){
      const a=benign(mask), b=benign(mask,"outer","inner","callback");
      expect(guarded(a)).toMatch(/^[0-9a-f]{64}$/u);
      expect(guarded(a)).toBe(guarded(b));
      expect(guarded(a)).toBe(v5(a));
      digests.add(guarded(a)!);
      observations.add(JSON.stringify(runInNewContext(a+";select(11)",{}, {timeout:1000})));
    }
    expect(digests.size).toBe(16);
    expect(observations.size).toBe(16);
  });
});
