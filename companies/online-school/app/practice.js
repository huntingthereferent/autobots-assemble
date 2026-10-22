"use strict";
(function(){
const core=window.SchoolPractice, $=id=>document.getElementById(id);
let track="numbers",level="starter",problem=null,attempts=0,firstTry=0,tries=0,learner="",busy=false,saveRevision=0;
const feedback=(msg,kind)=>{$("feedback").textContent=msg;$("feedback").dataset.kind=kind||""};
function showScore(){
 $("attempts").textContent=String(attempts);
 $("first-try").textContent=String(firstTry);
 $("save-session").disabled=!learner||attempts===0||busy;
}
function next(){
 problem=core.newProblem(track,level);
 tries=0;
 $("question-prompt").textContent=problem.prompt;
 $("question-detail").textContent=problem.detail;
 $("activity-tag").textContent=track==="numbers"?"NUMBER LAB":"WORD LAB";
 $("question-number").textContent="Question "+(attempts+1);
 $("response").value="";
 $("response").disabled=false;
 $("check").disabled=false;
 $("next").disabled=true;
 feedback("Try it your way.");
 $("response").focus();
}
function restart(){
 attempts=0;firstTry=0;saveRevision++;$("save-status").textContent="";
 showScore();next();
}
async function readLearners(){
 try{
  const response=await fetch("/api/state",{cache:"no-store"});
  if(!response.ok)throw Error("Learner records are unavailable");
  const data=await response.json();
  const records=Array.isArray(data.learners)?data.learners:[];
  $("learner").replaceChildren();
  if(!records.length){
    $("learner").add(new Option("Add a learner in School Home",""));
    $("save-status").textContent="Practice is available, but recording an observation needs a learner.";
    showScore();return;
  }
  const chosen=new URLSearchParams(location.search).get("learner");
  for(const item of records){const option=new Option(item.display_name||item.id,item.id);$("learner").add(option)}
  if(records.some(item=>item.id===chosen))$("learner").value=chosen;
  learner=$("learner").value;
  showScore();
 }catch(err){
  $("learner").replaceChildren(new Option("Learner source unavailable",""));
  $("save-status").textContent=err.message;
  showScore();
 }
}
$("response-form").addEventListener("submit",event=>{
 event.preventDefault();
 if(!problem||$("check").disabled)return;
 tries++;
 if(core.correct(problem,$("response").value)){
   attempts++;
   if(tries===1)firstTry++;
   feedback(tries===1?"Yes! You got it on your first try.":"You worked it out! Nice retry.","correct");
   $("check").disabled=true;
   $("response").disabled=true;
   $("next").disabled=false;
   showScore();
 }else{
   feedback("Not quite. You can change your answer, or ask for a hint.","retry");
   $("response").focus();
 }
});
$("hint").addEventListener("click",()=>{if(problem)feedback(problem.hint,"hint")});
$("next").addEventListener("click",next);
$("restart").addEventListener("click",restart);
$("learner").addEventListener("change",()=>{learner=$("learner").value;restart()});
$("level").addEventListener("change",()=>{level=$("level").value;restart()});
document.querySelectorAll("[data-track]").forEach(button=>button.addEventListener("click",()=>{
 track=button.dataset.track;
 document.querySelectorAll("[data-track]").forEach(b=>b.classList.toggle("chosen",b===button));
 $("level").hidden=track==="words";
 $("level-label").hidden=track==="words";
 $("response").placeholder=track==="words"?"Write the word":"Type your answer";
 restart();
}));
$("save-form").addEventListener("submit",async event=>{
 event.preventDefault();
 if(busy||!learner||attempts===0)return;
 busy=true;showScore();$("save-status").textContent="Saving observation…";
 const revision=saveRevision,owner=learner,mode=track,count=attempts,first=firstTry,note=$("session-note").value.trim();
 const payload={learner_id:owner,referent:"Practice Lab / "+(mode==="words"?"word blending":"numbers"),
 observed:count+" practice questions solved; "+first+" answered correctly on the first try."+(note?" Learner note: "+note:" No learner note recorded."),
 supports:[],contradicts:[],provenance:["online-school:practice-lab:v1"]};
 try{
  const r=await fetch("/api/observations",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});
  const data=await r.json().catch(()=>({}));
  if(!r.ok)throw Error(data.error||"Could not save observation");
  if(revision===saveRevision&&owner===learner){
   $("save-status").textContent="Saved to this learner’s observations.";
   $("session-note").value="";
  }
 }catch(err){$("save-status").textContent=err.message}
 finally{busy=false;showScore()}
});
next();readLearners();
})();