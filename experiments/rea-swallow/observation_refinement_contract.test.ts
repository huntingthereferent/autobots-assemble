import { createHash } from "node:crypto";
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname } from "node:path";
import { runInNewContext } from "node:vm";
import { parse } from "@babel/parser";
import { describe, expect, it } from "vitest";
import { artifactEvidence, fixtureNode } from "./javascriptApplicationGraph.fixture.js";
import { fingerprintJavaScriptAst } from "./javascriptAstFingerprint.js";
import { matchJavaScriptApplicationVersions, refineJavaScriptApplicationPairByObservations,
  type ApplicationVersionInputObservation } from "./javascriptApplicationVersionKeys.js";

const sha = (input: string) => createHash("sha256").update(input).digest("hex");
const program = (mask: number): string => {
  const chosen=Array.from({length:4},(_,i)=>(mask&(1<<i))?"b":"a");
  return "function pick(a,b){return ["+chosen.join(",")+"];}";
};
const nodeFor = (source: string, position: "L"|"R") => {
  const artifact = (position==="L"?"a":"b").repeat(64);
  return fixtureNode("javascript-module", {
    strategy: "canonical-path",stability:"artifact-version",
    artifact_sha256:artifact,path:position+".js",
  },position+".js", {
    source_sha256:sha(source),
    structural_fingerprint_sha256:fingerprintJavaScriptAst(parse(source)),
    structural_fingerprint_algorithm:"babel-ast-v3",
  },artifactEvidence(artifact,position+".js"));
};
const capture = (code:string, contextId:string, args:readonly number[]):ApplicationVersionInputObservation => {
  // This runner executes only the 16 deterministic source strings authored above.
  // Actual REA is not asked to execute arbitrary external artifacts.
  const inputDigest=sha(JSON.stringify(args));
  try {
    const value:unknown=runInNewContext(code+";pick("+args.join(",")+")",{}, {timeout:1000});
    return {contextId,inputDigest,result:{status:"returned",canonicalValue:JSON.stringify(value)}};
  } catch(err:unknown){
    return {contextId,inputDigest,result:{status:"threw",errorName:err instanceof Error?err.name:"Error",
      message:err instanceof Error?err.message:"unknown"}};
  }
};
describe("REA A/B finite observation refinement of structural matching",()=>{
 it("refines one structural class into 16 witnessed behavior classes without asserting equivalence",()=>{
   const programs=Array.from({length:16},(_,i)=>program(i));
   expect(new Set(programs.map(p=>fingerprintJavaScriptAst(parse(p)))).size).toBe(1);
   const captures=programs.map(p=>({
     equal:capture(p,"equal-arguments",[11,11]),
     separated:capture(p,"different-arguments",[11,29])
   }));
   const sourceResults=[];
   let initiallyUnknown=0,witnessed=0,stillUndetermined=0;
   for(let left=0;left<16;left++) for(let right=0;right<16;right++){
      const original=matchJavaScriptApplicationVersions(
        [nodeFor(programs[left]!,"L")],[nodeFor(programs[right]!,"R")]);
      expect(original.pairs).toHaveLength(1);
      expect(original.pairs[0]).toMatchObject({basis:"structural-fingerprint",confidence:"medium"});
      const pair=original.pairs[0]!;
      const initial=refineJavaScriptApplicationPairByObservations(pair,
        [captures[left]!.equal],[captures[right]!.equal]);
      expect(initial.result).toBe("undetermined");
      expect(initial.agreeingContextIds).toEqual(["equal-arguments"]);
      initiallyUnknown++;
      const after=refineJavaScriptApplicationPairByObservations(pair,
        [captures[left]!.equal,captures[left]!.separated],
        [captures[right]!.equal,captures[right]!.separated]);
      if(left===right){
        expect(after.result).toBe("undetermined");
        expect(after.separatingContextIds).toEqual([]);
        stillUndetermined++;
      }else{
        expect(after.result).toBe("witnessed-difference");
        expect(after.separatingContextIds).toEqual(["different-arguments"]);
        witnessed++;
      }
      sourceResults.push({left,right,before:initial.result,after:after.result,
        witnessed:after.separatingContextIds});
   }
   expect(initiallyUnknown).toBe(256);
   expect(witnessed).toBe(240);
   expect(stillUndetermined).toBe(16);
   expect(new Set(captures.map(c=>c.separated.result.status==="returned"
     ? c.separated.result.canonicalValue : "unsupported")).size).toBe(16);
   const output=process.env.REA_AB_OBSERVATION_OUTPUT;
   if(output){
     mkdirSync(dirname(output),{recursive:true});
     writeFileSync(output,JSON.stringify({
       upstream:"morluto/rea@f0b9ef34c404c1c65f8167502db972b0bd708403",
       actual_matcher_basis:"structural-fingerprint",
       candidate_programs:16,comparisons:256,
       comparisons_with_equal_only_context:"256/256 undetermined",
       distinctions_after_one_more_context:witnessed,
       pairs_still_undetermined:stillUndetermined,
       not_claimed:"Observational agreement never establishes universal equivalence",
       results:sourceResults
     })+"\n");
   }
 });
 it("ignores incomparable contexts, reports unknown results, and fails closed on duplicates",()=>{
   const a=nodeFor(program(0),"L"),b=nodeFor(program(1),"R");
   const pair=matchJavaScriptApplicationVersions([a],[b]).pairs[0]!;
   const l={contextId:"same-label",inputDigest:sha("different-left"),result:{status:"returned" as const,canonicalValue:"11"}};
   const r={contextId:"same-label",inputDigest:sha("different-right"),result:{status:"returned" as const,canonicalValue:"29"}};
   const noFalseWitness=refineJavaScriptApplicationPairByObservations(pair,[l],[r]);
   expect(noFalseWitness.result).toBe("undetermined");
   expect(noFalseWitness.incomparableContextIds).toEqual(["same-label"]);
   expect(refineJavaScriptApplicationPairByObservations(pair,[l],[])
     .incomparableContextIds).toEqual(["same-label"]);
   const unknown={...l,inputDigest:sha("common"),result:{status:"unknown" as const,reason:"unresolved"}};
   const observed={...r,inputDigest:sha("common")};
   const partial=refineJavaScriptApplicationPairByObservations(pair,[unknown],[observed]);
   expect(partial.result).toBe("undetermined");
   expect(partial.unresolvedContextIds).toEqual(["same-label"]);
   expect(()=>refineJavaScriptApplicationPairByObservations(pair,[l,l],[r])).toThrow(/duplicate/);
   expect(refineJavaScriptApplicationPairByObservations(pair,[],[]).result).toBe("undetermined");
   const witnessed=refineJavaScriptApplicationPairByObservations(pair,[
     capture(program(0),"different-arguments",[11,29]),unknown
   ],[
     capture(program(1),"different-arguments",[11,29]),observed
   ]);
   expect(witnessed.result).toBe("witnessed-difference");
   expect(witnessed.unresolvedContextIds).toEqual(["same-label"]);
 });
});
