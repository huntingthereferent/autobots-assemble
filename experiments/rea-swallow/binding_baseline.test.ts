import { parse } from "@babel/parser";
import { describe, it, expect } from "vitest";
import { fingerprintJavaScriptAst } from "./javascriptAstFingerprint.js";

describe("REA v3 baseline: the reference identity information lost", () => {
  it("has the same fingerprint for all 16 four-position parameter reference choices", () => {
    const hashes = [];
    for (let choice=0;choice<16;choice++) {
      const values=Array.from({length:4},(_,i)=>(choice&(1<<i)) ? "b" : "a");
      hashes.push(fingerprintJavaScriptAst(parse("function select(a,b){return ["+values.join(",")+"];}")));
    }
    expect(new Set(hashes).size).toBe(1);
  });
});
