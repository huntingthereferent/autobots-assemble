const $=s=>document.querySelector(s);
const templateFields=$("#template-fields"), editor=$("#question-editor"), list=$("#worksheet-items"), answers=$("#answer-items"), error=$("#worksheet-error"), library=$("#worksheet-library");
let worksheet=null;

const fieldSets={
 arithmetic:`<label>Describe the math worksheet<textarea id="math-prompt" rows="3" placeholder="Addition and subtraction within 20 for 1st grade"></textarea></label><div class="form-grid"><label>Grade<select id="grade"><option value="auto">Auto</option><option value="K">Kindergarten</option><option value="1">1st</option><option value="2">2nd</option><option value="3">3rd</option><option value="4">4th</option><option value="5">5th</option><option value="6">6th</option><option value="7">7th</option><option value="8">8th</option><option value="9">9th</option><option value="10">10th</option><option value="11">11th</option><option value="12">12th</option><option value="adult">Adult / unbounded</option></select></label><label>Topic<select id="math-topic"><option value="auto">Auto</option><option value="addition">Addition</option><option value="subtraction">Subtraction</option><option value="multiplication">Multiplication</option><option value="division">Division</option><option value="mixed">Mixed arithmetic</option><option value="fractions">Fractions</option><option value="decimals">Decimals</option><option value="percent">Percent</option><option value="algebra">Algebra</option><option value="geometry">Geometry</option><option value="time">Time</option><option value="money">Money</option><option value="measurement">Measurement</option><option value="place-value">Place value</option><option value="comparison">Comparison</option><option value="patterns">Patterns</option><option value="word-problems">Word problems</option></select></label></div><div class="form-grid"><label>Question type<select id="question-type"><option value="short-answer">Short answer</option><option value="single-choice">Single choice</option><option value="fill-blank">Fill blank</option><option value="mixed">Mixed</option></select></label><label>Questions<input id="count" type="number" min="1" max="60" value="10"></label></div><label>Language<select id="language"><option value="English">English</option></select></label>`,
 spelling:`<label>Words<textarea id="words" rows="6" placeholder="because, friend, beautiful"></textarea></label>`,
 vocabulary:`<label>Terms + definitions<textarea id="terms" rows="7" placeholder="evaporation: liquid changing into gas&#10;condensation: gas changing into liquid"></textarea></label>`,
 reading:`<label>Source passage<textarea id="passage" rows="12" placeholder="Paste the text the learner should work through."></textarea></label>`,
 handwriting:`<label>Copy text<textarea id="copy-text" rows="7" placeholder="One phrase or sentence per line"></textarea></label><label>Rows<input id="count" type="number" min="1" max="60" value="8"></label>`,
 custom:`<label>Questions + answers<textarea id="custom-items" rows="9" placeholder="What is 2 + 2? :: 4&#10;Explain evaporation. :: Liquid changes into gas."></textarea></label><label>Response lines<input id="response-lines" type="number" min="1" max="8" value="2"></label>`
};

