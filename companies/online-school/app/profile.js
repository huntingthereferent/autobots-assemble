const $ = sel => document.querySelector(sel);
let record = null;

function statusMeta(status){
  return {
    "demonstrated": {symbol:"✓", label:"Demonstrated"},
    "developing": {symbol:"◐", label:"Developing"},
    "introduced": {symbol:"○", label:"Introduced / some evidence"},
    "not-observed": {symbol:"□", label:"Not yet evidenced"}
  }[status] || {symbol:"□",label:"Not yet evidenced"};
}

function row(title, detail=""){
  const el=document.createElement("div");
  el.className="record-row";
  const strong=document.createElement("strong");
  strong.textContent=title;
  el.append(strong);
  if(detail){
    const p=document.createElement("p");
    p.textContent=detail;
    el.append(p);
  }
  return el;
}

async function loadLearners(){
  const response=await fetch("/api/state",{cache:"no-store"});
  const state=await response.json();
  const select=$("#learner-select");
  select.replaceChildren(...(state.learners||[]).map(learner=>{
    const option=document.createElement("option");
    option.value=learner.id;
    option.textContent=learner.display_name||learner.id;
    return option;
  }));
  const wanted=new URLSearchParams(location.search).get("learner");
  if(wanted && [...select.options].some(o=>o.value===wanted)) select.value=wanted;
  if(select.value) await loadRecord(select.value);
}

async function loadRecord(learnerId){
  const response=await fetch("/api/record?learner="+encodeURIComponent(learnerId),{cache:"no-store"});
  if(!response.ok) throw new Error("Could not load learner record");
  record=await response.json();
  render();
}

function renderStandards(){
  const root=$("#standards-list");
  const standards=record.standards||[];
  root.replaceChildren(...standards.map(target=>{
    const meta=statusMeta(target.status);
    const card=document.createElement("article");
    card.className="standard-row";
    const evidenceCount=(target.task_evidence||[]).length+(target.worksheet_evidence||[]).length;
    card.innerHTML='<div class="standard-top"><span class="status-symbol"></span><div><h3></h3><p></p><span class="standard-code"></span></div><strong class="status-label"></strong></div><div class="standard-controls"><select></select><input type="text" placeholder="Optional evaluation note"><button type="button">Save</button></div><p class="evidence-note"></p>';
    const symbol=card.querySelector(".status-symbol");
    symbol.textContent=meta.symbol;
    symbol.classList.add("status-"+target.status);
    card.querySelector("h3").textContent=target.title;
    card.querySelector(".standard-top p").textContent=target.description;
    card.querySelector(".standard-code").textContent=target.code;
    card.querySelector(".status-label").textContent=meta.label;
    const select=card.querySelector("select");
    [
      ["demonstrated","✓ Demonstrated"],
      ["developing","◐ Developing"],
      ["introduced","○ Introduced / some evidence"],
      ["not-observed","□ Not yet evidenced"]
    ].forEach(([value,label])=>{
      const option=document.createElement("option");
      option.value=value;option.textContent=label;
      if(value===target.status) option.selected=true;
      select.append(option);
    });
    const note=card.querySelector("input");
    note.value=target.note||"";
    card.querySelector(".evidence-note").textContent=evidenceCount
      ? evidenceCount+" linked task/work evidence item(s)"
      : "No explicitly linked task/work evidence yet";
    card.querySelector("button").onclick=async()=>{
      const response=await fetch("/api/progress",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({
          learner_id:record.learner.id,
          code:target.code,
          status:select.value,
          note:note.value
        })
      });
      if(!response.ok){alert("Could not save progress");return;}
      await loadRecord(record.learner.id);
    };
    return card;
  }));
  $("#standards-empty").hidden=standards.length!==0;
}

function render(){
  const learner=record.learner||{};
  $("#learner-name").textContent=learner.display_name||"Learner";
  $("#learner-meta").textContent=[
    learner.age ? "Age "+learner.age : "",
    record.grade_context ? "Grade comparison "+record.grade_context : "No grade comparison selected"
  ].filter(Boolean).join(" · ");
  $("#generated-on").textContent=record.generated_on||"";
  $("#standards-source").textContent=record.standards_source||"";

  const standards=record.standards||[];
  $("#count-demonstrated").textContent=standards.filter(x=>x.status==="demonstrated").length;
  $("#count-developing").textContent=standards.filter(x=>x.status==="developing").length;
  $("#recorded-hours").textContent=record.hours?.recorded_completed_hours??0;
  $("#work-count").textContent=(record.worksheets||[]).length;

  renderStandards();

  $("#relations-list").replaceChildren(...(record.current_relations||[]).map(rel=>{
    const detail=[
      ...(rel.supported||[]).map(x=>"available: "+x),
      ...(rel.unsupported||[]).map(x=>"not yet: "+x)
    ].join(" · ");
    return row(rel.referent||"Current relation",detail||"Evidence recorded");
  }));

  $("#observations-list").replaceChildren(...(record.observations||[]).map(obs=>
    row(obs.referent||"Observation",(obs.observed||"")+" · "+(obs.formed_at||""))
  ));

  const placement=record.placement||{};
  $("#placement-record").replaceChildren(
    row("Placement status: "+(placement.status||"required"),
      (placement.completed_subjects||[]).length
        ? "Completed: "+placement.completed_subjects.join(", ")
        : "No placement sections completed yet")
  );
  const retests=(record.tasks||[]).filter(task=>(task.meta||{}).week_phase==="retest");
  $("#retests-list").replaceChildren(...retests.map(task=>
    row(task.date+" · "+task.title,task.status)
  ));

  const categories=record.hours?.completed_by_category_minutes||{};
  $("#hours-breakdown").replaceChildren(
    ...Object.entries(categories).map(([category,minutes])=>{
      const el=document.createElement("div");
      el.className="hour-card";
      el.innerHTML="<strong></strong><span></span>";
      el.querySelector("strong").textContent=(minutes/60).toFixed(2)+" hr";
      el.querySelector("span").textContent=category.replaceAll("-"," ");
      return el;
    })
  );

  $("#task-record").replaceChildren(...(record.tasks||[]).slice().sort((a,b)=>
    String(a.date||"").localeCompare(String(b.date||""))
  ).map(task=>row(
    (task.date||"")+" · "+(task.title||"Activity"),
    [task.status,task.planned_minutes ? task.planned_minutes+" min" : "",task.source||""].filter(Boolean).join(" · ")
  )));

  $("#worksheets-list").replaceChildren(...(record.worksheets||[]).map(work=>
    row(work.title||"Saved worksheet",work.knowledge_goal||work.template||"Portfolio work")
  ));

  $("#calendar-list").replaceChildren(...(record.calendar||[]).map(item=>
    row(item.date+" · "+item.relation,"Current generated week")
  ));

  $("#record-boundary").textContent=record.record_boundary||"";
}

$("#learner-select").onchange=event=>{
  const url=new URL(location.href);
  url.searchParams.set("learner",event.target.value);
  history.replaceState(null,"",url);
  loadRecord(event.target.value);
};
$("#print-record").onclick=()=>window.print();

loadLearners().catch(err=>{
  document.body.innerHTML="<p style='padding:24px'>"+err.message+"</p>";
});
