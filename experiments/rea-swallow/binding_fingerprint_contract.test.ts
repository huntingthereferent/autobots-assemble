import { parse } from "@babel/parser";
import { runInNewContext } from "node:vm";
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname } from "node:path";
import { describe, it, expect } from "vitest";
import {
  fingerprintJavaScriptAst,
  fingerprintJavaScriptAstParameterRelations,
} from "./javascriptAstFingerprint.js";

const sourceFor = (choice: number, left="a", right="b") => {
  const positions = Array.from({length:4}, (_,index)=>(choice & (1 << index)) ? right : left);
  return "function select("+left+","+right+") { return ["+positions.join(",")+"]; }";
};
const fingerprint = (source: string) => fingerprintJavaScriptAstParameterRelations(parse(source));

describe("REA A/B lexical reference identity experiment", () => {
  it("separates all 16 reference choices while preserving 16 consistent renames", () => {
    const outputs = [];
    const oldSet = new Set<string>();
    const newSet = new Set<string>();
    const observed = new Set<string>();
    for (let mask=0;mask<16;mask++) {
      const before = sourceFor(mask);
      const renamed = sourceFor(mask,"left","right");
      const v3 = fingerprintJavaScriptAst(parse(before));
      const v4 = fingerprint(before);
      const v4Renamed = fingerprint(renamed);
      const behavior = JSON.stringify(runInNewContext(before+"; select(11,29)",{}, {timeout:1000}));
      expect(v4).toMatch(/^[0-9a-f]{64}$/u);
      expect(v4).toBe(v4Renamed);
      expect(v3).toBe(fingerprintJavaScriptAst(parse(renamed)));
      oldSet.add(v3);
      newSet.add(v4!);
      observed.add(behavior);
      outputs.push({mask,returned:JSON.parse(behavior),old_fingerprint:v3,
        reference_fingerprint:v4,renamed_reference_fingerprint:v4Renamed});
    }
    expect(oldSet.size).toBe(1);
    expect(newSet.size).toBe(16);
    expect(observed.size).toBe(16);
    for (const [a,b] of [
      ["function pick(a,b){return a;}", "function pick(a,b){return b;}"],
      ["function calc(a,b){return a-b;}", "function calc(a,b){return b-a;}"],
      ["function pick(a,b){const result=a;return result;}", "function pick(a,b){const result=b;return result;}"],
    ] as const) {
      expect(fingerprintJavaScriptAst(parse(a))).toBe(fingerprintJavaScriptAst(parse(b)));
      expect(fingerprint(a)).not.toBe(fingerprint(b));
    }
    expect(fingerprint("function get(a,b){return globalThis;}"))
      .not.toBe(fingerprint("function get(a,b){return externalGlobal;}"));
    const out=process.env.REA_AB_BINDING_OUTPUT;
    if(out) {
      mkdirSync(dirname(out),{recursive:true});
      writeFileSync(out,JSON.stringify({
        supported_domain:"single function with identifier parameters and non-shadowing simple local declarations",
        original_v3_fingerprint_classes:oldSet.size,
        binding_aware_fingerprint_classes:newSet.size,
        distinctly_observed_output_words:observed.size,
        consistent_rename_pairs_checked:16,
        proposed_algorithm:"babel-ast-parameter-relations-v1",
        upstream_default_algorithm_unchanged:"babel-ast-v3",
        cases:outputs
      },null,2)+"\n");
    }
  });
  it("rejects unsupported lexical shadowing, nested functions and destructuring",()=>{
    for(const source of [
      "function f(a,b){ function g(a){return a;} return g(b); }",
      "function f(a,b){ {const a=2; return a;} }",
      "function f({a},b){ return a; }",
      "function f(a,b){ try {return a;} catch (a) {return a;} }",
    ]) {
      expect(fingerprint(source)).toBeNull();
    }
  });
});
