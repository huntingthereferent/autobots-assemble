import { mkdirSync, writeFileSync } from "node:fs";
import { dirname } from "node:path";
import { describe, expect, it } from "vitest";
import { matchJavaScriptApplicationVersions } from "./javascriptApplicationVersionKeys.js";
import type { ApplicationNode } from "./javascriptApplicationGraphSchemas.js";

const kinds = ["javascript-module", "source-module", "package", "endpoint", "unknown"] as const;
const h = (i: number) => i.toString(16).padStart(64,"0");

function makeNode(seed: number, i: number, side: number): ApplicationNode {
  const kind = kinds[(seed + i * 3 + side) % kinds.length]!;
  const group = (i * 7 + Math.floor(seed/3) + (side * (seed % 4))) % 6;
  const sameId = (seed % 5 === 0);
  const node_id = (sameId ? "shared-" : side === 0 ? "L-" : "R-") + i;
  const mode = (seed + i + side) % 3;
  const identity = mode === 0 ? { strategy:"content-digest", sha256:h(group + 1) }
    : mode === 1 ? { strategy:"source-map-original", source_root:"root" + (group % 2), original_source:"a"+group+".js" }
    : { strategy:"canonical-path", path:"/src/" + group + ".js" };
  const properties = {
    source_sha256:h(group+1),
    structural_fingerprint_sha256:h(group % 3+1),
    structural_fingerprint_algorithm:"fixture",
    name:"package"+group, value:"url"+group,endpoint_kind:"fetch",
    path:"/src/" + group + ".js"
  };
  return {
    kind, node_id, identity, observations:[{properties,label:"node"+group}]
  } as unknown as ApplicationNode;
}
function pairsToOutput(left: ApplicationNode[], right: ApplicationNode[]) {
  const x=matchJavaScriptApplicationVersions(left,right);
  const leftCandidates=[...x.candidatesForLeft].map(([id,vals])=>[id,vals]);
  const rightCandidates=[...x.candidatesForRight].map(([id,vals])=>[id,vals]);
  for(const [l,rs] of leftCandidates) {
    for(const r of rs as string[]) {
      const reciprocal=x.candidatesForRight.get(r);
      expect(reciprocal).toContain(l);
      expect(x.pairs.find(p=>p.left.node_id===l)).toBeUndefined();
    }
  }
  for(const [r,ls] of rightCandidates) for(const l of ls as string[]) {
    expect(x.candidatesForLeft.get(l)).toContain(r);
    expect(x.pairs.find(p=>p.right.node_id===r)).toBeUndefined();
  }
  expect(x.pairs.length+x.unmatchedLeft.length).toBe(left.length);
  expect(x.pairs.length+x.unmatchedRight.length).toBe(right.length);
  return {
    pairs:x.pairs.map(p=>({left:p.left.node_id,right:p.right.node_id,
      basis:p.basis,confidence:p.confidence})),
    unmatchedLeft:x.unmatchedLeft.map(n=>n.node_id),
    unmatchedRight:x.unmatchedRight.map(n=>n.node_id),
    leftCandidates,rightCandidates
  };
}
describe("REA version-matcher A/B relation transpose",()=>{
  it("preserves 2048 typed synthetic source relation comparisons and inverse candidate sets",()=>{
    const records=[];
    for(let seed=0;seed<512;seed++){
      const countL=seed%7, countR=Math.floor(seed/7)%7;
      const left=Array.from({length:countL},(_,i)=>makeNode(seed,i,0));
      const right=Array.from({length:countR},(_,i)=>makeNode(seed,i,1));
      for(const reverseLeft of [false,true]){
        for(const reverseRight of [false,true]){
          const l=reverseLeft?[...left].reverse():left;
          const r=reverseRight?[...right].reverse():right;
          const outcome=pairsToOutput(l,r);
          records.push({seed,reverseLeft,reverseRight,outcome});
        }
      }
    }
    expect(records.length).toBe(2048);
    const output=process.env.REA_AB_MATCH_OUTPUT;
    if(output){
      mkdirSync(dirname(output),{recursive:true});
      writeFileSync(output,JSON.stringify(records)+"\n");
    }
  });
});
