import { createHash } from "node:crypto";
import { dirname } from "node:path";
import { mkdirSync, writeFileSync } from "node:fs";
import { runInNewContext } from "node:vm";
import { parse } from "@babel/parser";
import { describe, expect, it } from "vitest";
import { artifactEvidence, fixtureNode } from "./javascriptApplicationGraph.fixture.js";
import { fingerprintJavaScriptAst } from "./javascriptAstFingerprint.js";
import {
  matchJavaScriptApplicationVersions,
  refineJavaScriptApplicationPairByObservations,
  advanceJavaScriptApplicationInvestigation,
  type ApplicationVersionInputObservation,
  type ApplicationVersionConstructedObservation,
  type ApplicationVersionNodePair,
} from "./javascriptApplicationVersionKeys.js";

const digest = (s: string) => createHash("sha256").update(s).digest("hex");
const program = (mask: number): string => {
  const elements = Array.from({length: 4}, (_, i) => ((mask & (1 << i)) ? "b" : "a") + "[" + i + "]");
  return "function pick(a,b){return [" + elements.join(",") + "];}";
};
const source = Array.from({length: 16}, (_, i) => program(i));
const node = (s: string, side: "left"|"right") => {
  const artifact = (side === "left" ? "a" : "b").repeat(64);
  return fixtureNode("javascript-module", {
    strategy: "canonical-path", stability: "artifact-version", artifact_sha256: artifact,
    path: side + ".js",
  }, side + ".js", {
    source_sha256: digest(s),
    structural_fingerprint_sha256: fingerprintJavaScriptAst(parse(s)),
    structural_fingerprint_algorithm: "babel-ast-v3",
  }, artifactEvidence(artifact, side + ".js"));
};
const matched = (left: string, right: string): ApplicationVersionNodePair => {
  const results = matchJavaScriptApplicationVersions(
    [node(left, "left")], [node(right, "right")],
  );
  expect(results.pairs).toHaveLength(1);
  return results.pairs[0]!;
};
const baseline = [[0,0,0,0],[0,0,0,0]] as const;
const observe = (
  s: string, contextId: string,
  input: readonly [readonly number[], readonly number[]],
): ApplicationVersionInputObservation => {
  // Independently evaluate only the finite known pure source family, with timeout.
  const canonicalInput = JSON.stringify(input);
  const returned: unknown = runInNewContext(
    s + ";pick(..." + canonicalInput + ")", {}, {timeout:1000},
  );
  return {contextId, inputDigest: digest(canonicalInput),
    result: {status: "returned", canonicalValue: JSON.stringify(returned)}};
};
function step(
  pair: ApplicationVersionNodePair, l: string, r: string,
  left: ApplicationVersionInputObservation[], right: ApplicationVersionInputObservation[],
  accepted: string[], pending: ApplicationVersionConstructedObservation | null,
) {
  return advanceJavaScriptApplicationInvestigation(
    pair, l, r, left, right, accepted, pending,
  );
}

