"use strict";
/* Read-only workstation observation instrument.
   No scheduling, simulated ticks, inferred capacity or private journal writes. */
(() => {
  const $=id=>document.getElementById(id);
  const DAY=24*60*60*1000;
  const state={
    view:"day",anchor:new Date(),followToday:true,onChange:null,previous:new Map(),previousCheck:null,
    changes:[],loaded:false
  };
  state.anchor.setHours(0,0,0,0);
  const validTime=value=>{const time=Date.parse(value||"");return Number.isFinite(time)?time:null};
  const localDay=d=>new Date(d.getFullYear(),d.getMonth(),d.getDate());
  const sameDay=(a,b)=>a.getFullYear()===b.getFullYear()&&a.getMonth()===b.getMonth()&&a.getDate()===b.getDate();
  const status=r=>{
    if(["queued","waiting","pending","requested"].includes(r.status))return "queued";
    if(r.status==="in_progress")return "running";
    if(r.status==="completed")return "finished";
    return "other";
  };
  const number=n=>Number(n).toLocaleString();
  const clock=t=>new Date(t).toLocaleTimeString(undefined,{hour:"numeric",minute:"2-digit",hour12:true});
  function periodBounds(){
    synchronizeToday();
    const a=state.anchor;
    if(state.view==="all")return null;
    if(state.view==="year")return [new Date(a.getFullYear(),0,1),new Date(a.getFullYear()+1,0,1)];
    if(state.view==="month")return [new Date(a.getFullYear(),a.getMonth(),1),new Date(a.getFullYear(),a.getMonth()+1,1)];
    return [localDay(a),new Date(a.getFullYear(),a.getMonth(),a.getDate()+1)];
  }
  function matches(r){
    const bounds=periodBounds();
    if(!bounds)return true;
    const t=validTime(r.created);
    return t!==null&&t>=bounds[0].getTime()&&t<bounds[1].getTime();
  }
  function synchronizeToday(){
    if(!state.followToday)return false;
    const now=localDay(new Date());
    if(sameDay(now,state.anchor))return false;
    state.anchor=now;
    return true;
  }
  function tick(){if(synchronizeToday()){notify();return true;}return false;}
  function periodName(){
    synchronizeToday();
    if(state.view==="all")return "ALL HISTORY";
    if(state.view==="year")return String(state.anchor.getFullYear());
    if(state.view==="month")return state.anchor.toLocaleDateString(undefined,{month:"long",year:"numeric"}).toUpperCase();
    if(sameDay(state.anchor,new Date()))return "TODAY";
    return state.anchor.toLocaleDateString(undefined,{weekday:"short",month:"short",day:"numeric",year:"numeric"}).toUpperCase();
  }
  function nav(){
    if(!$("journal-title"))return;
    $("journal-title").textContent=periodName();
    document.querySelectorAll("[data-journal-mode]").forEach(btn=>{
      const value=btn.dataset.journalMode;
      const active=value===state.view&&(value!=="day"||!sameDay(state.anchor,new Date()));
      btn.setAttribute("aria-pressed",String(active));
    });
    const isToday=state.view==="day"&&sameDay(state.anchor,new Date());
    $("journal-today").setAttribute("aria-pressed",String(isToday));
    const future=state.view!=="all"&&(state.view==="day"&&isToday||
      state.view==="month"&&state.anchor.getFullYear()===new Date().getFullYear()&&state.anchor.getMonth()===new Date().getMonth()||
      state.view==="year"&&state.anchor.getFullYear()===new Date().getFullYear());
    $("journal-next").disabled=state.view==="all"||future;
    $("journal-prev").disabled=state.view==="all";
    $("journal-note").textContent="Local calendar time · original source IDs retained · choose a run for its native jobs and steps";
  }
  function notify(){nav();if(state.onChange)state.onChange();}
  function choose(mode){
    if(mode==="today"){state.view="day";state.anchor=localDay(new Date());state.followToday=true;}
    else {state.followToday=false;state.view=mode;if(mode==="day"&&state.anchor>new Date())state.anchor=localDay(new Date());}
    notify();
  }
  function shift(amount){
    if(state.view==="all")return;
    state.followToday=false;
    const d=state.anchor;
    if(state.view==="year")state.anchor=new Date(d.getFullYear()+amount,0,1);
    else if(state.view==="month")state.anchor=new Date(d.getFullYear(),d.getMonth()+amount,1);
    else state.anchor=new Date(d.getFullYear(),d.getMonth(),d.getDate()+amount);
    if(state.anchor>new Date())state.anchor=localDay(new Date());
    notify();
  }
  function install(onChange){
    state.onChange=onChange;
    document.querySelectorAll("[data-journal-mode]").forEach(b=>b.addEventListener("click",()=>choose(b.dataset.journalMode)));
    $("journal-today").addEventListener("click",()=>choose("today"));
    $("journal-prev").addEventListener("click",()=>shift(-1));
    $("journal-next").addEventListener("click",()=>shift(1));
    nav();
  }
  function scopeLabel(total,shown){
    return periodName()+" · "+number(total)+" matching runs · "+number(shown)+" shown";
  }
  function setStat(name,value,available=state.loaded){
    const el=document.querySelector('[data-stat="'+name+'"]');
    if(!el)return;
    const next=available?number(value):"—";
    if(el.textContent!==next){
      el.textContent=next;el.classList.remove("flow-changed");
      void el.offsetWidth;el.classList.add("flow-changed");
    }
    const cell=el.closest(".metric");
    const light=cell&&cell.querySelector(".flow-level");
    if(light){
      light.replaceChildren();
      for(let i=0;i<12;i++){
        const led=document.createElement("i");
        if(available&&i<Math.min(12,value))led.className="on";
        light.append(led);
      }
      light.title=available?number(value)+" observed · 12 indicators maximum, not a capacity gauge":"No fresh execution-state sample";
    }
  }
  function setText(id,s){const el=$(id);if(el)el.textContent=s;}
  function lane(id,items,note,available=state.loaded){
    const box=$("flow-beads-"+id);
    if(!box)return;
    box.replaceChildren();
    if(!items.length){const placeholder=document.createElement("span");placeholder.className="flow-empty";placeholder.textContent=available?"No observed runs":"Current state unavailable";box.append(placeholder);}
    for(const [i,r] of items.slice(0,18).entries()){
      const bead=document.createElement("span");
      bead.className="flow-bead";
      bead.style.setProperty("--bead-index",String(i));
      bead.title=r.name+" · #"+r.id+" · "+r.status+(r.conclusion?" / "+r.conclusion:"");
      bead.setAttribute("aria-label",bead.title);
      box.append(bead);
    }
    if(items.length>18){const more=document.createElement("span");more.className="flow-overflow";more.textContent="+"+number(items.length-18);box.append(more);}
    setText("flow-count-"+id,available?number(items.length):"—");
    setText("flow-note-"+id,note);
  }
  function bars(runs,now){
    const target=$("flow-bars");
    if(!target)return;
    const start=new Date(now);start.setMinutes(0,0,0);
    const bins=Array.from({length:12},(_,i)=>({start:start.getTime()-(11-i)*3600000,count:0}));
    for(const r of runs){
      const t=validTime(r.created);if(t===null)continue;
      for(const bin of bins)if(t>=bin.start&&t<bin.start+3600000){bin.count++;break;}
    }
    const max=Math.max(1,...bins.map(x=>x.count));
    target.replaceChildren();
    for(const bin of bins){
      const col=document.createElement("div");col.className="flow-spark-col";
      const b=document.createElement("span");b.style.height=(bin.count?Math.max(5,Math.round(bin.count/max*69)):2)+"px";
      col.title=clock(bin.start)+" · "+number(bin.count)+" runs created";
      col.append(b);target.append(col);
    }
  }
  function observeChanges(latest,checked){
    if(!checked||state.previousCheck===checked)return;
    const curr=new Map(latest.map(r=>[r.id,{status:r.status,conclusion:r.conclusion,name:r.name}]));
    if(state.previousCheck!==null){
      for(const r of latest){
        const was=state.previous.get(r.id);
        if(was&&(was.status!==r.status||was.conclusion!==r.conclusion)){
          state.changes.unshift({name:r.name,id:r.id,status:r.conclusion||r.status,at:checked});
        }
      }
      state.changes=state.changes.slice(0,12);
    }
    state.previous=curr;state.previousCheck=checked;
    const wrap=$("flow-changes");
    if(!wrap)return;
    wrap.replaceChildren();
    if(!state.changes.length){
      const item=document.createElement("div");item.className="flow-change";
      item.textContent="No status transitions observed between checks yet";
      wrap.append(item);
    }else{
      for(const c of state.changes.slice(0,4)){
        const el=document.createElement("div");el.className="flow-change";
        const name=document.createElement("span");name.textContent=c.name+" #"+c.id;
        const result=document.createElement("b");result.textContent=c.status.toUpperCase()+" · "+clock(c.at);
        el.append(name,result);wrap.append(el);
      }
    }
  }
  function render(snapshot){
    const {runs=[],latestPage=[],archiveComplete=false,checked=null,liveAvailable=true}=snapshot||{};
    const source=archiveComplete?runs:latestPage;
    state.loaded=archiveComplete||latestPage.length>0;
    const now=Date.now(),today=localDay(new Date(now));
    const fresh=liveAvailable&&Number.isFinite(checked)&&checked<=now+15000&&now-checked<=5*60*1000&&latestPage.length>0;
    const todays=source.filter(r=>{const t=validTime(r.created);return t!==null&&sameDay(new Date(t),today);});
    // Never count archived queued/running statuses as live. The latest
    // checked page covers only its returned 100 identities, not all jobs.
    const queue=fresh?latestPage.filter(r=>status(r)==="queued"):[];
    const active=fresh?latestPage.filter(r=>status(r)==="running"):[];
    const finished=todays.filter(r=>status(r)==="finished");
    const passed=finished.filter(r=>r.conclusion==="success");
    const failed=finished.filter(r=>["failure","cancelled","timed_out"].includes(r.conclusion));
    const arrivalsHour=source.filter(r=>{const t=validTime(r.created);return t!==null&&t>=now-3600000&&t<=now;});
    const clearance=todays.length?Math.round(finished.length/todays.length*100):null;
    setStat("queued",queue.length,fresh);
    setStat("running",active.length,fresh);
    setStat("passed",passed.length);
    setStat("failed",failed.length);
    const show=v=>state.loaded?number(v):"—";
    setText("flow-created",show(todays.length));
    setText("flow-cleared",show(finished.length));
    setText("flow-clearance",state.loaded?(clearance===null?"—":clearance+"%"):"—");
    setText("flow-arrivals",show(arrivalsHour.length));
    setText("flow-source",fresh?(archiveComplete?"LATEST 100 STATES · FULL HISTORICAL INDEX":"LATEST 100 STATES · PARTIAL HISTORY"):
      (archiveComplete?"ARCHIVE ONLY · LIVE STATE UNAVAILABLE":"LIVE STATE UNAVAILABLE"));
    lane("queued",queue,fresh?"Waiting workflows in latest 100 · not capacity":"Live state unavailable · archive does not prove queue",fresh);
    lane("running",active,fresh?"Executing workflows in latest 100":"Live state unavailable · archive does not prove activity",fresh);
    lane("finished",finished,"Completed runs created today");
    bars(source,now);
    observeChanges(latestPage,checked);
    setText("flow-last",checked?"Last successful live check "+clock(checked)+(fresh?" · latest 100 sampled":" · STALE / NOT CURRENT"):"No verified live check yet");
    nav();
  }
  function historyBins(runs){
    synchronizeToday();
    const a=state.anchor,bins=[];
    function push(start,end,label){bins.push({start:start.getTime(),end:end.getTime(),label,
      tooltip:start.toLocaleDateString(undefined,{month:"short",day:"numeric",year:"numeric"})});}
    if(state.view==="day"){
      for(let h=0;h<24;h+=2)push(new Date(a.getFullYear(),a.getMonth(),a.getDate(),h),
        new Date(a.getFullYear(),a.getMonth(),a.getDate(),h+2),
        new Date(a.getFullYear(),a.getMonth(),a.getDate(),h).toLocaleTimeString(undefined,{hour:"numeric",hour12:true}));
    }else if(state.view==="month"){
      const days=new Date(a.getFullYear(),a.getMonth()+1,0).getDate();
      for(let d=1;d<=days;d++)push(new Date(a.getFullYear(),a.getMonth(),d),
        new Date(a.getFullYear(),a.getMonth(),d+1),String(d));
    }else if(state.view==="year"){
      for(let m=0;m<12;m++)push(new Date(a.getFullYear(),m,1),
        new Date(a.getFullYear(),m+1,1),
        new Date(a.getFullYear(),m,1).toLocaleDateString(undefined,{month:"short"}));
    }else{
      const years=runs.map(r=>validTime(r.created)).filter(t=>t!==null).map(t=>new Date(t).getFullYear());
      const first=years.length?Math.min(...years):new Date().getFullYear(),last=years.length?Math.max(...years):new Date().getFullYear();
      for(let y=first;y<=last;y++)push(new Date(y,0,1),new Date(y+1,0,1),String(y));
    }
    return {title:state.view==="all"?"Run activity by year":
      state.view==="year"?"Run activity by month":
      state.view==="month"?"Run activity by day":"Run activity by two-hour window",
      label:periodName(),bins};
  }
  window.WorkstationFlow={install,matches,scopeLabel,render,clock,tick,historyBins};
})();
