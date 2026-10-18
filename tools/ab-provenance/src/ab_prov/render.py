"""Self-contained offline SVG provenance explorer; no external CDN or JS packages.

The rendered graph is a *view*, never a source of scientific verification.
Source strings enter the HTML as escaped JSON, and reach DOM via textContent.
"""
from __future__ import annotations
import json

_HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">\n<meta name="visual-template" content="ab_provenance_graph_v1">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>A/B · Relational Provenance</title>
<style>
:root{color-scheme:dark;--bg:#10161b;--panel:#172027;--line:#35434b;--text:#d9e1df;--muted:#98a9ad;--accent:#a7c8bd;--warn:#d8b98c;--danger:#d99e96;font-family: "Segoe UI",Arial,sans-serif}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:14px/1.55 "Segoe UI",Arial,sans-serif}
header{border-bottom:1px solid var(--line);padding:24px 30px;background:#141c22}h1{font-family:Georgia,serif;font-size:27px;letter-spacing:-.02em;font-weight:500;margin:0}h2{font-family:Georgia,serif;font-size:19px;font-weight:500;margin:0 0 12px}
.small{font-size:12px;color:var(--muted)}.eyebrow{font:11px/1.5 Consolas,monospace;letter-spacing:.13em;color:var(--accent);text-transform:uppercase}
.metrics{display:flex;gap:25px;flex-wrap:wrap;margin-top:12px;font:12px Consolas,monospace;color:var(--muted)}.metrics strong{color:var(--text);font-weight:normal}
main{display:grid;grid-template-columns:minmax(450px,1fr) minmax(300px,355px);height:calc(100vh - 140px);min-height:550px}
#surface{overflow:auto;position:relative;border-right:1px solid var(--line)}
.bar{display:flex;gap:12px;align-items:center;flex-wrap:wrap;padding:14px 20px;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:2;background:var(--bg)}
input,select{background:var(--panel);color:var(--text);border:1px solid var(--line);border-radius:3px;padding:8px 10px;max-width:100%}
input{flex:1;min-width:180px}.graph-wrap{overflow:auto;padding:12px;min-height:65vh}
svg{min-width:860px;width:100%;min-height:560px;background:radial-gradient(circle at 12% 20%,#1d2b30 0%,#10161b 44%);border:1px solid #2b353e}
g.node{cursor:pointer}g.node:focus-visible rect{stroke:#fff;stroke-width:3}
.node rect{fill:#1e2a30;stroke:#6c868a;stroke-width:1.2}
.node[data-kind=handoff] rect{stroke:#b2ad8a}.node[data-kind=event] rect{stroke:#9cafa1}
.node[data-kind=evidence_reference] rect{stroke:#88a6bd}.node[data-kind=unresolved] rect{stroke:var(--danger)}
.node text{fill:#dce2e3;font:12px Consolas,monospace;pointer-events:none}
.node .kind{fill:#97abae;font-size:9px;text-transform:uppercase}.node.dim{opacity:.17}
line.link{stroke:#698087;stroke-width:1.5;opacity:.65;cursor:pointer}
line.link[data-state=contested]{stroke:var(--danger);stroke-dasharray:5 4}
line.link[data-state=unresolved]{stroke:var(--warn);stroke-dasharray:3 5}
line.link.dim{opacity:.05}line.link.selected{opacity:1;stroke-width:3}
aside{padding:22px;overflow:auto;background:#151e24}
aside section{border-bottom:1px solid var(--line);padding-bottom:18px;margin-bottom:22px}
pre{font:12px/1.65 Consolas,monospace;white-space:pre-wrap;overflow-wrap:anywhere;background:#10161b;border:1px solid var(--line);padding:12px;border-radius:2px}
.detail{overflow-wrap:anywhere}.detail dt{color:var(--muted);font:11px Consolas,monospace;text-transform:uppercase;margin-top:13px}
.detail dd{margin:4px 0 10px;white-space:pre-wrap;overflow-wrap:anywhere}
ul{padding-left:20px;margin:6px 0}li{margin-bottom:9px}
.note{border-left:2px solid var(--warn);padding-left:12px;color:var(--muted)}
button{font:12px Consolas,monospace;background:#20313a;color:var(--text);border:1px solid var(--line);border-radius:2px;padding:7px 10px;cursor:pointer}
button:hover,button:focus-visible{outline:2px solid var(--accent)}
footer{padding:10px 20px;color:var(--muted);font-size:12px;border-top:1px solid var(--line)}
@media(max-width:900px){main{height:auto;grid-template-columns:1fr}aside{border-top:1px solid var(--line);max-height:500px}#surface{border-right:0}}
</style>
</head>
<body>
<header>
<div class="eyebrow">A/B / Local source projection / Version 0.1</div>
<h1>Relational provenance</h1>
<div class="small">Recorded ancestry, evidence references, and unresolved movement. No inferred proof.</div>
<div id="metrics" class="metrics"></div>
</header>
<main>
<div id="surface">
<div class="bar"><input id="query" type="search" aria-label="Filter referents and relations" placeholder="Filter by referent, relation, or source…"><select id="scope" aria-label="Filter relationship scope"><option value="all">All relationships</option><option value="provenance">Cross-layer provenance</option><option value="trace">Traversal</option><option value="workstation">Workstation</option></select><button id="clear">Reset</button></div>
<div class="graph-wrap"><svg id="map" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Graph of supplied provenance objects and relationships"></svg></div>
</div>
<aside>
<section><h2>Inspection</h2><p id="hint" class="small">Select a referent or relationship to inspect its recorded ancestry and evidence boundary.</p><div id="detail" class="detail"></div></section>
<section><h2>Source record</h2><div id="sources"></div></section>
<section><h2>Unresolved and contested</h2><div id="warnings" class="small"></div></section>
<section class="note">A link, source label, observation, or digest is not an independent verification of its claim. Original native records remain authoritative.</section>
</aside>
</main>
<footer>A/B provenance explorer · standalone read-only projection · local files only</footer>
<script id="ab-graph-data" type="application/json">__AB_GRAPH_DATA__</script>
<script>
"use strict";
const data=JSON.parse(document.getElementById("ab-graph-data").textContent);
const ns="http://www.w3.org/2000/svg";
const svg=document.getElementById("map"), query=document.getElementById("query"),scope=document.getElementById("scope");
const detail=document.getElementById("detail");
const nodes=data.nodes,edges=data.edges;
const byId=new Map(nodes.map(n=>[n.id,n]));
const metrics=document.getElementById("metrics");
function el(tag,cls,txt){const e=document.createElement(tag);if(cls)e.className=cls;if(txt!==undefined)e.textContent=txt;return e;}
function stat(k,v){const e=el("span",null,k+" ");e.append(el("strong",null,String(v)));metrics.append(e);}
stat("Nodes",nodes.length);stat("Relations",edges.length);stat("Open",edges.filter(e=>e.state==="unresolved").length);stat("Contested",edges.filter(e=>e.state==="contested").length);
const kinds=["referent","handoff","event","evidence_reference","unresolved"];
const cols=new Map(kinds.map((k,i)=>[k,120+i*210]));
const loc=new Map();
for(const kind of kinds){
  let index=0;for(const n of nodes.filter(n=>n.kind===kind))loc.set(n.id,{x:cols.get(kind),y:75+index++*72});
}
const height=Math.max(600,...Array.from(loc.values()).map(p=>p.y+75));
svg.setAttribute("viewBox","0 0 1040 "+height);
function svgEl(tag,attrs){let e=document.createElementNS(ns,tag);for(const [k,v]of Object.entries(attrs||{}))e.setAttribute(k,String(v));return e;}
function show(obj){detail.replaceChildren();document.getElementById("hint").textContent=obj?.id||"Source record";
  for(const [k,v]of Object.entries(obj||{})){const dt=el("dt",null,k.replaceAll("_"," ")),dd=el("dd",null,typeof v==="object"?JSON.stringify(v,null,2):String(v));const dl=detail.querySelector("dl")||el("dl");dl.append(dt,dd);detail.append(dl);}
}
const linksGroup=svgEl("g"),nodeGroup=svgEl("g");svg.append(linksGroup,nodeGroup);
const linkItems=[],nodeItems=[];
for(const relation of edges){
  const a=loc.get(relation.from),b=loc.get(relation.to);
  if(!a||!b)continue;const line=svgEl("line",{x1:a.x+65,y1:a.y+17,x2:b.x-65,y2:b.y+17,"class":"link","data-state":relation.state});
  const title=svgEl("title");title.textContent=relation.relation+" · "+relation.state;line.append(title);
  line.addEventListener("click",()=>{document.querySelectorAll(".selected").forEach(e=>e.classList.remove("selected"));line.classList.add("selected");show(relation);});
  linksGroup.append(line);linkItems.push([line,relation]);
}
for(const n of nodes){
  const p=loc.get(n.id);if(!p)continue;
  const g=svgEl("g",{"class":"node","data-kind":n.kind,role:"button",tabindex:"0","aria-label":n.kind+": "+n.label});
  const rect=svgEl("rect",{x:p.x-80,y:p.y-12,width:160,height:54,rx:3});
  const name=svgEl("text",{x:p.x-72,y:p.y+11});name.textContent=n.label.length>22?n.label.slice(0,21)+"…":n.label;
  const kind=svgEl("text",{x:p.x-72,y:p.y+28,"class":"kind"});kind.textContent=n.kind.replace("_"," ");
  g.append(rect,name,kind);
  g.addEventListener("click",()=>show(n));g.addEventListener("keydown",e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();show(n);}});
  nodeGroup.append(g);nodeItems.push([g,n]);
}
function filter(){
 const term=query.value.trim().toLowerCase(), s=scope.value;
 const matchedEdges=edges.filter(e=>(s==="all"||s===e.scope)&&(
  !term||[e.id,e.relation,e.scope,e.state,...e.evidence_refs,...e.boundaries,
  byId.get(e.from)?.label||"",byId.get(e.to)?.label||""].join(" ").toLowerCase().includes(term)));
 const accepted=new Set(matchedEdges.map(e=>e.id));
 const matchedNodes=new Set(matchedEdges.flatMap(e=>[e.from,e.to]));
 for(const [e,r]of linkItems)e.classList.toggle("dim",!accepted.has(r.id));
 for(const [e,n]of nodeItems)e.classList.toggle("dim",
   Boolean(term||s!=="all")&&!(matchedNodes.has(n.id)||(s==="all"&&n.label.toLowerCase().includes(term))));
}
query.addEventListener("input",filter);scope.addEventListener("change",filter);
document.getElementById("clear").addEventListener("click",()=>{query.value="";scope.value="all";filter();});
const sources=document.getElementById("sources");
for(const s of data.sources){const block=el("div");block.append(el("div",null,s.name));block.append(el("div","small","SHA-256 "+s.sha256));block.append(el("p","small",s.scope));sources.append(block);}
if(!data.sources.length)sources.textContent="No source files declared.";
const warnings=document.getElementById("warnings");
if(!data.warnings.length)warnings.textContent="No structural warning emitted. This does not prove the claims.";
else{const ul=el("ul");for(const w of data.warnings)ul.append(el("li",null,w));warnings.append(ul);}
</script>
</body></html>
"""

def render_html(graph: dict) -> str:
    # Script-body escaping: no user-supplied </script>, HTML, or JS injection.
    raw = json.dumps(graph, ensure_ascii=True, allow_nan=False, sort_keys=True)
    raw = raw.replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")
    return _HTML.replace("__AB_GRAPH_DATA__", raw)
