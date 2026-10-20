import { createHash } from "node:crypto";
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname } from "node:path";
import { runInNewContext } from "node:vm";
import { parse } from "@babel/parser";
import { describe, expect, it } from "vitest";

import { fingerprintJavaScriptAst } from "./javascriptAstFingerprint.js";
import { artifactEvidence, completeCoverage, fixtureNode } from "./javascriptApplicationGraph.fixture.js";
import { createJavaScriptApplicationGraph } from "./javascriptApplicationGraph.js";
import { compareJavaScriptApplicationVersions } from "./javascriptApplicationVersionComparison.js";
import { matchJavaScriptApplicationVersions } from "./javascriptApplicationVersionKeys.js";

const sha = (source: string) => createHash("sha256").update(source).digest("hex");

const cases = [
  {
    case_id: "A-consistent-rename",
    change: "consistent parameter renaming only",
    original: "function pick(a,b){return a;}",
    changed: "function pick(left,right){return left;}",
    call: "pick(11,29)",
    expected_same_behavior: true,
  },
  {
    case_id: "B-reference-redirect",
    change: "return second parameter instead of first",
    original: "function pick(a,b){return a;}",
    changed: "function pick(a,b){return b;}",
    call: "pick(11,29)",
    expected_same_behavior: false,
  },
  {
    case_id: "B-subtraction-order",
    change: "swap operand identities without changing syntax shape",
    original: "function calc(a,b){return a-b;}",
    changed: "function calc(a,b){return b-a;}",
    call: "calc(11,29)",
    expected_same_behavior: false,
  },
  {
    case_id: "B-predicate-selection",
    change: "switch which argument controls a conditional",
    original: "function choose(a,b){return a ? 1 : 2;}",
    changed: "function choose(a,b){return b ? 1 : 2;}",
    call: "choose(true,false)",
    expected_same_behavior: false,
  },
  {
    case_id: "B-local-data-dependency",
    change: "change which parameter initializes the returned local",
    original: "function pick(a,b){const result=a;return result;}",
    changed: "function pick(a,b){const result=b;return result;}",
    call: "pick(11,29)",
    expected_same_behavior: false,
  },
] as const;

const nodeFor = (source: string, position: "left" | "right") => {
  const artifact = position === "left" ? "a".repeat(64) : "b".repeat(64);
  const path = position + ".js";
  return fixtureNode(
    "javascript-module",
    {
      strategy: "canonical-path",
      stability: "artifact-version",
      artifact_sha256: artifact,
      path,
    },
    path,
    {
      source_sha256: sha(source),
      structural_fingerprint_sha256: fingerprintJavaScriptAst(parse(source)),
      structural_fingerprint_algorithm: "babel-ast-v3",
    },
    artifactEvidence(artifact, path),
  );
};

function compare(original: string, changed: string) {
  const left = nodeFor(original, "left");
  const right = nodeFor(changed, "right");
  const matching = matchJavaScriptApplicationVersions([left], [right]);
  const graph = (node: typeof left) => createJavaScriptApplicationGraph({
    schema: "JavaScriptApplicationGraph",
    root_node_ids: [node.node_id],
    nodes: [node],
    edges: [],
    coverage: completeCoverage,
    limitations: [],
  });
  const comparison = compareJavaScriptApplicationVersions({
    left: { evidenceId: "ev_" + "1".repeat(64), rootArtifactSha256: "a".repeat(64), graph: graph(left) },
    right: { evidenceId: "ev_" + "2".repeat(64), rootArtifactSha256: "b".repeat(64), graph: graph(right) },
    leftNativeEvidence: [],
    rightNativeEvidence: [],
  });
  return { left, right, matching, comparison };
}

describe("REA A/B structural language-reference counterexamples", () => {
  it("finds which source movements erase different binding meanings under the same fingerprint", () => {
    const receipts = [];
    let witnessedChangedBehavior = 0;
    for (const item of cases) {
      const originalFingerprint = fingerprintJavaScriptAst(parse(item.original));
      const changedFingerprint = fingerprintJavaScriptAst(parse(item.changed));
      const leftDigest = sha(item.original);
      const rightDigest = sha(item.changed);
      expect(leftDigest).not.toBe(rightDigest);
      expect(originalFingerprint).toBe(changedFingerprint);
      // These are authored, fixed, deterministic fixtures, not arbitrary external code.
      const originalResult = runInNewContext(item.original + "\n" + item.call, {}, { timeout: 1000 });
      const changedResult = runInNewContext(item.changed + "\n" + item.call, {}, { timeout: 1000 });
      const sameBehaviorOnWitness = Object.is(originalResult, changedResult);
      expect(sameBehaviorOnWitness).toBe(item.expected_same_behavior);
      if (!sameBehaviorOnWitness) witnessedChangedBehavior++;
      const matched = compare(item.original, item.changed);
      expect(matched.matching.pairs).toHaveLength(1);
      expect(matched.matching.pairs[0]).toMatchObject({
        basis: "structural-fingerprint",
        confidence: "medium",
      });
      const comparisonItem = matched.comparison.items.find(i=>i.left_node_id===matched.left.node_id);
      expect(comparisonItem).toMatchObject({
        status: "changed",
        dimensions: expect.arrayContaining(["content"]),
        match: { basis: "structural-fingerprint", confidence: "medium" },
      });
      expect(comparisonItem?.limitations.join(" ")).toContain("not byte identity or proof of semantic equivalence");
      receipts.push({
        case_id: item.case_id,
        change: item.change,
        original_source_sha256: leftDigest,
        changed_source_sha256: rightDigest,
        structural_fingerprint_sha256: originalFingerprint,
        same_fingerprint: originalFingerprint === changedFingerprint,
        witness_call: item.call,
        original_result: originalResult,
        changed_result: changedResult,
        same_behavior_on_witness: sameBehaviorOnWitness,
        rea_pairing_basis: matched.matching.pairs[0]?.basis,
        rea_pairing_confidence: matched.matching.pairs[0]?.confidence,
        rea_item_status: comparisonItem?.status,
        rea_item_limitations: comparisonItem?.limitations,
      });
    }
    expect(receipts).toHaveLength(5);
    expect(witnessedChangedBehavior).toBe(4);
    const path = process.env.REA_AB_STRUCTURAL_OUTPUT;
    if (path) {
      mkdirSync(dirname(path), {recursive:true});
      writeFileSync(path, JSON.stringify({
        observation: "Structural fingerprint preserves syntax type/operator/literal sequence but not parameter-reference equality",
        intended_preserving_A_examples: 1,
        distinct_behavior_B_witnesses: witnessedChangedBehavior,
        does_rea_claim_semantic_equivalence: false,
        cases: receipts,
      }, null, 2)+"\n");
    }
  });
});
