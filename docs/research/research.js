"use strict";
/* Tracework Research Instruments - source-referenced, read-only Pages.
   Only documented numerical derivations are computed; source observations are not synthesized. */
(function(){
 const ROOT="https://github.com/huntingthereferent/autobots-assemble";
 const PIN="f08368e5f59a5ca531dd69cd040e43ccf2c2cf12";
 const RAW="https://raw.githubusercontent.com/huntingthereferent/autobots-assemble/"+PIN+"/";
 const PAGE=document.body.dataset.page||"index";
 const $=s=>document.querySelector(s);
 const node=(tag,attrs={},txt)=>{const n=document.createElement(tag);for(const [k,v] of Object.entries(attrs)){if(k==="class")n.className=v;else if(k==="href")n.href=v;else n.setAttribute(k,v);}if(txt!==undefined)n.textContent=String(txt);return n};
 const clear=e=>{if(e)e.replaceChildren()};
 const link=(parent,label,url)=>{const a=node("a",{href:url,target:"_blank",rel:"noopener noreferrer"},label);parent.append(a);return a};
 const set=(id,text)=>{const x=$("#"+id);if(x)x.textContent=text};
 const paths={
  math:[
   ["48-law family and mathematical classification","work/arc_like_maze/WINDOW_COMBINED.md"],
   ["48-law interpreter","work/arc_like_maze/window_combined.py"],
   ["Engine 1 — bounded inverse construction","work/arc_like_maze/ENGINE_ONE.md"],
   ["Engine 1 implementation","work/arc_like_maze/engine_one.py"],
   ["Pointed couplings","work/arc_like_maze/POINTED_COUPLING_CLASSIFICATION.md"],
   ["Cyclic action continuation","work/arc_like_maze/CYCLIC_ACTION_CONTINUATION.md"],
   ["Non-diagonal transport","work/arc_like_maze/NONDIAGONAL_TRANSPORT.md"],
   ["Complete research index","work/arc_like_maze/README.md"],
   ["Focused finite model tests","network/tests/test_arc_like_window_combined.py"]],
  arc:[
   ["ARC native research index","research/arc_native_runs/README.md"],
   ["FT09 local route JSON","research/arc_native_runs/ft09_route.json"],
   ["LS20 local route JSON","research/arc_native_runs/ls20_route.json"],
   ["SK48 local route JSON","research/arc_native_runs/sk48_route.json"],
   ["Native trial notes","research/arc_native_runs/AUTONOMOUS_TRIALS.md"],
   ["Replay of saved routes","research/arc_native_runs/replay_saved_paths.py"],
   ["LS20 original complete replay","research/arc_native_runs/original_ls20_complete_replay.py"],
   ["SK48 original complete replay","research/arc_native_runs/original_sk48_complete_replay.py"]],
  world:[
   ["General construction and scope","work/ab_world/GENERAL_CONSTRUCTION.md"],
   ["Trial 06 — virtual trajectories","work/ab_world/TRIAL06_SOURCE_HANDOFF.md"],
   ["Trial 12 — research handoff","work/ab_world/TRIAL12_SOURCE_HANDOFF.md"],
   ["Trial 18 — research handoff","work/ab_world/TRIAL18_SOURCE_HANDOFF.md"],
   ["Trial 22 — research handoff","work/ab_world/TRIAL22_SOURCE_HANDOFF.md"],
   ["Trial 25 — research handoff","work/ab_world/TRIAL25_SOURCE_HANDOFF.md"],
   ["Trial 30 — research handoff","work/ab_world/TRIAL30_SOURCE_HANDOFF.md"],
   ["Trial 31 — sufficiency boundary","work/ab_world/TRIAL31_SOURCE_HANDOFF.md"],
   ["Trial 31 implementation","work/ab_world/world_trial31_handoff.py"]],
  nih:[
   ["AACT status comparison","systems/workspace/NIH_P2_STATUS_DIFFERENCE_SEARCH.md"],
   ["Comparison program","systems/workspace/nih_p2_historical_status_difference_search.py"],
   ["Source dates and custody","systems/workspace/NIH_P2_AACT_OWNER_DATE_LINK.md"],
   ["Archive source boundary","systems/workspace/NIH_P2_TWO_AACT_SNAPSHOT_BOUNDARY.md"],
   ["Source variations","systems/workspace/NIH_P2_SOURCE_VARIATIONS.md"],
   ["Derived history boundary","systems/workspace/NIH_P2_DERIVED_HISTORY_BOUNDARY.md"],
   ["External-source boundary","systems/workspace/NIH_P2_EXTERNAL_SOURCE_BOUNDARY.md"],
   ["Phase 1 — source motion","systems/workspace/NIH_PHASE1_WORLD_SOURCE_MOTION.md"],
   ["Comparison tests","network/tests/test_nih_p2_historical_status_difference_search.py"]]
 };
 function initSourceReader(group){
  const select=$("#source-choice"),viewer=$("#source-body"),search=$("#source-search"),meta=$("#source-meta"),list=$("#source-list");
  if(!select||!viewer)return;
  const files=paths[group]||[];
  files.forEach(([label,path],i)=>{const b=node("button",{type:"button"},label);b.append(node("small",{},path));b.addEventListener("click",()=>select.value=String(i)&&load(i));list.append(b);const opt=node("option",{value:String(i)},label);select.append(opt)});
  let lines=[],current=0,request=0;
  const render=()=>{const needle=(search.value||"").toLowerCase().trim();clear(viewer);
   let count=0;const frag=document.createDocumentFragment();
   for(let i=0;i<lines.length;i++){if(needle&&!lines[i].toLowerCase().includes(needle))continue;
    const line=node("div",{class:"line"});line.append(node("span",{class:"n"},i+1));
    const span=node("span",{},lines[i]);line.append(span);frag.append(line);count++;
    if(count>=600){frag.append(node("div",{class:"note"},"Showing first 600 matches/lines; narrow your search for further matches."));break;}
   }
   if(count===0)frag.append(node("p",{class:"note"},"No matching lines in this source."));
   viewer.append(frag);set("line-count",lines.length+" total lines · "+count+" displayed");
  };
  const load=async i=>{current=i;select.value=String(i);request++;const id=request;const [label,path]=files[i];clear(meta);meta.append(node("span",{class:"flag"},"source revision "+PIN.slice(0,12)));link(meta,"Open original ↗",ROOT+"/blob/"+PIN+"/"+path);meta.append(node("span",{class:"note"},path));
   [...list.children].forEach((b,j)=>b.classList.toggle("selected",j===i));
   lines=["Loading original source..."];render();
   try{const res=await fetch(RAW+path,{cache:"no-store"});if(!res.ok)throw Error("HTTP "+res.status);const body=await res.text();if(id!==request)return;lines=body.split(/\r?\n/);render();}
   catch(err){if(id!==request)return;lines=["Source retrieval unavailable: "+String(err.message),"Open the original link above for the repository file."];render();}
  };
  select.addEventListener("change",()=>load(Number(select.value)));search.addEventListener("input",render);
  const copy=$("#copy-source");if(copy)copy.addEventListener("click",()=>navigator.clipboard?.writeText(lines.join("\n")).then(()=>set("copy-status","Copied"),()=>set("copy-status","Browser denied copy")));
  load(0);
 }
 const mod=n=>(n%3+3)%3;
 function world(k,e,t,c){return {k,e,t,c}}
 function next(w,x,op){
  let [u,v,z]=x;
  if(op==="A")return [mod(u+1),v,z];
  const support=(u===2&&v<w.k)?1:0;
  const pulse=(u===0&&v===0)?w.e:0;
  const balance=u===1?(v===0?w.t:v===1?-w.t:0):0;
  const shear=w.c*((v+u+1)**2-v**2);
  return [u,mod(v+u+1),mod(z+support+pulse+balance+shear)];
 }
 function pairRelation(a,b){
  if(a.k!==b.k)return ["FULL_OBSTRUCTED","Fix(B) differs across support levels; no full-state labeled conjugacy."];
  if(a.e!==b.e)return ["FULL_OBSTRUCTED","Fix(BBB) distinguishes pulse values."];
  if(a.t!==b.t){
   if(a.e===0)return ["FULL_OBSTRUCTED","Fix(AABAB) separates balanced edit values."];
   if(a.k===1||a.k===2)return ["FULL_OBSTRUCTED","Fix(ABABAB) separates partial-support worlds."];
   return ["FULL_UNROOTED","Explicit whole-state alignment moves the marked origin; not rooted."];
  }
  return ["ROOTED_FULL","Origin-fixing shear map relates these chart versions (or identity)."];
 }
 function initMath(){
  for(const side of ["a","b"]){for(const [name,range] of [["k",4],["e",2],["t",2],["c",3]]){const s=$("#"+side+"-"+name);for(let i=0;i<range;i++)s.append(node("option",{value:String(i)},i));}}
  $("#b-t").value="1";$("#a-e").value="1";$("#b-e").value="1";
  const read=s=>world(...["k","e","t","c"].map(n=>Number($("#"+s+"-"+n).value)));
  function render(){
   const a=read("a"),b=read("b"),relation=pairRelation(a,b);
   set("relation-kind",relation[0]);set("relation-explain",relation[1]);
   const q=$("#q-table");clear(q);
   for(let u=0;u<3;u++){const row=node("div",{class:"state-grid"});for(let v=0;v<3;v++){
      const qa=next(a,[u,v,0],"B")[2];const qb=next(b,[u,v,0],"B")[2];
      row.append(node("div",{class:"state-node"+(qa!==qb?" active":"")},u+","+v+" → "+qa+" / "+qb));
   }q.append(row)}
   const original=($("#action-word").value||"").toUpperCase().replace(/[^AB]/g,"").slice(0,120);const hist=[];let x=[0,0,0],y=[0,0,0];hist.push(["∅",x.slice(),y.slice()]);
   for(const op of original){x=next(a,x,op);y=next(b,y,op);hist.push([op,x.slice(),y.slice()]);}
   const step=$("#trajectory");clear(step);
   hist.forEach(([op,left,right],i)=>{const ch=node("button",{class:"chip",title:"Step "+i+" · "+op},i+" "+op+" ["+left.join("")+"] / ["+right.join("")+"]");ch.addEventListener("click",()=>{[...step.children].forEach(c=>c.classList.remove("active"));ch.classList.add("active");set("step-detail","Step "+i+" · "+op+"  A=["+left.join(", ")+"]  B=["+right.join(", ")+"]");});step.append(ch)});
   set("step-detail","Final state A=["+x.join(", ")+"]  B=["+y.join(", ")+"]");
   set("world-count","48 specified laws · 14 full-state classes · 16 rooted classes");
  }
  ["a","b"].forEach(side=>["k","e","t","c"].forEach(name=>$("#"+side+"-"+name).addEventListener("change",render)));
  $("#action-word").addEventListener("input",render);
  $("#swap-worlds").addEventListener("click",()=>{["k","e","t","c"].forEach(n=>{const a=$("#a-"+n),b=$("#b-"+n),t=a.value;a.value=b.value;b.value=t;});render()});
  render();
 }
 function initArc(){
  const sel=$("#arc-route"),level=$("#arc-level"),summary=$("#arc-summary"),plot=$("#arc-plot"),steps=$("#arc-steps");
  const entries=[["FT09","ft09_route.json"],["LS20","ls20_route.json"],["SK48","sk48_route.json"]];
  entries.forEach((x,i)=>sel.append(node("option",{value:String(i)},x[0])));
  let route=null;
  const rerender=()=>{
   clear(summary);clear(plot);clear(steps);if(!route)return;
   const meta=route.locally_reported||{};const pairs=[["Game",route.game||"not recorded"],["Local status",meta.status||"unavailable"],["Local levels",meta.levels??"unavailable"],["Reported actions",meta.actions??"unavailable"],["Source checksum",route.origin_sha256?.slice(0,12)||"unavailable"]];
   pairs.forEach(([label,value])=>{const card=node("div",{class:"metric"});card.append(node("span",{},label),node("strong",{},value));summary.append(card)});
   const groups=route.coordinate_paths_by_level||route.game_action_ids_by_level||route.action_ids_by_level||[];
   const chosen=Number(level.value)||0;
   clear(level);groups.forEach((g,i)=>level.append(node("option",{value:String(i)},"Level "+(i+1)+" ("+g.length+" entries)")));
   level.value=String(Math.min(chosen,Math.max(0,groups.length-1)));
   if(!groups.length){steps.append(node("p",{class:"note"},"Route contains no recognized per-level trajectory field. Open original JSON in source inspector."));return;}
   const g=groups[Math.max(0,Number(level.value))]||groups[0];
   const milestones=(route.recorded_milestones||[]).map((n,i)=>"L"+(i+1)+": "+n).join(" · ");
   set("arc-milestones",milestones||"No per-level milestone array in this record.");
   if(g.length&&Array.isArray(g[0])&&g[0].length>=2){
    const svgNS="http://www.w3.org/2000/svg";plot.setAttribute("viewBox","0 0 440 340");plot.setAttribute("role","img");plot.setAttribute("aria-label","Recorded coordinate points from route JSON");
    const points=g.map(p=>[Number(p[0]),Number(p[1])]);const lim=Math.max(64,...points.flat());
    for(let z=0;z<=4;z++){const ln=document.createElementNS(svgNS,"line");const at=18+z*76;ln.setAttribute("x1",String(at));ln.setAttribute("x2",String(at));ln.setAttribute("y1","18");ln.setAttribute("y2","322");ln.setAttribute("stroke","#244157");plot.append(ln);}
    const scaled=points.map(p=>[18+p[0]/lim*396,18+p[1]/lim*304]);
    const path=document.createElementNS(svgNS,"polyline");path.setAttribute("points",scaled.map(p=>p.join(",")).join(" "));path.setAttribute("fill","none");path.setAttribute("stroke","#6fd9c5");path.setAttribute("stroke-width","1.5");plot.append(path);
    scaled.forEach(([x,y],i)=>{const dot=document.createElementNS(svgNS,"circle");dot.setAttribute("cx",String(x));dot.setAttribute("cy",String(y));dot.setAttribute("r",i===0?"5":"3");dot.setAttribute("fill",i===0?"#f1c57c":"#af9aff");const title=document.createElementNS(svgNS,"title");title.textContent="Index "+(i+1)+" · "+points[i].join(",");dot.append(title);plot.append(dot)});
    steps.append(node("div",{class:"seq"},points.map((p,i)=>(i+1)+":("+p.join(",")+")").join("  →  ")));
    set("arc-plot-note","Recorded coordinate targets joined by index for inspection. The connecting lines do not reconstruct intermediate gameplay frames.");
   }else{
    plot.setAttribute("viewBox","0 0 440 60");set("arc-plot-note","This route records discrete action identifiers, not coordinates.");
    const max=160;const wrap=node("div",{class:"seq"},g.slice(0,max).map((v,i)=>(i+1)+":"+String(v)).join("   "));steps.append(wrap);
    if(g.length>max)steps.append(node("p",{class:"note"},"Showing "+max+" of "+g.length+" actions; inspect original JSON for the complete route."));
   }
  };
  sel.addEventListener("change",load);level.addEventListener("change",rerender);
  async function load(){
   const [label,file]=entries[Number(sel.value)];const path="research/arc_native_runs/"+file;
   set("arc-route-status","Retrieving recorded route...");
   try{const r=await fetch(RAW+path,{cache:"no-store"});if(!r.ok)throw Error("HTTP "+r.status);route=await r.json();level.value="0";set("arc-route-status","Source JSON loaded · "+PIN.slice(0,12)+" · "+label);rerender();}
   catch(e){route=null;clear(summary);clear(plot);clear(steps);set("arc-route-status","Could not load source JSON ("+e.message+"). Use repository link.");}
  }
  load();
 }
 function initWorld(){
  const items=[["Trial 06","Virtual source trajectories", "10 connected trajectory results and matched controls recorded over 1.5 seconds","work/ab_world/TRIAL06_SOURCE_HANDOFF.md"],["Trial 30","Short-response comparison","Three hypothetical qualified response cases over a short declared virtual-time window","work/ab_world/TRIAL30_SOURCE_HANDOFF.md"],["Trial 31","Sufficient-bound limit","24 conservative inequalities checked over a 0.25-unit horizon; three qualified cases lost a sufficient clearance bound","work/ab_world/TRIAL31_SOURCE_HANDOFF.md"]];
  const target=$("#world-trials");
  items.forEach(([label,name,desc,path])=>{const p=node("div",{class:"panel"});p.append(node("div",{class:"eyebrow"},label),node("h2",{},name),node("p",{},desc));link(p,"Inspect pinned source",ROOT+"/blob/"+PIN+"/"+path);target.append(p);});
 }
 function initNih(){
  const metrics=[["2022-labeled file","432,983"],["Other deposit","432,597"],["Shared NCT IDs","432,597"],["Different status fields","1,345"],["Only in 2022-labeled file","386"],["Only in other file","0"]];
  const target=$("#nih-metrics");metrics.forEach(([label,val])=>{const c=node("div",{class:"metric"});c.append(node("span",{},label),node("strong",{},val));target.append(c)});
  const bars=$("#nih-bars");const rows=[["Shared IDs",432597,432983],["Only in 2022-labeled file",386,432983],["Different recorded status values",1345,432597]];
  rows.forEach(([label,v,d])=>{const group=node("div",{class:"barrow"});group.append(node("div",{class:"barlabel"},label+" · "+v.toLocaleString()+" / "+d.toLocaleString()+" ("+(v/d*100).toFixed(3)+"%)"));const track=node("div",{class:"bartrack"}),bar=node("div");bar.style.width=(v/d*100)+"%";if(v/d*100<1)bar.style.minWidth="3px";track.append(bar);group.append(track);bars.append(group);});
 }
 document.addEventListener("DOMContentLoaded",()=>{if(PAGE==="math")initMath();if(PAGE==="arc")initArc();if(PAGE==="world")initWorld();if(PAGE==="nih")initNih();if(paths[PAGE])initSourceReader(PAGE);});
})();