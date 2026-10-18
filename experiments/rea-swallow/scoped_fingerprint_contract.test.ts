import { parse } from "@babel/parser";
import { runInNewContext } from "node:vm";
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname } from "node:path";
import { describe, expect, it } from "vitest";
import { fingerprintJavaScriptAst, fingerprintJavaScriptAstParameterRelations,
  fingerprintJavaScriptAstScopedReferences } from "./javascriptAstFingerprint.js";

const v3=(s:string)=>fingerprintJavaScriptAst(parse(s));
const v5=(s:string)=>fingerprintJavaScriptAstScopedReferences(parse(s));
const source=(mask:number,outer="a",inner="b",local="run")=>{
  const uses=Array.from({length:4},(_,i)=>(mask&(1<<i))?inner:outer);
  return "function select("+outer+") { const "+local+" = ("+inner+") => ["+
    uses.join(",")+"]; return "+local+"(29); }";
};
const exec=(s:string)=>JSON.stringify(runInNewContext(s+"; select(11)",{}, {timeout:1000}));
describe("REA experimental scoped-reference A/B evidence",()=>{
  it("separates 16 closure choices while retaining their 16 consistent renames",()=>{
    const old=new Set<string>(), now=new Set<string>(), observed=new Set<string>(), rows=[];
    for(let mask=0;mask<16;mask++){
      const a=source(mask);
      const renamed=source(mask,"outer","inner","callback");
      expect(v3(a)).toBe(v3(renamed));
      expect(v5(a)).toMatch(/^[0-9a-f]{64}$/u);
      expect(v5(a)).toBe(v5(renamed));
      old.add(v3(a));
      now.add(v5(a)!);
      observed.add(exec(a));
      rows.push({mask,result:JSON.parse(exec(a)),old:v3(a),scoped:v5(a)});
    }
    expect(old.size).toBe(1);
    expect(now.size).toBe(16);
    expect(observed.size).toBe(16);
    for(const [a,b] of [
      ["function select(a){const run=(b)=>a;return run(29);}",
       "function select(a){const run=(b)=>b;return run(29);}"],
      ["function select(a){const x=a;{const x=29;return x;}}",
       "function select(a){const x=a;{const x=29;return a;}}"],
      ["function select(a){const run=(b)=>{const c=a;return c;};return run(29);}",
       "function select(a){const run=(b)=>{const c=b;return c;};return run(29);}"]
    ] as const) {
      expect(v3(a)).toBe(v3(b));
      expect(v5(a)).not.toBe(v5(b));
      expect(exec(a)).not.toBe(exec(b));
    }
    expect(v5("function select(a){const x=a;{const x=29;return x;}}"))
      .toBe(v5("function select(left){const outer=left;{const inner=29;return inner;}}"));
    const path=process.env.REA_AB_SCOPED_OUTPUT;
    if(path){
      mkdirSync(dirname(path),{recursive:true});
      writeFileSync(path,JSON.stringify({algorithm:"babel-ast-scoped-references-v1",
        original_classes:old.size,experimental_classes:now.size,distinct_runtime_witnesses:observed.size,
        rename_pairs:16,cases:rows},null,2)+"\n");
    }
  });
  it("rejects constructs outside its declared scope",()=>{
    for(const s of [
      "function select({x}){return x;}",
      "function select(a){var x=a;return x;}",
      "function select(a){try{return a;}catch(e){return e;}}",
      "function select(a){function nested(b){return b;}return nested(a);}",
      "function select(a){for(let i=0;i<2;i++){}return a;}",
      "function select(a){const {x}=a;return x;}",
      "function select(a){const f=function named(b){return a+b;};return f(2);}"
    ]) expect(v5(s)).toBeNull();
  });
  it("retains the previously validated simpler binding experiment",()=>{
    const a="function select(a,b){return a;}";
    const b="function select(a,b){return b;}";
    expect(fingerprintJavaScriptAstParameterRelations(parse(a)))
      .not.toBe(fingerprintJavaScriptAstParameterRelations(parse(b)));
    expect(v5(a)).not.toBe(v5(b));
  });
});
