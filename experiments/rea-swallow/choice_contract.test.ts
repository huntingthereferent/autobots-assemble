import {createHash} from "node:crypto";
import {mkdirSync,writeFileSync} from "node:fs";
import {dirname} from "node:path";
import {runInNewContext} from "node:vm";
import {parse} from "@babel/parser";
import {describe,expect,it} from "vitest";
import {artifactEvidence,fixtureNode} from "./javascriptApplicationGraph.fixture.js";
import {fingerprintJavaScriptAst} from "./javascriptAstFingerprint.js";
import {
  matchJavaScriptApplicationVersions,
  refineJavaScriptApplicationPairByObservations,
  selectNextJavaScriptApplicationObservation,
  type ApplicationVersionObservationLedger,
  type ApplicationVersionInputObservation
} from "./javascriptApplicationVersionKeys.js";

const hash=(v:string)=>createHash("sha256").update(v).digest("hex");
const program=(mask:number)=>{
  const items=Array.from({length:4},(_,i)=>((mask&(1<<i))?"b":"a")+"["+i+"]");
  return "function pick(a,b){return ["+items.join(",")+"];}";
};
const node=(source:string,side:"L"|"R")=>{
  const key=(side==="L"?"a":"b").repeat(64);
  return fixtureNode("javascript-module",{
    strategy:"canonical-path",stability:"artifact-version",
    artifact_sha256:key,path:side+".js"
  },side+".js",{
    source_sha256:hash(source),
    structural_fingerprint_sha256:fingerprintJavaScriptAst(parse(source)),
    structural_fingerprint_algorithm:"babel-ast-v3"
  },artifactEvidence(key,side+".js"));
};
const contexts=[
  {id:"baseline-all-equal",active:-1},
  {id:"probe-0",active:0},
  {id:"probe-1",active:1},
  {id:"probe-2",active:2},
  {id:"probe-3",active:3},
] as const;
function externalCapture(source:string,id:string,active:number):ApplicationVersionInputObservation{
  const a=[0,0,0,0],b=[0,0,0,0];
  if(active>=0)b[active]=7;
  const args=JSON.stringify([a,b]);
  // This source runs only in this trusted fixture; the actual REA selector never executes source.
  const result:unknown=runInNewContext(source+";pick(..."+args+")",{}, {timeout:1000});
  return {contextId:id,inputDigest:hash(args),
    result:{status:"returned",canonicalValue:JSON.stringify(result)}};
}
const sources=Array.from({length:16},(_,mask)=>program(mask));
const observations=sources.map(source=>
  contexts.map(c=>externalCapture(source,c.id,c.active)));
function ledger(left:number,right:number):ApplicationVersionObservationLedger{
  const matched=matchJavaScriptApplicationVersions([node(sources[left]!,"L")],[node(sources[right]!,"R")]);
  if(matched.pairs.length!==1)throw Error("upstream REA matching failed");
  return {ledgerId:"L"+left+"-R"+right,pair:matched.pairs[0]!,
    left:observations[left]!,right:observations[right]!};
}
describe("REA A/B next-observation selection from real previously collected witnesses",()=>{
 it("chooses 4 evidence-based probes and separates 240 unresolved matches without assuming equivalence",()=>{
   expect(new Set(sources.map(s=>fingerprintJavaScriptAst(parse(s)))).size).toBe(1);
   const pool=Array.from({length:256},(_,i)=>ledger(Math.floor(i/16),i%16));
   let known=["baseline-all-equal"];
   const steps=[];
   const expectedNew=[128,64,32,16];
   for(let round=0;round<4;round++){
     const selected=selectNextJavaScriptApplicationObservation(pool,known);
     expect(selected.status).toBe("selected");
     expect(selected.newlySeparatingPairs).toBe(expectedNew[round]);
     // Tie resolution depends on evidence counts, not preselected input values.
     expect(selected.contextId).toBe("probe-"+round);
     const allScores=selected.candidateScores;
     expect(allScores.length).toBe(4-round);
     expect(allScores.every(row=>row.newSeparations>=0)).toBe(true);
     known=[...known,selected.contextId!];
     const distinct=pool.filter(l=>refineJavaScriptApplicationPairByObservations(
       l.pair,
       l.left.filter(o=>known.includes(o.contextId)),
       l.right.filter(o=>known.includes(o.contextId))
     ).result==="witnessed-difference");
     steps.push({round,chosen:selected.contextId,
       newly_distinguished:selected.newlySeparatingPairs,
       total_witnessed:distinct.length,
       currently_unresolved:pool.length-distinct.length,
       scores:allScores});
   }
   expect(steps.map(s=>s.total_witnessed)).toEqual([128,192,224,240]);
   const exhausted=selectNextJavaScriptApplicationObservation(pool,known);
   expect(exhausted.status).toBe("no-new-witness");
   expect(exhausted.contextId).toBeNull();
   expect(exhausted.remainingUndeterminedPairs).toBe(16);
   expect(exhausted.candidateScores).toEqual([]);
   expect(steps.map(s=>s.currently_unresolved)).toEqual([128,64,32,16]);
   const out=process.env.REA_AB_CHOICE_OUTPUT;
   if(out){
     mkdirSync(dirname(out),{recursive:true});
     writeFileSync(out,JSON.stringify({
       upstream:"morluto/rea@f0b9ef34c404c1c65f8167502db972b0bd708403",
       captured_programs:16,ordered_pair_ledgers:256,
       candidate_pool:"5 captured contexts including baseline; externally evaluated in trusted fixture",
       selection_rule:"max new witnessed differences among currently unresolved, codepoint-order ties",
       autonomous_claim:false,
       runner_executes_arbitrary_untrusted_source:false,
       never_infers_semantic_equivalence:true,
       steps,after_exhaustion:exhausted
     },null,2)+"\n");
   }
 });
 it("does not select when candidate captures are unavailable or uninformative",()=>{
   const base=ledger(0,1);
   const duplicate=()=>selectNextJavaScriptApplicationObservation([base,base],[]);
   expect(duplicate).toThrow(/duplicate observation ledger/);
   expect(()=>selectNextJavaScriptApplicationObservation([base],["probe-0","probe-0"]))
     .toThrow(/duplicate observed context/);
   const empty=selectNextJavaScriptApplicationObservation([],[]);
   expect(empty.status).toBe("no-new-witness");
   const onlyAgree={...base,left:base.left.filter(o=>o.contextId==="baseline-all-equal"),
     right:base.right.filter(o=>o.contextId==="baseline-all-equal")};
   const agreement=selectNextJavaScriptApplicationObservation([onlyAgree],[]);
   expect(agreement.status).toBe("no-new-witness");
   const missing={...base,left:base.left.filter(o=>o.contextId==="probe-0"),
     right:[]};
   expect(selectNextJavaScriptApplicationObservation([missing],[]).status)
     .toBe("no-new-witness");
   const mixed={...base,left:base.left.filter(o=>o.contextId==="probe-0"),
     right:base.right.filter(o=>o.contextId==="probe-0").map(o=>({...o,inputDigest:hash("unrelated")}))};
   expect(selectNextJavaScriptApplicationObservation([mixed],[]).status)
     .toBe("no-new-witness");
 });
});
