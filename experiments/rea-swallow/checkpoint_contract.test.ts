import {spawnSync} from "node:child_process";
import {mkdtempSync,readFileSync,writeFileSync,existsSync,unlinkSync,rmSync} from "node:fs";
import {tmpdir} from "node:os";
import {join} from "node:path";
import {fileURLToPath} from "node:url";
import {describe,it,expect} from "vitest";
const cli=fileURLToPath(new URL("./javascriptCheckpointCLI.ab-swallow.ts", import.meta.url));
type Snapshot={
 pid:number;revision:number;status:string;pendingContext:string|null;
 accepted:string[];leftCount:number;rightCount:number;
 eventCount:number;checksum:string;
};
function invoke(command:string,path:string,...args:string[]):Snapshot {
 const response=spawnSync(process.execPath,["--import","tsx",cli,command,path,...args],{
   encoding:"utf8",timeout:18000,env:{...process.env,NODE_NO_WARNINGS:"1"}
 });
 if(response.status!==0)throw new Error("CLI failed: "+command+" "+response.stderr+" "+response.stdout);
 return JSON.parse(response.stdout.trim()) as Snapshot;
}
function reject(command:string,path:string,...args:string[]){
 const response=spawnSync(process.execPath,["--import","tsx",cli,command,path,...args],{
   encoding:"utf8",timeout:18000,env:{...process.env,NODE_NO_WARNINGS:"1"}
 });
 expect(response.status).not.toBe(0);
}
describe("REAL REA checkpoint across fresh OS processes",()=>{
 it("recovers after one-sided capture and closes once, without duplicate progression",()=>{
  const root=mkdtempSync(join(tmpdir(),"rea-resume-"));
  try {
   const path=join(root,"checkpoint.json");
   const trace=[];
   const start=invoke("init",path,"0","1");
   expect(start).toMatchObject({revision:0,status:"undetermined",eventCount:0,
     leftCount:1,rightCount:1,pendingContext:null});
   trace.push(start);
   const proposed=invoke("advance",path,"move-1");
   expect(proposed).toMatchObject({revision:1,status:"request-independent-capture",
     eventCount:1});
   expect(proposed.pendingContext).toMatch(/^constructed-reference-/u);
   trace.push(proposed);
   // A new Node PID for the next event models the crashed/terminated driver.
   const left=invoke("capture-left",path,"capture-L");
   expect(left).toMatchObject({revision:2,status:"awaiting-independent-capture",
     leftCount:2,rightCount:1,eventCount:2});
   expect(left.pendingContext).toBe(proposed.pendingContext);
   expect(left.pid).not.toBe(proposed.pid);
   trace.push(left);
   // Reopened after restart with no in-memory state from the old driver.
   const resumed=invoke("read",path);
   expect(resumed).toMatchObject({revision:2,status:"awaiting-independent-capture"});
   expect(resumed.checksum).toBe(left.checksum);
   const redundant=invoke("advance",path,"resume-check");
   expect(redundant.status).toBe("awaiting-independent-capture");
   expect(redundant.pendingContext).toBe(proposed.pendingContext);
   trace.push(redundant);
   const beforeWrong=invoke("read",path);
   reject("capture-right",path,"bad-R","wrong-digest");
   expect(invoke("read",path).checksum).toBe(beforeWrong.checksum);
   const right=invoke("capture-right",path,"capture-R");
   expect(right).toMatchObject({status:"witnessed-difference",
     leftCount:2,rightCount:2,pendingContext:null});
   expect(right.accepted).toEqual(["baseline",proposed.pendingContext]);
   trace.push(right);
   const replay=invoke("advance",path,"move-1");
   expect(replay).toMatchObject({revision:right.revision,status:"witnessed-difference"});
   expect(replay.checksum).toBe(right.checksum);
   const noNew=invoke("advance",path,"extra-advance");
   expect(noNew.revision).toBe(right.revision);
   reject("capture-right",path,"capture-different");
   const stored=JSON.parse(readFileSync(path,"utf8")) as {
     revision:number;events:unknown[];checksum:string
   };
   expect(stored.revision).toBe(right.revision);
   expect(stored.events).toHaveLength(right.eventCount);
   const output=process.env.REA_AB_RESTART_OUTPUT;
   if(output)writeFileSync(output,JSON.stringify({
     source:"actual REA experimental TypeScript module",
     independentProcessPids:trace.map(x=>x.pid),
     stepStatuses:trace.map(x=>x.status),
     originalProposal:proposed.pendingContext,
     persistedLeftCapture:left.checksum===resumed.checksum,
     finalRevision:right.revision,terminalIdempotence:replay.checksum===right.checksum,
     witnessed:true,trace
   },null,2)+"\n");
  } finally {rmSync(root,{recursive:true,force:true});}
 });
 it("preserves unresolved same-source relation and does not invent a new event",()=>{
  const root=mkdtempSync(join(tmpdir(),"rea-exhausted-"));
  try{
    const path=join(root,"checkpoint.json");
    const baseline=invoke("init",path,"0","0");
    const n=invoke("advance",path,"no-new");
    expect(n).toMatchObject({status:"undetermined",revision:0,eventCount:0,
       pendingContext:null});
    expect(baseline.checksum).toBe(n.checksum);
    reject("capture-left",path,"invalid-capture");
    reject("init",path,"0","1");
  }finally{rmSync(root,{recursive:true,force:true});}
 });
 it("detects corruption, stale write locks and conflicting replay IDs",()=>{
  const root=mkdtempSync(join(tmpdir(),"rea-lock-"));
  try{
    const path=join(root,"checkpoint.json");
    invoke("init",path,"0","1");
    const before=invoke("advance",path,"move-1");
    reject("capture-left",path,"move-1"); // duplicate event ID of a different kind
    expect(invoke("read",path).checksum).toBe(before.checksum);
    writeFileSync(path+".lock","unrecovered-owner\n");
    reject("capture-left",path,"capture-L"); // fail-closed stale lock, no takeover
    unlinkSync(path+".lock");
    expect(invoke("read",path).checksum).toBe(before.checksum);
    const saved=readFileSync(path,"utf8");
    writeFileSync(path,saved.replace('"revision":1','"revision":999'));
    reject("read",path);
    reject("advance",path,"move-next");
    expect(existsSync(path)).toBe(true);
  }finally{rmSync(root,{recursive:true,force:true});}
 });
});
