"use strict";
(function(){
const $=id=>document.getElementById(id),core=window.SchoolReading;
let learner="",current=core.get("seed"),ownText="",saveSerial=0,busy=false;
const voice=window.speechSynthesis,canSpeak=Boolean(voice&&window.SpeechSynthesisUtterance);
function say(text){
 if(!canSpeak){$("voice-state").textContent="Voice not available in this browser. You can still read and tap the words.";return;}
 voice.cancel();
 const phrase=core.speakable(text);if(!phrase)return;
 const utterance=new SpeechSynthesisUtterance(phrase);utterance.rate=.82;utterance.lang="en-US";
 voice.speak(utterance);
 $("voice-state").textContent="Playing the selected text. Stop voice whenever you like.";
}
function render(){
 const text=ownText||current.text;
 $("story-title").textContent=ownText?"Your own passage":current.title;
 $("story-level").textContent=ownText?"PERSONAL PRACTICE TEXT":current.level.toUpperCase();
 $("question").textContent=ownText?"What happened in this passage? What did you notice?":current.question;
 const area=$("reading-paper");area.replaceChildren();
 for(const part of core.words(text)){
  if(/^\s+$/.test(part)){area.append(document.createTextNode(part));continue;}
  const button=document.createElement("button");button.type="button";button.className="word";
  button.textContent=part;button.setAttribute("aria-label","Hear word "+core.cleanWord(part));
  button.addEventListener("click",()=>say(core.cleanWord(part)));
  area.append(button);
 }
 $("answer").value="";
 $("reflection").value="";
 saveSerial++;$("save-state").textContent="";
}
async function learners(){
 try{
  const r=await fetch("/api/state",{cache:"no-store"});
  if(!r.ok)throw Error("Learner records unavailable");
  const data=await r.json();
  const records=Array.isArray(data.learners)?data.learners:[];
  $("learner").replaceChildren();
  if(!records.length){$("learner").add(new Option("Add a learner on School Home",""));return}
  for(const record of records)$("learner").add(new Option(record.display_name||record.id,record.id));
  const param=new URLSearchParams(location.search).get("learner");
  if(records.some(x=>x.id===param))$("learner").value=param;
  learner=$("learner").value;$("save").disabled=false;
 }catch(err){$("save-state").textContent=err.message;$("learner").replaceChildren(new Option("No learner source",""))}
}
for(const p of core.PASSAGES)$("story").add(new Option(p.label+" · "+p.level,p.id));
$("story").addEventListener("change",()=>{voice?.cancel();current=core.get($("story").value);ownText="";render()});
$("size").addEventListener("change",()=>$("reading-paper").dataset.size=$("size").value);
$("use-custom").addEventListener("click",()=>{
 const chosen=core.speakable($("custom-text").value);
 if(!chosen){$("save-state").textContent="Write a passage first.";return}
 voice?.cancel();ownText=chosen;render();
});
$("restore").addEventListener("click",()=>{voice?.cancel();ownText="";render()});
$("listen").addEventListener("click",()=>say(ownText||current.text));
$("stop").addEventListener("click",()=>{voice?.cancel();$("voice-state").textContent="Voice stopped."});
$("learner").addEventListener("change",()=>{learner=$("learner").value;saveSerial++;$("save").disabled=!learner});
$("save").addEventListener("click",async()=>{
 if(!learner||busy)return;
 const note=$("answer").value.trim(),reflection=$("reflection").value.trim();
 if(!note&&!reflection){$("save-state").textContent="Write what happened or what you noticed first.";return}
 busy=true;$("save").disabled=true;
 const serial=++saveSerial,owner=learner,story=ownText?"Reader-provided passage":current.title;
 $("save-state").textContent="Saving reading observation…";
 const payload={learner_id:owner,referent:"Reading Room / "+story,
  observed:"Learner response: "+(note||"No retelling entered.")+(reflection?" Observation: "+reflection:""),
  supports:[],contradicts:[],provenance:["online-school:reading-room:v1"]};
 try{
  const r=await fetch("/api/observations",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});
  const data=await r.json().catch(()=>({}));
  if(!r.ok)throw Error(data.error||"Could not save reading observation");
  if(serial===saveSerial&&learner===owner)$("save-state").textContent="Saved to this reader’s observations.";
 }catch(err){if(serial===saveSerial)$("save-state").textContent=err.message}
 finally{busy=false;$("save").disabled=!learner}
});
render();learners();
})();