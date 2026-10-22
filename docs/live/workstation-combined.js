/* Combined workstation observations inside the primary execution viewer.
   Read-only, source-owned GitHub observation journals. No job dispatch. */
"use strict";
(()=>{
  const ORIGIN="https://raw.githubusercontent.com/huntingthereferent/autobots-assemble/";
  const BASE=ORIGIN+"meta-observations/";
  const URLS={
    registry:ORIGIN+"main/docs/live/meta-registry.json",
    history:BASE+"history.json",
    daily:BASE+"daily.json",
    health:BASE+"health.json",
    routing:BASE+"routing.json"
  };
  const $=id=>document.getElementById(id);
  const integer=n=>Number.isSafeInteger(n)&&n>=0;
  const validTime=s=>{const n=Date.parse(s||"");return Number.isFinite(n)?n:null};
  const fresh=(s,now)=>{const n=validTime(s);return n!==null&&n<=now+60000&&now-n<=90*60000};
  const fmt=n=>integer(n)?n.toLocaleString():"—";
  const stamp=s=>{const n=validTime(s);return n===null?"Unknown time":new Date(n).toLocaleString(undefined,{month:"short",day:"numeric",hour:"numeric",minute:"2-digit",hour12:true})};
  function chicagoDay(date){
    const parts=new Intl.DateTimeFormat("en-US",{timeZone:"America/Chicago",year:"numeric",month:"2-digit",day:"2-digit"}).formatToParts(new Date(date));
    const v=Object.fromEntries(parts.map(p=>[p.type,p.value]));
    return v.year+"-"+v.month+"-"+v.day;
  }
  function verifiedRegistry(registry){
    if(registry?.schema!=="meta-workstation/registry-v1"||!Array.isArray(registry.nodes))throw Error("Registry unknown");
    const nodes=["A","B"].map(id=>registry.nodes.find(n=>n.id===id));
    if(nodes.some(n=>!n||typeof n.repo!=="string"||!/^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/.test(n.repo)))throw Error("Source identities unknown");
    return nodes;
  }
  function matchesNodes(record,nodes){
    return nodes.every(n=>record?.nodes?.[n.id]?.repo===n.repo&&record.nodes[n.id].observed===true);
  }
  function summarize(registry,history,daily,health,routing,now=Date.now()){
    const nodes=verifiedRegistry(registry);
    const result={running:null,waiting:null,successful:null,review:null,issues:[],route:"Routing advice unavailable",status:"PARTIAL SOURCE",sourceAt:null,dayAt:null,healthAt:null};
    const samples=history?.schema==="ab-meta-observations/v1"&&Array.isArray(history.samples)?history.samples:[];
    const candidates=samples.filter(s=>matchesNodes(s,nodes)&&fresh(s.ts,now));
    const last=candidates.reduce((best,s)=>!best||Date.parse(s.ts)>Date.parse(best.ts)?s:best,null);
    if(last){
      const r=nodes.reduce((n,node)=>n+last.nodes[node.id].in_progress,0);
      const q=nodes.reduce((n,node)=>n+last.nodes[node.id].queued+last.nodes[node.id].pending+last.nodes[node.id].waiting,0);
      if(nodes.every(node=>["in_progress","queued","pending","waiting"].every(k=>integer(last.nodes[node.id][k])))){
        result.running=r;result.waiting=q;result.sourceAt=last.ts;
      }
    }
    if(daily?.schema==="meta-workstation/daily-runs-v1"&&daily.all_sources===true&&
      daily.timezone==="America/Chicago"&&daily.local_date===chicagoDay(now)&&
      matchesNodes(daily,nodes)&&fresh(daily.observed_at,now)&&integer(daily.totals?.success)){
      result.successful=daily.totals.success;
      result.dayAt=daily.observed_at;
    }
    if(health?.schema==="meta-workstation/current-workflow-health-v1"&&health.all_sources===true&&
      matchesNodes(health,nodes)&&fresh(health.observed_at,now)&&
      integer(health.summary?.open_count)&&Array.isArray(health.summary.open)&&
      health.summary.open.length===health.summary.open_count){
      result.review=health.summary.open_count;
      result.issues=health.summary.open.filter(r=>nodes.some(n=>n.repo===r.repo)&&integer(r.run_id)&&r.run_id>0&&typeof r.name==="string");
      result.healthAt=health.observed_at;
    }
    if(routing?.schema==="meta-workstation/routing-advice-v1"&&fresh(routing.generated_at,now)){
      result.route=routing.signal==="NO_CLEAR_PRESSURE"?"No supported rerouting pressure in sampled queues":
        routing.signal==="OBSERVING"?"Measuring queue pressure; no routing change":
        ["A_BACKLOG","B_BACKLOG"].includes(routing.signal)?"Backlog signal; verify workflow eligibility before moving work":
        "No verified routing change";
    }
    result.status=[result.running,result.waiting,result.successful,result.review].every(integer)?"SOURCE OBSERVED":"PARTIAL SOURCE";
    return result;
  }
  function render(summary){
    for(const [key,value] of Object.entries({running:summary.running,waiting:summary.waiting,passed:summary.successful,review:summary.review})){
      const target=$("combined-"+key);if(target)target.textContent=fmt(value);
    }
    $("combined-status").textContent=summary.status;
    $("combined-source-note").textContent=summary.sourceAt?
      "Both source journals · sampled "+stamp(summary.sourceAt)+" · counts are observations, not execution capacity":
      "Current paired observation unavailable · unknown is not zero";
    $("combined-daily-note").textContent=summary.dayAt?"Full-day success journal · "+stamp(summary.dayAt):"Full-day combined success total unavailable";
    $("combined-review-note").textContent=summary.healthAt?
      "Latest conclusive workflow outcomes · "+stamp(summary.healthAt)+" · not individual test proof":
      "Combined workflow-health record unavailable";
    $("combined-routing").textContent=summary.route+" · advisory only; no automatic movement";
    const items=$("combined-issues");items.replaceChildren();
    if(!integer(summary.review)){items.textContent="Current source health unavailable; no open/closed inference.";return}
    if(summary.review===0){items.textContent="No workflows currently flagged by this source snapshot; prior history is retained.";return}
    for(const issue of summary.issues){
      const row=document.createElement("div");row.className="combined-issue";
      const a=document.createElement("a");
      a.href="https://github.com/"+issue.repo+"/actions/runs/"+issue.run_id;
      a.target="_blank";a.rel="noopener noreferrer";
      a.textContent=issue.name+" · run "+issue.run_id+" ↗";
      row.append(a);items.append(row);
    }
  }
  let busy=false;
  async function refresh(){
    if(busy)return;busy=true;
    try{
      const names=Object.keys(URLS);
      const settled=await Promise.allSettled(names.map(async key=>{
        const response=await fetch(URLS[key],{cache:"no-store",headers:{Accept:"application/json"}});
        if(!response.ok)throw Error("Source HTTP "+response.status);
        return response.json();
      }));
      const values=Object.fromEntries(names.map((key,i)=>[key,settled[i].status==="fulfilled"?settled[i].value:null]));
      render(summarize(values.registry,values.history,values.daily,values.health,values.routing));
    }catch(e){
      render({running:null,waiting:null,successful:null,review:null,issues:[],route:"Registry or source unavailable",status:"SOURCE UNKNOWN",sourceAt:null,dayAt:null,healthAt:null});
    }finally{busy=false}
  }
  function start(){
    $("check-now")?.addEventListener("click",refresh);
    document.addEventListener("visibilitychange",()=>{if(!document.hidden)refresh()});
    setInterval(()=>{if(!document.hidden)refresh()},300000);
    refresh();
  }
  window.WorkstationCombined={start,summarize};
})();
