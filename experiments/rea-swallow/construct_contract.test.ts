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
  constructNextJavaScriptApplicationObservation,
  type ApplicationVersionInputObservation
} from "./javascriptApplicationVersionKeys.js";

const hash=(source:string)=>createHash("sha256").update(source).digest("hex");
const sourceFor=(mask:number)=>{
 const refs=Array.from({length:4},(_,i)=>((mask&(1<<i))?"b":"a")+"["+i+"]");
 return "function pick(a,b){return ["+refs.join(",")+"];}";
};
const moduleNode=(source:string,side:"left"|"right")=>{
 const artifact=(side==="left"?"a":"b").repeat(64);
 return fixtureNode("javascript-module",{
    strategy:"canonical-path",stability:"artifact-version",artifact_sha256:artifact,path:side+".js"
 },side+".js",{
    source_sha256:hash(source),
    structural_fingerprint_sha256:fingerprintJavaScriptAst(parse(source)),
    structural_fingerprint_algorithm:"babel-ast-v3"
 },artifactEvidence(artifact,side+".js"));
};
const baselineArgs=[[0,0,0,0],[0,0,0,0]] as const;
function externalWitness(
  source:string,contextId:string, vectors:readonly [readonly number[],readonly number[]]
):ApplicationVersionInputObservation{
 const encoded=JSON.stringify(vectors);
 // Independently execute only this bounded, authored family in a timeout VM.
 const result:unknown=runInNewContext(source+";pick(..."+encoded+")",{}, {timeout:1000});
 return {contextId,inputDigest:hash(encoded),result:{
   status:"returned",canonicalValue:JSON.stringify(result)
 }};
}
describe("REA Movement 10: new observation constructed from unresolved source relations",()=>{
 it("generates fresh inputs and independently verifies 240 new separation witnesses",()=>{
  const source=Array.from({length:16},(_,i)=>sourceFor(i));
  expect(new Set(source.map(s=>fingerprintJavaScriptAst(parse(s)))).size).toBe(1);
  const rows=[];
  let constructed=0,verified=0,exhausted=0;
  for(let i=0;i<16;i++) for(let j=0;j<16;j++){
    const matched=matchJavaScriptApplicationVersions([moduleNode(source[i]!,"left")],
      [moduleNode(source[j]!,"right")]);
    expect(matched.pairs).toHaveLength(1);
    const pair=matched.pairs[0]!;
    expect(pair).toMatchObject(i===j?{
      basis:"exact-module-source-digest",confidence:"exact"
    }:{basis:"structural-fingerprint",confidence:"medium"});
    const baseL=externalWitness(source[i]!,"baseline",baselineArgs);
    const baseR=externalWitness(source[j]!,"baseline",baselineArgs);
    expect(refineJavaScriptApplicationPairByObservations(pair,[baseL],[baseR]).result)
      .toBe("undetermined");
    const proposal=constructNextJavaScriptApplicationObservation(
      pair,source[i]!,source[j]!,[baseL],[baseR]);
    const expectedPosition=Array.from({length:4},(_,k)=>k).find(k=>
      ((i>>k)&1)!==((j>>k)&1));
    if(i===j){
      expect(proposal.status).toBe("unsupported-or-exhausted");
      expect(proposal.contextId).toBeNull();
      exhausted++;
      continue;
    }
    expect(proposal.status).toBe("proposed");
    expect(proposal.differentReferencePosition).toBe(expectedPosition);
    expect(proposal.inputVectors).not.toBeNull();
    expect(proposal.inputDigest).toBe(hash(JSON.stringify(proposal.inputVectors)));
    constructed++;
    const generatedL=externalWitness(source[i]!,proposal.contextId!,proposal.inputVectors!);
    const generatedR=externalWitness(source[j]!,proposal.contextId!,proposal.inputVectors!);
    const refined=refineJavaScriptApplicationPairByObservations(pair,
      [baseL,generatedL],[baseR,generatedR]);
    expect(refined.result).toBe("witnessed-difference");
    expect(refined.separatingContextIds).toEqual([proposal.contextId]);
    expect(generatedL.result).not.toEqual(generatedR.result);
    const independentlyExpectedLeft=((i>>proposal.differentReferencePosition!)&1)?7:0;
    const independentlyExpectedRight=((j>>proposal.differentReferencePosition!)&1)?7:0;
    const actualLeft=JSON.parse(generatedL.result.status==="returned"?generatedL.result.canonicalValue:"null");
    const actualRight=JSON.parse(generatedR.result.status==="returned"?generatedR.result.canonicalValue:"null");
    expect(actualLeft[proposal.differentReferencePosition!]).toBe(independentlyExpectedLeft);
    expect(actualRight[proposal.differentReferencePosition!]).toBe(independentlyExpectedRight);
    expect(constructNextJavaScriptApplicationObservation(pair,source[i]!,source[j]!,
      [baseL,generatedL],[baseR,generatedR]).status).toBe("unsupported-or-exhausted");
    verified++;
    rows.push({left:i,right:j,context:proposal.contextId,
      differing_slot:proposal.differentReferencePosition,input:proposal.inputVectors,
      observed_left:actualLeft,observed_right:actualRight});
  }
  expect(constructed).toBe(240);
  expect(verified).toBe(240);
  expect(exhausted).toBe(16);
  const path=process.env.REA_AB_CONSTRUCTION_OUTPUT;
  if(path) {
    mkdirSync(dirname(path),{recursive:true});
    writeFileSync(path,JSON.stringify({
      genuine_rea_upstream:"f0b9ef34c404c1c65f8167502db972b0bd708403",
      source_operator:"constructNextJavaScriptApplicationObservation",
      input_evaluation:"independent bounded authored fixture; not REA production runtime",
      family:"two array parameters, pure return of four indexed direct accesses",
      matched_pairs:256,proposed_new_inputs:constructed,
      independently_witnessed_differences:verified,unresolved_same_source_pairs:exhausted,
      universal_equivalence_claim:false,rows
    })+"\n");
  }
 });
 it("fails closed on unsupported source and mismatched source provenance",()=>{
  const l=sourceFor(0),r=sourceFor(1);
  const pair=matchJavaScriptApplicationVersions([moduleNode(l,"left")],
    [moduleNode(r,"right")]).pairs[0]!;
  const baselineL=externalWitness(l,"baseline",baselineArgs);
  const baselineR=externalWitness(r,"baseline",baselineArgs);
  for(const changed of [
    "function pick(a,b){return [a[0],b[1],a[2],b[3]];}",
    "function pick(a,b){while(true){}return [a[0],a[1],a[2],a[3]];}",
    "function pick(a,b){return [a[0],a[1],a[2],b[x]];}",
    "function pick(a,b){return a;}",
    "function pick(a,b){return [a[1],a[1],a[2],b[3]];}",
    "function pick(a,b){return [a[0],a[1],a[2],b[3]]; sideEffect();",
  ]){
    expect(constructNextJavaScriptApplicationObservation(pair,changed,r,
      [baselineL],[baselineR]).status).toBe("unsupported-or-exhausted");
  }
  expect(constructNextJavaScriptApplicationObservation(pair,r,l,[baselineL],[baselineR]).status)
    .toBe("unsupported-or-exhausted");
  const proposal=constructNextJavaScriptApplicationObservation(pair,l,r,[baselineL],[baselineR]);
  expect(proposal.status).toBe("proposed");
  expect(constructNextJavaScriptApplicationObservation(pair,l,r,[
    baselineL,{contextId:proposal.contextId!,inputDigest:proposal.inputDigest!,
      result:{status:"unknown",reason:"not executed"}}
  ],[baselineR]).status).toBe("unsupported-or-exhausted");
 });
});
