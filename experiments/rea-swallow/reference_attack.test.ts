import { parse } from "@babel/parser";
import { runInNewContext } from "node:vm";
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname } from "node:path";
import { describe, expect, it } from "vitest";
import { fingerprintJavaScriptAst, fingerprintJavaScriptAstScopedReferences } from "./javascriptAstFingerprint.js";

// These are bounded, authored programs. They are NOT an inference of general equivalence.
const probes = [
  { id: "function-name-reflection",
    left: "function select(a){return select.name;}",
    right:"function renamed(b){return renamed.name;}",
    callLeft:"select(11)",callRight:"renamed(11)", expectedCollision:true },
  { id: "direct-eval-captures-parameter-spelling",
    left:'function select(a){return eval("a");}',
    right:'function select(b){return eval("a");}',
    callLeft:"select(11)",callRight:"select(11)",expectedCollision:true },
  { id: "implicit-arguments-callee-name-reflection",
    left:"function select(a){return arguments.callee.name;}",
    right:"function renamed(b){return arguments.callee.name;}",
    callLeft:"select(11)",callRight:"renamed(11)",expectedCollision:true },
  { id: "arrow-name-inferred-from-local-binding",
    left:"function select(a){const dog=()=>a;return dog.name;}",
    right:"function select(b){const cat=()=>b;return cat.name;}",
    callLeft:"select(11)",callRight:"select(11)",expectedCollision:true },
  { id: "ordinary-consistent-parameter-rename",
    left:"function select(a){return a+1;}",
    right:"function select(b){return b+1;}",
    callLeft:"select(11)",callRight:"select(11)",expectedCollision:true },
  { id: "assignment-target-choice",
    left:"function select(a,b){let x=a; x=b; return x;}",
    right:"function select(a,b){let x=a; b=x; return x;}",
    callLeft:"select(11,29)",callRight:"select(11,29)",expectedCollision:false },
] as const;
function execute(source: string, call: string) {
  try {
    const result: unknown = runInNewContext(source+";"+call,{}, {timeout:1000});
    return {state:"returned",value:result};
  } catch (err: unknown) {
    return {state:"threw", error:err instanceof Error ? err.name : Object.prototype.toString.call(err)};
  }
}
describe("A/B source attack on REA's scoped candidate representation",()=>{
  it("retains explicitly witnessed observational collisions instead of asserting semantic identity",()=>{
    const results=[];
    for(const p of probes){
      const fingerprint1=fingerprintJavaScriptAstScopedReferences(parse(p.left));
      const fingerprint2=fingerprintJavaScriptAstScopedReferences(parse(p.right));
      const actual1=execute(p.left,p.callLeft), actual2=execute(p.right,p.callRight);
      const sameBehavior=JSON.stringify(actual1)===JSON.stringify(actual2);
      const collision=fingerprint1!==null && fingerprint1===fingerprint2;
      // Establish fixed, reproducible counterexamples for the supported syntax.
      expect(collision).toBe(p.expectedCollision);
      if(p.id==="ordinary-consistent-parameter-rename") expect(sameBehavior).toBe(true);
      else expect(sameBehavior).toBe(false);
      results.push({
        case_id:p.id,
        sources:[p.left,p.right],
        original_fingerprint_equal:fingerprintJavaScriptAst(parse(p.left))===fingerprintJavaScriptAst(parse(p.right)),
        scoped_fingerprint_equal:collision,scoped_left:fingerprint1,scoped_right:fingerprint2,
        observation_left:actual1,observation_right:actual2,
        same_observed_result:sameBehavior,
        interpretation:collision && !sameBehavior ? "OBSERVED_COLLISION" : "CONTROL_OR_DISTINGUISHED"
      });
    }
    expect(results.filter(p=>p.interpretation==="OBSERVED_COLLISION")).toHaveLength(4);
    const out=process.env.REA_AB_ATTACK_OUTPUT;
    if(out){
      mkdirSync(dirname(out),{recursive:true});
      writeFileSync(out,JSON.stringify({
        pinned_upstream:"f0b9ef34c404c1c65f8167502db972b0bd708403",
        target:"babel-ast-scoped-references-v1 (not the upstream default)",
        evidence_kind:"same structural digest, different evaluated outputs",
        caveat:"No semantic-equivalence claim by upstream REA",
        cases:results
      },null,2)+"\n");
    }
  });
});
