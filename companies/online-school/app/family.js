"use strict";
(function(){
const $=id=>document.getElementById(id),core=window.SchoolFamily;
const localDay=()=>{const d=new Date();return new Date(d.getTime()-d.getTimezoneOffset()*60000).toISOString().slice(0,10)};
let monday=core.monday(localDay()),learners=[],tasks=[],selected="all",revision=0,busy=false;
const today=localDay();
const display=d=>new Date(d+"T12:00:00Z").toLocaleDateString(undefined,{weekday:"short",day:"numeric",month:"short",timeZone:"UTC"});
const dayText=d=>new Date(d+"T12:00:00Z").toLocaleDateString(undefined,{weekday:"long",timeZone:"UTC"});
const node=(tag,text,cls)=>{const el=document.createElement(tag);if(text!==undefined)el.textContent=String(text);if(cls)el.className=cls;return el};
async function json(url,options){const r=await fetch(url,{cache:"no-store",...options});const data=await r.json().catch(()=>({}));if(!r.ok)throw Error(data.error||"Source request failed");return data}
function fillOptions(select,placeholder){
 select.replaceChildren();
 if(placeholder)select.add(new Option(placeholder,"all"));
 for(const learner of learners)select.add(new Option(learner.display_name||learner.id,learner.id));
}
async function loadLearners(){
 const data=await json("/api/state");
 learners=Array.isArray(data.learners)?data.learners:[];
 fillOptions($("learner"),"Everyone");fillOptions($("task-learner"));
 const chosen=new URLSearchParams(location.search).get("learner");
 if(chosen&&learners.some(x=>x.id===chosen))selected=chosen;
 $("learner").value=selected;
 if(selected!=="all")$("task-learner").value=selected;
 if(!learners.length){$("task-feedback").textContent="Add a learner in School Home before creating a task.";$("add").disabled=true}
}
function refreshView(){
 const week=core.week(monday),filtered=tasks.filter(x=>core.forLearner(x,selected));
 const m=core.metrics(filtered,selected);
 $("total").textContent=String(m.total);$("done").textContent=String(m.done);
 $("remaining").textContent=String(m.remaining);
 $("planned").textContent=m.plannedMinutes+" min";
 $("week-anchor").value=monday;
 $("week-title").textContent=display(week[0])+" — "+display(week[6]);
 const grid=$("week-grid");grid.replaceChildren();
 for(const date of week){
  const rows=filtered.filter(task=>task.date===date);
  const day=node("article",undefined,"day"+(date===today?" today":""));
  const header=node("div",undefined,"day-header");
  header.append(node("strong",dayText(date)),node("time",display(date)));
  const tally=core.metrics(rows,selected);
  day.append(header,node("p",rows.length?tally.done+" / "+rows.length+" marked done":"No saved tasks","day-count"));
  if(!rows.length)day.append(node("p","A blank day is not evidence of no learning.","empty"));
  for(const task of rows){
   const row=node("label",undefined,"task"+(task.status==="done"?" done":""));
   const cb=document.createElement("input");cb.type="checkbox";cb.checked=task.status==="done";
   cb.setAttribute("aria-label","Mark "+task.title+" done");
   const content=node("span",task.title||"Untitled task");
   const whom=learners.filter(x=>Array.isArray(task.learner_ids)&&task.learner_ids.includes(x.id)).map(x=>x.display_name);
   const detail=node("small",(task.scope==="shared"?"Shared · ":"")+
     (whom.length?whom.join(", ")+" · ":"")+
     (task.planned_minutes?task.planned_minutes+" min planned":"No planned time"));
   content.append(detail);row.append(cb,content);
   cb.addEventListener("change",()=>patch(task,cb));
   day.append(row);
  }
  grid.append(day);
 }
}
async function loadWeek(){
 const serial=++revision,dates=new Set(core.week(monday));
 $("source-state").textContent="Reading saved tasks from Online School…";
 try{
  const data=await json("/api/tasks");
  if(serial!==revision)return;
  if(!Array.isArray(data.tasks))throw Error("Task source format unavailable");
  tasks=data.tasks.filter(t=>dates.has(t.date));
  refreshView();
  $("source-state").textContent="Showing persisted task records only · Week beginning "+monday;
 }catch(err){if(serial===revision){tasks=[];refreshView();$("source-state").textContent="Task source unavailable: "+err.message+". No absence claim is implied."}}
}
async function patch(task,checkbox){
 if(busy){checkbox.checked=task.status==="done";return}
 busy=true;checkbox.disabled=true;
 try{
  await json("/api/tasks/"+encodeURIComponent(task.id),{method:"PATCH",headers:{"Content-Type":"application/json"},body:JSON.stringify({status:checkbox.checked?"done":"todo"})});
  await loadWeek();
 }catch(err){checkbox.checked=task.status==="done";$("source-state").textContent="Change was not saved: "+err.message}
 finally{busy=false;checkbox.disabled=false}
}
function shift(days){const next=new Date(Date.parse(monday+"T12:00:00Z")+days*86400000);monday=core.monday(next.toISOString().slice(0,10));loadWeek()}
$("previous-week").addEventListener("click",()=>shift(-7));
$("next-week").addEventListener("click",()=>shift(7));
$("this-week").addEventListener("click",()=>{monday=core.monday(localDay());loadWeek()});
$("week-anchor").addEventListener("change",()=>{try{monday=core.monday($("week-anchor").value);loadWeek()}catch(err){$("source-state").textContent=err.message}});
$("learner").addEventListener("change",()=>{selected=$("learner").value;refreshView()});
$("print").addEventListener("click",()=>window.print());
$("new-task").addEventListener("submit",async ev=>{
 ev.preventDefault();if(busy)return;
 const title=$("task-title").value.trim(),learnerId=$("task-learner").value,date=$("task-date").value;
 if(!title||!learnerId){$("task-feedback").textContent="Choose a learner and task title.";return}
 const raw=$("task-minutes").value.trim(),minutes=raw?Number(raw):null;
 if(raw&&(!Number.isInteger(minutes)||minutes<0||minutes>1440)){$("task-feedback").textContent="Planned minutes must be between 0 and 1440.";return}
 busy=true;$("add").disabled=true;$("task-feedback").textContent="Saving task…";
 try{
  await json("/api/tasks",{method:"POST",headers:{"Content-Type":"application/json"},
   body:JSON.stringify({date,title,learner_ids:[learnerId],scope:"individual",kind:"academic",status:"todo",
    planned_minutes:minutes,notes:"",source:"family-command-center",meta:{}})});
  $("task-title").value="";$("task-minutes").value="";
  monday=core.monday(date);
  await loadWeek();
  $("task-feedback").textContent="Saved. The task is available in School Home.";
 }catch(err){$("task-feedback").textContent="Could not save: "+err.message}
 finally{busy=false;$("add").disabled=!learners.length}
});
$("task-date").value=today;
(async()=>{try{await loadLearners();await loadWeek()}catch(err){$("source-state").textContent="Learner source unavailable: "+err.message}})();
})();