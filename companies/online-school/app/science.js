"use strict";
(function(){
const $=id=>document.getElementById(id),core=window.SchoolScience;
let learner="",busy=false,formRevision=0;
const note=message=>$("save-state").textContent=message;
for(const idea of core.CHALLENGES){
 const b=document.createElement("button");b.type="button";b.className="challenge";b.dataset.idea=idea.id;
 const title=document.createElement("strong");title.textContent=idea.title;
 const subtitle=document.createElement("small");subtitle.textContent=idea.question;
 b.append(title,subtitle);
 b.addEventListener("click",()=>{
  for(const sibling of document.querySelectorAll(".challenge"))sibling.classList.toggle("selected",sibling===b);
  $("question").value=idea.question;
  $("materials").textContent=idea.materials;
  $("method-tip").textContent=idea.method;
  formRevision++;note("An idea is not an observation. Record what you actually tried below.");
 });
 $("challenges").append(b);
}
async function loadLearners(){
 try{
  const response=await fetch("/api/state",{cache:"no-store"});
  if(!response.ok)throw Error("Learner source unavailable.");
  const data=await response.json();const rows=Array.isArray(data.learners)?data.learners:[];
  $("learner").replaceChildren();
  if(!rows.length){$("learner").add(new Option("Add a learner in School Home",""));return}
  for(const l of rows)$("learner").add(new Option(l.display_name||l.id,l.id));
  const requested=new URLSearchParams(location.search).get("learner");
  if(rows.some(l=>l.id===requested))$("learner").value=requested;
  learner=$("learner").value;
 }catch(err){$("learner").replaceChildren(new Option("Learner source unavailable",""));note(err.message)}
}
$("learner").addEventListener("change",()=>{learner=$("learner").value;formRevision++});
$("clear").addEventListener("click",()=>{
 $("notebook-form").reset();$("materials").textContent="Choose an idea, or plan your own safe activity.";
 $("method-tip").textContent="";
 for(const sibling of document.querySelectorAll(".challenge"))sibling.classList.remove("selected");
 formRevision++;note("");
});
$("notebook-form").addEventListener("submit",async ev=>{
 ev.preventDefault();if(busy)return;
 let payload;
 try{payload=core.buildObservation({learner,question:$("question").value,prediction:$("prediction").value,
  method:$("method").value,observed:$("observed").value,next:$("next").value})}
 catch(err){note(err.message);return}
 busy=true;$("save").disabled=true;
 const requestRevision=++formRevision,requestOwner=learner;
 note("Saving the observation you recorded…");
 try{
  const response=await fetch("/api/observations",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});
  const data=await response.json().catch(()=>({}));if(!response.ok)throw Error(data.error||"Save failed");
  if(requestRevision===formRevision&&learner===requestOwner)note("Saved to this learner’s observations.");
 }catch(err){if(requestRevision===formRevision)note("Not saved: "+err.message)}
 finally{busy=false;$("save").disabled=false}
});
loadLearners();
})();