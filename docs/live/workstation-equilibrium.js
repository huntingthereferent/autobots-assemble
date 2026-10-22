"use strict";
/* Source-observed GitHub workflow equilibrium watch.
 * Data points are successful browser polls, NOT exact job-level telemetry.
 * No auto-dispatch, synthetic completions, capacity claims, persistent storage,
 * or mathematical proof of a stationary equilibrium.
 */
(() => {
  const $=id=>document.getElementById(id);
  const samples=[];
  let previous=null;
  let firstAt=null;
  let firstWaiting=null;
  let totalSamples=0;
  let arrivals=0;
  let observedFinishes=0;
  const WINDOW=180;
  const QUEUED=new Set(["queued","waiting","pending","requested"]);
  const validDate=value=>{const t=Date.parse(value||"");return Number.isFinite(t)?t:null};
  const numeric=n=>Number(n).toLocaleString(undefined,{maximumFractionDigits:1});
  function status(run) {
    return run.status==="completed"?"completed":
      QUEUED.has(run.status)?"queued":run.status==="in_progress"?"running":"other";
  }
  function sample(snapshot) {
    if(!snapshot||!Number.isFinite(snapshot.checked)||!Array.isArray(snapshot.latestPage)||!snapshot.latestPage.length)return;
    const t=snapshot.checked;
    if(samples.length&&t<=samples[samples.length-1].t)return;
    const runs=snapshot.latestPage;
    const known=new Map(runs.map(r=>[r.id,r]));
    const waiting=runs.filter(r=>status(r)==="queued").length;
    const working=runs.filter(r=>status(r)==="running").length;
    // Only count arrivals that we actually see, since an individual completed
    // run might be dropped from a latest-100 API page before the next poll.
    if(previous!==null){
      for(const [id,r] of known){
        const before=previous.get(id);
        if(before){
          if(status(before)!=="completed"&&status(r)==="completed")observedFinishes++;
        }else{
          const created=validDate(r.created);
          if(created!==null&&created>samples[samples.length-1].t&&created<=t){
            arrivals++;
            if(status(r)==="completed")observedFinishes++;
          }
        }
      }
    }
    if(firstAt===null){firstAt=t;firstWaiting=waiting;}
    totalSamples++;
    previous=known;
    samples.push({t,waiting,working});
    if(samples.length>WINDOW)samples.shift();
    render();
  }
  function toText(id,value){const node=$(id);if(node)node.textContent=value;}
  function lineChart(){
    const target=$("equilibrium-graph");
    if(!target)return;
    target.replaceChildren();
    const rows=samples.slice(-32);
    const high=Math.max(1,...rows.map(r=>Math.max(r.waiting,r.working)));
    for(const r of rows){
      const col=document.createElement("div");col.className="eq-graph-col";
      const q=document.createElement("span");q.className="eq-wait";
      const running=document.createElement("span");running.className="eq-work";
      q.style.height=(r.waiting?Math.max(3,r.waiting/high*62):2)+"px";
      running.style.height=(r.working?Math.max(3,r.working/high*62):2)+"px";
      col.title=new Date(r.t).toLocaleTimeString(undefined,{hour:"numeric",minute:"2-digit",hour12:true})+
        " · "+r.waiting+" queued / "+r.working+" running (latest-page sample)";
      col.append(q,running);target.append(col);
    }
  }
  function render(){
    const count=samples.length;
    if(!count)return;
    const first=samples[0],latest=samples[count-1];
    const seconds=(latest.t-firstAt)/1000;
    let weight=0,weightedBusy=0,weightedWait=0;
    for(let i=1;i<count;i++){
      const dt=samples[i].t-samples[i-1].t;
      // Snapshot-state average over observation intervals: a previous
      // successful API sample remains the most recent known state.
      if(dt<=0||dt>15*60*1000)continue; // gaps are unobserved, not stable.
      weight+=dt;
      weightedBusy+=samples[i-1].working*dt;
      weightedWait+=samples[i-1].waiting*dt;
    }
    const avgBusy=weight?weightedBusy/weight:null;
    const avgQueue=weight?weightedWait/weight:null;
    const peak=Math.max(...samples.map(s=>s.working));
    const queueDelta=latest.waiting-firstWaiting;
    const hours=seconds/3600;
    const arrivalsPerHour=hours>0?arrivals/hours:null;
    const finishesPerHour=hours>0?observedFinishes/hours:null;
    const enough=count>=5&&seconds>=8*60&&weight>=6*60*1000;
    let state="OBSERVING";
    let explanation="Need at least five successful checks over eight minutes to compare flow.";
    if(enough){
      if(latest.waiting>firstWaiting+1&&arrivalsPerHour>finishesPerHour*1.15){
        state="BACKLOG GROWING";explanation="Queue is rising and newly observed arrival rate exceeds completion detection.";
      }else if(latest.waiting<firstWaiting-1){
        state="BACKLOG DRAINING";explanation="Observed queue is shrinking across this session.";
      }else if(latest.waiting>0&&Math.abs(arrivalsPerHour-finishesPerHour)<=Math.max(1,Math.max(arrivalsPerHour,finishesPerHour)*.2)){
        state="STEADY CANDIDATE";explanation="Observed arrival/completion rates are close; queue has not grown materially. Keep measuring.";
      }else if(latest.waiting===0&&latest.working===0){
        state="IDLE";explanation="No queued or running workflow appears in the latest 100-run page.";
      }else if(latest.waiting===0){
        state="NO VISIBLE BACKLOG";explanation="Useful capacity might be waiting for more work; runner capacity is not established.";
      }else{
        state="UNSETTLED";explanation="Queue and measured arrival/completion signals do not yet indicate steady flow.";
      }
    }
    toText("eq-state",state);
    toText("eq-description",explanation);
    toText("eq-samples",totalSamples+" checks · "+numeric(seconds/60)+" session min");
    toText("eq-avg-running",avgBusy===null?"—":numeric(avgBusy));
    toText("eq-peak-running",numeric(peak));
    toText("eq-avg-waiting",avgQueue===null?"—":numeric(avgQueue));
    toText("eq-queue-drift",(queueDelta>0?"+":"")+numeric(queueDelta));
    toText("eq-in",arrivalsPerHour===null?"—":numeric(arrivalsPerHour)+"/h");
    toText("eq-out",finishesPerHour===null?"—":numeric(finishesPerHour)+"/h");
    toText("eq-boundary",
      "Only latest-100 GitHub workflow RUNS sampled during this browser session. "+ 
      "Arrival and completion rates are lower-bound detections between polls; fast runs may be missed. "+
      "Running and waiting averages are sampled, not measured runner/job utilization. "+
      "No confirmed concurrency cap, automatic queue filling, or persisted equilibrium history.");
    lineChart();
  }
  window.WorkstationEquilibrium={sample};
})();
