import { mkdirSync, writeFileSync } from "node:fs";
import { dirname } from "node:path";
import { describe, expect, it } from "vitest";
import { traverseApplicationFeature } from "./javascriptFeatureTraversal.js";
import type { JavaScriptApplicationGraph } from "./javascriptApplicationGraph.js";
type Edge = { edge_id: string; source_node_id: string; target_node_id: string };
type Dir = "outgoing" | "incoming" | "both";
const ids = ["a", "b", "c"] as const;
const choices: Edge[] = ids.flatMap(a => ids.filter(b => a !== b).map(b =>
  ({ edge_id: "e_"+a+b, source_node_id: a, target_node_id: b })));
function closure(edges: Edge[], seeds: string[], dir: Dir) {
  const seen = new Set(seeds);
  for (;;) {
    const prior = seen.size;
    for (const e of edges) {
      if (dir !== "incoming" && seen.has(e.source_node_id)) seen.add(e.target_node_id);
      if (dir !== "outgoing" && seen.has(e.target_node_id)) seen.add(e.source_node_id);
    }
    if (prior === seen.size) return [...seen].sort();
  }
}
describe("swallowed REA source relation mathematics", () => {
  it("preserves exact reachable nodes, edges and witnesses", () => {
    const rows = [];
    for (let g=0;g<64;g++) {
      const edges = choices.filter((_,i)=>(g&(1<<i))!==0);
      const graph = {nodes: ids.map(node_id=>({node_id})),edges} as unknown as JavaScriptApplicationGraph;
      for(let s=0;s<8;s++) for(const reverse of [false,true]) {
        const raw = ids.filter((_,i)=>(s&(1<<i))!==0);
        const seeds = reverse ? [...raw].reverse() : [...raw];
        for(const dir of ["outgoing","incoming","both"] as const) {
          const actual = traverseApplicationFeature(graph,seeds,dir);
          const reached = closure(edges,seeds,dir);
          expect(actual.nodes.map(n=>n.node_id)).toEqual(reached);
          expect(actual.edges.map(e=>e.edge_id)).toEqual(edges.filter(e=>
            (dir!=="incoming"&&reached.includes(e.source_node_id)) ||
            (dir!=="outgoing"&&reached.includes(e.target_node_id))
          ).map(e=>e.edge_id).sort());
          for(const id of reached) {
            if(seeds.includes(id)) { expect(actual.predecessors.has(id)).toBe(false); continue; }
            const pred = actual.predecessors.get(id);
            expect(pred).toBeDefined();
            const edge = edges.find(e=>e.edge_id===pred!.edgeId);
            expect(edge).toBeDefined();
            const forward = edge!.source_node_id===pred!.previousNodeId&&edge!.target_node_id===id;
            const back = edge!.target_node_id===pred!.previousNodeId&&edge!.source_node_id===id;
            expect((dir!=="incoming"&&forward)||(dir!=="outgoing"&&back)).toBe(true);
          }
          rows.push({g,s,reverse,dir,nodes:actual.nodes.map(n=>n.node_id),
            edges:actual.edges.map(e=>e.edge_id),
            predecessors:[...actual.predecessors.entries()].sort(([a],[b])=>a.localeCompare(b))});
        }
      }
    }
    expect(rows).toHaveLength(3072);
    const out=process.env.REA_AB_OUTPUT;
    if(out){mkdirSync(dirname(out),{recursive:true});writeFileSync(out,JSON.stringify(rows)+"\n");}
  });
});
