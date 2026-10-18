/** Fixture driver: a fresh OS process is used for every checkpoint event. */
import {createHash} from "node:crypto";
import {runInNewContext} from "node:vm";
import {parse} from "@babel/parser";
import {artifactEvidence,fixtureNode} from "./javascriptApplicationGraph.fixture.js";
import {fingerprintJavaScriptAst} from "./javascriptAstFingerprint.js";
import {matchJavaScriptApplicationVersions,
  type ApplicationVersionInputObservation} from "./javascriptApplicationVersionKeys.js";
import {
  initializeJavaScriptInvestigationCheckpoint,
  readJavaScriptInvestigationCheckpoint,
  transactJavaScriptInvestigationCheckpoint
} from "./javascriptInvestigationCheckpoint.js";

const sha=(s:string)=>createHash("sha256").update(s).digest("hex");
const program=(mask:number)=>{
 const elements=Array.from({length:4},(_,i)=>((mask&(1<<i))?"b":"a")+"["+i+"]");
 return "function pick(a,b){return ["+elements.join(",")+"];}";
};
const node=(s:string,side:"left"|"right")=>{
 const artifact=(side==="left"?"a":"b").repeat(64);
 return fixtureNode("javascript-module",{
   strategy:"canonical-path",stability:"artifact-version",
   artifact_sha256:artifact,path:side+".js"
 },side+".js",{
   source_sha256:sha(s),
   structural_fingerprint_sha256:fingerprintJavaScriptAst(parse(s)),
   structural_fingerprint_algorithm:"babel-ast-v3"
 },artifactEvidence(artifact,side+".js"));
};
function evaluate(s:string,id:string,vectors:readonly [readonly number[], readonly number[]])
  :ApplicationVersionInputObservation{
 const arg=JSON.stringify(vectors);
 const value:unknown=runInNewContext(s+";pick(..."+arg+")",{}, {timeout:1000});
 return {contextId:id,inputDigest:sha(arg),
   result:{status:"returned",canonicalValue:JSON.stringify(value)}};
}
const [cmd,location,p1,p2,p3] = process.argv.slice(2);
if (!cmd || !location) throw new Error("Expected command and checkpoint path");
let result;
if (cmd === "init") {
 const a=Number(p1),b=Number(p2);
 if (!Number.isInteger(a)||!Number.isInteger(b)||a<0||a>15||b<0||b>15)
   throw new Error("Fixture masks must be 0..15");
 const left=program(a),right=program(b);
 const matching=matchJavaScriptApplicationVersions([node(left,"left")],[node(right,"right")]);
 if (matching.pairs.length!==1) throw new Error("Native REA matching failed");
 const zero=[[0,0,0,0],[0,0,0,0]] as const;
 result=initializeJavaScriptInvestigationCheckpoint(location,"case-"+a+"-"+b,
   matching.pairs[0]!,left,right,[evaluate(left,"baseline",zero)],
   [evaluate(right,"baseline",zero)],["baseline"]);
} else if(cmd==="read") {
 result=readJavaScriptInvestigationCheckpoint(location);
} else if(cmd==="advance") {
 if (!p1) throw new Error("advance event ID missing");
 result=transactJavaScriptInvestigationCheckpoint(location,
   {kind:"advance",eventId:p1});
} else if(cmd==="capture-left"||cmd==="capture-right"){
 if(!p1)throw new Error("capture event ID missing");
 const state=readJavaScriptInvestigationCheckpoint(location);
 if(!state.pending || !state.pending.contextId || !state.pending.inputVectors)
   throw new Error("No pending source proposal");
 const side=cmd==="capture-left"?"left":"right";
 const observation=evaluate(
   side==="left"?state.leftSource:state.rightSource,
   state.pending.contextId,state.pending.inputVectors,
 );
 const input=p2==="wrong-digest"?{...observation,inputDigest:sha("invalid")}:observation;
 result=transactJavaScriptInvestigationCheckpoint(location,{
   kind:"capture",eventId:p1,side,observation:input
 });
} else if(cmd==="unknown-event") {
 if(!p1)throw new Error("event ID missing");
 result=transactJavaScriptInvestigationCheckpoint(location,{kind:"advance",eventId:p1});
} else throw new Error("Unsupported fixture command "+cmd);
process.stdout.write(JSON.stringify({
  pid:process.pid,revision:result.revision,status:result.status,
  pendingContext:result.pending?.contextId??null,
  accepted:result.acceptedContextIds,
  leftCount:result.left.length,rightCount:result.right.length,
  eventCount:result.events.length,checksum:result.checksum
})+"\n");