describe("REA A/B integrated event-driven investigation transition", () => {
  it("repeats request, partial observation, complete witness and closure on all 256 REA matches", () => {
    expect(new Set(source.map((s) => fingerprintJavaScriptAst(parse(s)))).size).toBe(1);
    const rows: unknown[] = [];
    let proposals=0, incomplete=0, independentlyWitnessed=0, stillUndetermined=0;
    for (let i=0; i<16; i++) for (let j=0; j<16; j++) {
      const l=source[i]!, r=source[j]!, pair=matched(l,r);
      const baseL=observe(l, "baseline", baseline), baseR=observe(r, "baseline", baseline);
      const left=[baseL], right=[baseR], history=["baseline"];
      const start=step(pair,l,r,left,right,history,null);
      if(i===j) {
        expect(start.status).toBe("undetermined");
        expect(start.request).toBeNull();
        stillUndetermined++;
        continue;
      }
      expect(start.status).toBe("request-independent-capture");
      expect(start.request?.status).toBe("proposed");
      const request=start.request!;
      expect(request.inputVectors).not.toBeNull();
      expect(request.inputDigest).toBe(digest(JSON.stringify(request.inputVectors)));
      expect(request.contextId).toMatch(/^constructed-reference-/u);
      proposals++;
      const pendingL=observe(l,request.contextId!,request.inputVectors!);
      left.push(pendingL);
      const intermediate=step(pair,l,r,left,right,history,request);
      expect(intermediate.status).toBe("awaiting-independent-capture");
      expect(intermediate.acceptedContextIds).toEqual(history);
      expect(intermediate.request).toEqual(request);
      incomplete++;
      const pendingR=observe(r,request.contextId!,request.inputVectors!);
      right.push(pendingR);
      expect(pendingL.result).not.toEqual(pendingR.result);
      const complete=step(pair,l,r,left,right,history,request);
      expect(complete.status).toBe("witnessed-difference");
      expect(complete.selectedContextId).toBe(request.contextId);
      expect(complete.acceptedContextIds).toEqual(["baseline",request.contextId]);
      const checked=refineJavaScriptApplicationPairByObservations(
        pair, left, right,
      );
      expect(checked.result).toBe("witnessed-difference");
      const after=step(pair,l,r,left,right,
        [...complete.acceptedContextIds],null);
      expect(after.status).toBe("witnessed-difference");
      expect(after.request).toBeNull();
      expect(after.selectedContextId).toBeNull();
      independentlyWitnessed++;
      rows.push({left:i,right:j,requested:request.contextId,
        differingPosition:request.differentReferencePosition,
        input:request.inputVectors,
        leftResult:pendingL.result,rightResult:pendingR.result,
        transitions:[start.status,intermediate.status,complete.status,after.status]});
    }
    expect(proposals).toBe(240);
    expect(incomplete).toBe(240);
    expect(independentlyWitnessed).toBe(240);
    expect(stillUndetermined).toBe(16);
    const output=process.env.REA_AB_ADVANCE_OUTPUT;
    if(output) {
      mkdirSync(dirname(output),{recursive:true});
      writeFileSync(output,JSON.stringify({
        pinnedUpstream:"f0b9ef34c404c1c65f8167502db972b0bd708403",
        source:"native REA matcher, source-derived input construction and selector",
        pairs:256,constructed:proposals,partialAwaited:incomplete,
        independentRuntimeDifferences:independentlyWitnessed,
        unresolvedSelfPairs:stillUndetermined,
        execution:"finite authored fixtures evaluated by separate Node VM harness, not REA production",
        generalAutonomyProven:false,semanticEquivalenceClaim:false,
        trace:rows,
      })+"\n");
    }
  });
  it("uses already captured separating evidence before constructing a new input", () => {
    const l=source[0]!,r=source[1]!,pair=matched(l,r);
    const history=["baseline"];
    const extra=[[0,0,0,0],[7,0,0,0]] as const;
    const left=[observe(l,"baseline",baseline),observe(l,"external-captured",extra)];
    const right=[observe(r,"baseline",baseline),observe(r,"external-captured",extra)];
    const advance=step(pair,l,r,left,right,history,null);
    expect(advance.status).toBe("witnessed-difference");
    expect(advance.request).toBeNull();
    expect(advance.selectedContextId).toBe("external-captured");
    expect(advance.acceptedContextIds).toEqual(["baseline","external-captured"]);
  });
  it("preserves pending context on partial or mismatched evidence; rejects fabricated requests",()=>{
    const l=source[0]!,r=source[1]!,pair=matched(l,r);
    const left=[observe(l,"baseline",baseline)],right=[observe(r,"baseline",baseline)];
    const request=step(pair,l,r,left,right,["baseline"],null).request!;
    expect(request.status).toBe("proposed");
    const pendingLeft=observe(l,request.contextId!,request.inputVectors!);
    const partial=step(pair,l,r,[...left,pendingLeft],right,["baseline"],request);
    expect(partial.status).toBe("awaiting-independent-capture");
    const mismatchedR={...observe(r,request.contextId!,request.inputVectors!),
      inputDigest:digest("different-input")};
    const blocked=step(pair,l,r,[...left,pendingLeft],
      [...right,mismatchedR],["baseline"],request);
    expect(blocked.status).toBe("blocked-evidence");
    expect(blocked.request).toEqual(request);
    expect(blocked.acceptedContextIds).toEqual(["baseline"]);
    const unknownR={...observe(r,request.contextId!,request.inputVectors!),
      result:{status:"unknown" as const,reason:"capture failed"}};
    expect(step(pair,l,r,[...left,pendingLeft],
      [...right,unknownR],["baseline"],request).status).toBe("awaiting-independent-capture");
    expect(()=>step(pair,l,r,left,right,["baseline"],{
      ...request,inputDigest:digest("forged-input"),
    })).toThrow(/not source-derived/);
    expect(()=>step(pair,l,r,left,right,["baseline","baseline"],null))
      .toThrow(/duplicated accepted/);
    expect(()=>step(pair,l,r,[...left,left[0]!],right,["baseline"],null))
      .toThrow(/duplicate observation context/);
  });
  it("does not invent a repeat move when source is unsupported",()=>{
    const l=source[0]!,r=source[0]!,pair=matched(l,r);
    const a=[observe(l,"baseline",baseline)],b=[observe(r,"baseline",baseline)];
    expect(step(pair,l,r,a,b,["baseline"],null).status).toBe("undetermined");
    expect(step(pair,l,r,a,b,["baseline"],null).request).toBeNull();
    expect(step(pair,l,r,a,b,[],null).status).toBe("undetermined");
  });
});