function renderFields(){templateFields.innerHTML=fieldSets[$("#template").value]||"";if($("#template").value==="arithmetic")$("#columns").value="2";else $("#columns").value="1"}
function payload(){
 const get=id=>$(id)?.value??"";
 return {template:$("#template").value,level:$("#level").value,variant:$("#variant").value,title:$("#ws-title").value,knowledge_goal:$("#knowledge-goal").value,learner:$("#learner").value,subject:$("#subject").value,instructions:$("#instructions").value,page_size:$("#page-size").value,columns:Number($("#columns").value),seed:Number($("#seed").value||1),include_answer_key:$("#answer-key-toggle").checked,operation:get("#operation"),math_prompt:get("#math-prompt"),math_topic:get("#math-topic"),grade:get("#grade"),question_type:get("#question-type"),language:get("#language"),count:Number(get("#count")||0),words:get("#words"),terms:get("#terms"),passage:get("#passage"),copy_text:get("#copy-text"),custom_items:get("#custom-items"),response_lines:Number(get("#response-lines")||2)};
}
async function generate(){
 error.hidden=true;
 const r=await fetch("/api/worksheets/generate",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload())});
 const data=await r.json().catch(()=>({}));
 if(!r.ok){error.textContent=data.error||"Could not generate worksheet";error.hidden=false;return}
 worksheet=data; renderAll();
}
function renderAll(){
 if(!worksheet)return;
 $("#preview-title").textContent=worksheet.title;
 $("#answer-title").textContent=worksheet.title+" — Answer Key";
 $("#preview-subtitle").textContent=[worksheet.subject,worksheet.learner&&("Learner: "+worksheet.learner)].filter(Boolean).join(" · ");
 $("#preview-goal").textContent=worksheet.knowledge_goal?("Knowledge goal: "+worksheet.knowledge_goal):"";
 $("#preview-instructions").textContent=worksheet.instructions||"";
 $("#passage-block").hidden=!worksheet.passage;$("#preview-passage").textContent=worksheet.passage||"";
 $("#worksheet-paper").dataset.size=worksheet.page_size;$("#answer-paper").dataset.size=worksheet.page_size;
 list.className="worksheet-items columns-"+worksheet.columns;list.innerHTML="";answers.innerHTML="";
 worksheet.items.forEach((item,i)=>{
  const li=document.createElement("li");li.className="worksheet-item";
  const p=document.createElement("div");p.className="prompt";p.textContent=item.prompt;li.append(p);
  const lines=document.createElement("div");lines.className="response-lines"+(item.kind==="handwriting"?" handwriting-lines":"");
  for(let n=0;n<(item.lines||1);n++){const line=document.createElement("div");line.className="response-line";lines.append(line)}
  li.append(lines);list.append(li);
  const ai=document.createElement("li");const av=document.createElement("div");av.className="answer-value";av.textContent=item.answer||"Teacher review.";ai.append(av);answers.append(ai);
 });
 $("#preview-meta").textContent=`Variant ${worksheet.variant} · ${worksheet.level} · seed ${worksheet.seed}`;
 $("#answer-paper").hidden=!worksheet.include_answer_key;
 renderEditor();
}
function renderEditor(){
 editor.innerHTML=""; if(!worksheet)return;
 worksheet.items.forEach((item,i)=>{
  const row=document.createElement("div");row.className="question-row";
  row.innerHTML=`<div class="question-row-head"><strong>Question ${i+1}</strong><button class="danger" type="button">Remove</button></div><textarea rows="3"></textarea><input placeholder="Answer / key"><label>Response lines <input type="number" min="1" max="12"></label>`;
  const ta=row.querySelector("textarea"),ans=row.querySelector('input[placeholder]'),ln=row.querySelector('input[type="number"]');
  ta.value=item.prompt;ans.value=item.answer;ln.value=item.lines||1;
  ta.oninput=()=>{item.prompt=ta.value;renderAllPreviewOnly()};ans.oninput=()=>{item.answer=ans.value;renderAllPreviewOnly()};ln.oninput=()=>{item.lines=Math.max(1,Number(ln.value||1));renderAllPreviewOnly()};
  row.querySelector(".danger").onclick=()=>{worksheet.items.splice(i,1);renderAll()};editor.append(row);
 });
}
function renderAllPreviewOnly(){
 const savedScroll=editor.scrollTop;
 $("#preview-title").textContent=worksheet.title;list.innerHTML="";answers.innerHTML="";
 worksheet.items.forEach(item=>{
  const li=document.createElement("li");li.className="worksheet-item";const p=document.createElement("div");p.className="prompt";p.textContent=item.prompt;li.append(p);
  const lines=document.createElement("div");lines.className="response-lines"+(item.kind==="handwriting"?" handwriting-lines":"");for(let n=0;n<(item.lines||1);n++){const x=document.createElement("div");x.className="response-line";lines.append(x)}li.append(lines);list.append(li);
  const ai=document.createElement("li");ai.textContent=item.answer||"Teacher review.";answers.append(ai);
 });editor.scrollTop=savedScroll;
}
async function save(){
 if(!worksheet)return;
 worksheet.title=$("#ws-title").value||worksheet.title;worksheet.knowledge_goal=$("#knowledge-goal").value;worksheet.instructions=$("#instructions").value;worksheet.learner=$("#learner").value;worksheet.subject=$("#subject").value;worksheet.page_size=$("#page-size").value;worksheet.columns=Number($("#columns").value);worksheet.include_answer_key=$("#answer-key-toggle").checked;worksheet.variant=$("#variant").value;
 const r=await fetch("/api/worksheets",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(worksheet)});const data=await r.json();if(r.ok){worksheet=data;renderAll();loadLibrary()}else alert(data.error||"Could not save")}
async function loadLibrary(){const r=await fetch("/api/worksheets");const data=await r.json();library.innerHTML="";(data.worksheets||[]).forEach(ws=>{const b=document.createElement("button");b.className="library-item";b.type="button";b.innerHTML=`<strong>${ws.title}</strong><span>${ws.template||"custom"} · ${ws.level||"standard"} · ${ws.items?.length||0} items</span>`;b.onclick=()=>{worksheet=ws;hydrate();renderAll()};library.append(b)})}
function hydrate(){if(!worksheet)return;$("#template").value=worksheet.template||"custom";renderFields();$("#level").value=worksheet.level||"standard";$("#variant").value=worksheet.variant||"A";$("#ws-title").value=worksheet.title||"";$("#knowledge-goal").value=worksheet.knowledge_goal||"";$("#learner").value=worksheet.learner||"";$("#subject").value=worksheet.subject||"";$("#instructions").value=worksheet.instructions||"";$("#page-size").value=worksheet.page_size||"letter";$("#columns").value=String(worksheet.columns||1);$("#seed").value=worksheet.seed||1;$("#answer-key-toggle").checked=worksheet.include_answer_key!==false}
$("#template").onchange=renderFields;$("#generate-worksheet").onclick=generate;$("#save-worksheet").onclick=save;$("#print-worksheet").onclick=()=>window.print();$("#answer-key-toggle").onchange=()=>{if(worksheet){worksheet.include_answer_key=$("#answer-key-toggle").checked;renderAll()}};$("#columns").onchange=()=>{if(worksheet){worksheet.columns=Number($("#columns").value);renderAll()}};$("#page-size").onchange=()=>{if(worksheet){worksheet.page_size=$("#page-size").value;renderAll()}};
$("#add-question").onclick=()=>{if(!worksheet)worksheet={...payload(),items:[],title:$("#ws-title").value||"Untitled Worksheet",worksheet_id:""};worksheet.items.push({prompt:"New question",answer:"",kind:"response",lines:2});renderAll()};
renderFields();
const worksheetParams=new URLSearchParams(window.location.search);
const learnerParam=worksheetParams.get("learner");
const adultMode=worksheetParams.get("mode")==="adult";
if(learnerParam)$("#learner").value=learnerParam;
if(adultMode){
  const grade=$("#grade");
  if(grade)grade.value="adult";
  $("#level").value="challenge";
  $("#knowledge-goal").placeholder="Follow any relation as far as it needs to go";
}
loadLibrary();generate();
