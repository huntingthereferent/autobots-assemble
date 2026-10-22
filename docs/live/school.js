"use strict";
(function(){
  const $ = id => document.getElementById(id);
  const KEY = "online-school-browser-v1";
  const empty = () => ({version:1,learners:[],tasks:[],notes:[],attempts:[],creations:[],selected:""});
  const safeArray = x => Array.isArray(x) ? x : [];
  function load(){
    try {
      const raw = localStorage.getItem(KEY);
      if (!raw) return empty();
      const data = JSON.parse(raw);
      if (data.version !== 1) throw Error("Unsupported record version");
      return {version:1,learners:safeArray(data.learners),tasks:safeArray(data.tasks),
        notes:safeArray(data.notes),attempts:safeArray(data.attempts),creations:safeArray(data.creations),selected:String(data.selected||"")};
    } catch(err){$("storage-state").textContent="STORAGE NOT READABLE";return empty();}
  }
  let state=load(),storageAvailable=true,view="today";
  let weekAnchor="",practiceProblem=null,practiceTries=0,practiceSolved=false;
  let editingCreationId=null,pattern=Array(8).fill(0),patternTimer=null,patternAudio=null;
  let sparkIndex=0,storyParts=["A curious pony","A floating garden","A mysterious song"];
  const WORDS=[
    {word:"cat",sound:"c · a · t",hint:"A small pet that purrs."},
    {word:"sun",sound:"s · u · n",hint:"It lights the sky."},
    {word:"map",sound:"m · a · p",hint:"It shows where places are."},
    {word:"fish",sound:"f · i · sh",hint:"It swims in water."},
    {word:"ship",sound:"sh · i · p",hint:"It can sail on water."},
    {word:"frog",sound:"f · r · o · g",hint:"It hops and croaks."},
    {word:"rain",sound:"r · ai · n",hint:"It falls from clouds."},
    {word:"moon",sound:"m · oo · n",hint:"It shines in the night sky."}
  ];
  const PASSAGES={
    seed:{title:"The Little Seed",text:"A seed sat in the dirt. It had a little rain. The sun came out. The seed made a green sprout. Soon, a leaf reached for the light.",question:"What changed for the seed? Tell it in your own words."},
    bridge:{title:"The Bridge of Stones",text:"Mara wanted to cross the small stream. The water was too deep for her shoes. She found four flat stones beside the bank. She put them in a line and tested each one. The last stone moved, so Mara chose a wider one. This time the path held.",question:"What problem did Mara notice, and how did she change her plan?"},
    sky:{title:"The Shape of a Shadow",text:"At breakfast, Leo noticed his shadow reached all the way across the porch. By lunchtime, it was short and tucked close to his feet. The porch had not moved. Leo wondered if the Sun's position could explain the change. He decided to draw his shadow at three different times the next day.",question:"What did Leo observe, and what would his next test help him find out?"}
  };
  const CHALLENGES={
    shadow:{question:"Does a shadow stay the same size and direction all day?",materials:"Materials: sunlight, paper, pencil and a safe place to observe.",method:"Suggested method: Mark the same object's shadow at two different times. Record each clock time and shape. Never look directly at the Sun."},
    water:{question:"How does one drop of water behave on different surfaces?",materials:"Materials: a little water, a spoon, a towel and two safe surfaces.",method:"Suggested method: Ask an adult before using household surfaces. Place one drop on each surface; observe how it spreads. Dry everything afterward."},
    paper:{question:"Does folding paper change how much a bridge can hold?",materials:"Materials: paper, two books and light objects such as erasers.",method:"Suggested method: Bridge two books with flat paper, then folded paper. Observe the result with only light objects."}
  };
  const IDEAS=[
    "What if your pony discovered a tiny floating island?",
    "Could you build a paper bridge strong enough for an eraser?",
    "What would a rainstorm sound like if it were made by cats?",
    "Invent a creature who can only talk by drawing shapes.",
    "Can you make a musical pattern with four different notes?",
    "How would you map a secret trail using only pictures?",
    "Write a message from an explorer on a distant moon."
  ];
  const CHARACTERS=["A curious pony","A shy cloud","A singing cat","An inventive fox","A tiny robot","A brave beetle"];
  const PLACES=["a floating garden","an underground library","a moonlit forest","a musical mountain","a candy-colored planet","a secret treehouse"];
  const TWISTS=["a mysterious song","a door with no handle","a map written backwards","a bridge made of moonlight","an unexpected new friend","a clock that skips Tuesdays"];
  const KIND_LABELS={story:"Story",trail:"Trail idea",music:"Music idea",experiment:"Experiment",pattern:"Eight-beat pattern",reading:"Reading thought",other:"New invention"};
  const TONE_NAMES=["Rest","Low C","Middle E","High G","Sparkle C"];
  const TONE_MARKS=["·","●","◆","▲","✦"];
  const TONE_FREQ=[0,261.63,329.63,392,523.25];
  const uid=()=> typeof crypto!=="undefined"&&crypto.randomUUID ? crypto.randomUUID() : String(Date.now())+"-"+String(Math.random()).slice(2);
  function localDay(){
    const n=new Date(),d=new Date(n.getTime()-n.getTimezoneOffset()*60000);
    return d.toISOString().slice(0,10);
  }
  function parseDay(day){
    if(!/^\d{4}-\d{2}-\d{2}$/.test(String(day)))return null;
    const date=new Date(day+"T12:00:00Z");
    return Number.isFinite(date.getTime())&&date.toISOString().slice(0,10)===day?date:null;
  }
  function monday(day){
    const d=parseDay(day)||parseDay(localDay());
    d.setUTCDate(d.getUTCDate()-(d.getUTCDay()+6)%7);
    return d.toISOString().slice(0,10);
  }
  function shift(day,n){
    const d=parseDay(day);
    d.setUTCDate(d.getUTCDate()+n);
    return d.toISOString().slice(0,10);
  }
  function dateLabel(day){
    const d=parseDay(day);
    return d?d.toLocaleDateString(undefined,{month:"short",day:"numeric",weekday:"short",timeZone:"UTC"}):day;
  }
  const learner=()=>state.learners.find(x=>x.id===state.selected);
  function persist(){
    try {localStorage.setItem(KEY,JSON.stringify(state));storageAvailable=true;$("storage-state").textContent="SAVED IN THIS BROWSER";return true;}
    catch(err){storageAvailable=false;$("storage-state").textContent="NOT SAVED · STORAGE BLOCKED";return false;}
  }
  function node(tag,text,cls){
    const e=document.createElement(tag);
    if(text!==undefined)e.textContent=String(text);
    if(cls)e.className=cls;
    return e;
  }
  const feedback=(id,message)=>{$(id).textContent=message;};
  function ready(){
    if(learner())return true;
    $("setup-note").hidden=false;
    $("setup-note").textContent="Add or choose a learning-space nickname before saving work.";
    return false;
  }
  function renderLearners(){
    const select=$("learner");
    select.replaceChildren(new Option("Choose a space",""));
    state.learners.forEach(p=>select.add(new Option(p.name,p.id)));
    if(!learner())state.selected="";
    select.value=state.selected;
    $("setup-note").hidden=Boolean(learner());
    if(!learner())$("setup-note").textContent="Add a learning-space nickname to begin. Avoid names or private details on a shared device.";
  }
  function ownToday(){
    return state.tasks.filter(t=>t.learnerId===state.selected&&t.day===$("school-date").value);
  }
  function saveCreation(kind,title,body,extra){
    if(!learner())return false;
    state.creations.push({id:uid(),learnerId:state.selected,day:$("school-date").value,
      kind,title:String(title).slice(0,100),body:String(body).slice(0,5000),...(extra||{})});
    const saved=persist();renderCreations();
    return saved;
  }
  function kindName(kind){return KIND_LABELS[kind]||"Creative idea";}
  function linkFor(kind){return kind==="trail"?"pony-trail.html":kind==="music"||kind==="pattern"?"cat-keyboard.html":null;}
  function makeCreationCard(item,compact){
    const card=node("article",undefined,"creation-card");
    card.append(node("span",kindName(item.kind)+" · "+dateLabel(item.day||localDay()),"creation-label"));
    card.append(node("strong",item.title));
    card.append(node("p",compact?String(item.body||"").slice(0,135)+(String(item.body||"").length>135?"…":""):item.body||""));
    const actions=node("div",undefined,"creation-actions");
    const open=node("button",item.kind==="pattern"?"Play again ♫":"Continue ✎");
    open.type="button";open.addEventListener("click",()=>{
      if(item.kind==="pattern"&&Array.isArray(item.tones)&&item.tones.length===8&&item.tones.every(v=>Number.isInteger(v)&&v>=0&&v<TONE_NAMES.length)){
        pattern=item.tones.slice();renderPattern();show("pattern");
      }else{
        editingCreationId=item.id;
        $("creation-kind").value=Object.hasOwn(KIND_LABELS,item.kind)&&item.kind!=="pattern"&&item.kind!=="reading"?item.kind:"other";
        $("creation-title").value=item.title;$("creation-body").value=item.body||"";
        $("save-creation").textContent="Save changes ✦";$("cancel-creation-edit").hidden=false;
        show("create");$("creation-title").focus();
      }
    });actions.append(open);
    const href=linkFor(item.kind);
    if(href){const a=node("a",item.kind==="trail"?"Visit Pony Trail ↗":"Visit Meow Lab ↗");a.href=href;actions.append(a);}
    if(!compact){
      const remove=node("button","Remove");remove.type="button";
      remove.addEventListener("click",()=>{
        if(!confirm("Remove this creation from this browser?"))return;
        state.creations=state.creations.filter(x=>x.id!==item.id);
        if(editingCreationId===item.id)resetCreationForm();
        persist();renderCreations();
      });actions.append(remove);
    }
    card.append(actions);return card;
  }
  function renderCreations(){
    const items=learner()?safeArray(state.creations).filter(x=>x.learnerId===state.selected).slice().reverse():[];
    $("creation-count").textContent=String(items.length);
    const preview=$("play-creations"),library=$("creation-library");
    preview.replaceChildren();library.replaceChildren();
    if(!items.length){
      preview.append(node("p","Nothing saved yet. Make a story, a beat, or a discovery!","creation-empty"));
      library.append(node("p","Your ideas will live here. Start with something small.","creation-empty"));return;
    }
    items.slice(0,3).forEach(item=>preview.append(makeCreationCard(item,true)));
    items.forEach(item=>library.append(makeCreationCard(item,false)));
  }
  function resetCreationForm(){
    editingCreationId=null;$("creation-form").reset();
    $("save-creation").textContent="Save to my collection ✦";
    $("cancel-creation-edit").hidden=true;
  }
  function renderIdea(){
    $("spark-text").textContent=IDEAS[sparkIndex%IDEAS.length];
  }
  function renderStorySparks(){
    $("spark-character").textContent=storyParts[0];
    $("spark-place").textContent=storyParts[1];
    $("spark-twist").textContent=storyParts[2];
  }
  function stopPattern(){
    if(patternTimer!==null){clearInterval(patternTimer);patternTimer=null;}
    document.querySelectorAll(".pattern-beat").forEach(b=>b.classList.remove("is-playing"));
  }
  function renderPattern(){
    const beats=$("pattern-beats");beats.replaceChildren();
    pattern.forEach((tone,i)=>{
      const button=node("button",undefined,"pattern-beat");button.type="button";button.dataset.tone=String(tone);
      button.setAttribute("aria-label","Beat "+(i+1)+": "+TONE_NAMES[tone]+". Tap to change the note.");
      button.append(node("span",String(i+1)),node("strong",TONE_MARKS[tone]),node("small",TONE_NAMES[tone]));
      button.addEventListener("click",()=>{stopPattern();pattern[i]=(pattern[i]+1)%TONE_MARKS.length;renderPattern();});
      beats.append(button);
    });
  }
  async function playPattern(){
    stopPattern();
    const Audio=window.AudioContext||window.webkitAudioContext;
    if(Audio){try{
      if(!patternAudio)patternAudio=new Audio();
      if(patternAudio.state==="suspended")await patternAudio.resume();
    }catch(err){patternAudio=null;}}
    let index=0;
    function tick(){
      const buttons=$("pattern-beats").querySelectorAll(".pattern-beat");
      buttons.forEach((b,i)=>b.classList.toggle("is-playing",i===index));
      const freq=TONE_FREQ[pattern[index]];
      if(freq&&patternAudio){try{
        const osc=patternAudio.createOscillator(),gain=patternAudio.createGain(),at=patternAudio.currentTime;
        osc.type="sine";osc.frequency.setValueAtTime(freq,at);
        gain.gain.setValueAtTime(.0001,at);gain.gain.exponentialRampToValueAtTime(.11,at+.025);
        gain.gain.exponentialRampToValueAtTime(.0001,at+.24);
        osc.connect(gain);gain.connect(patternAudio.destination);osc.start(at);osc.stop(at+.26);
      }catch(err){$("pattern-feedback").textContent="Audio isn't available; the pattern will still light up."}}
      index++;
      if(index>=8){clearInterval(patternTimer);patternTimer=null;
        setTimeout(()=>{buttons.forEach(b=>b.classList.remove("is-playing"));},310);}
    }
    $("pattern-feedback").textContent=patternAudio?"Hear your eight little beats!":"Watch your pattern dance — sound isn't available here.";
    tick();if(index<8)patternTimer=setInterval(tick,360);
  }
  function renderToday(){
    const tasks=learner()?ownToday():[];
    const done=tasks.filter(t=>t.done).length;
    $("task-ratio").textContent=done+" / "+tasks.length;
    const percent=tasks.length?Math.round(done/tasks.length*100):0;
    $("progress-fill").style.width=percent+"%";
    $("progress-track").setAttribute("aria-valuenow",String(percent));
    $("task-empty").hidden=tasks.length>0;
    const container=$("task-list");container.replaceChildren();
    tasks.forEach(t=>{
      const row=node("article",undefined,"task-row"+(t.done?" done":""));
      const top=node("label",undefined,"task-main");
      const check=node("input");check.type="checkbox";check.checked=Boolean(t.done);
      check.setAttribute("aria-label","Mark "+t.title+" done");
      check.addEventListener("change",()=>{t.done=check.checked;persist();renderToday();renderFamily();});
      const copy=node("span");
      copy.append(node("strong",t.title),node("small",t.subject+" · "+(t.planned===null?"No planned minutes":t.planned+" min planned")));
      top.append(check,copy);row.append(top);
      const time=node("div",undefined,"task-time");
      const label=node("label","Actual min");
      const actual=node("input");actual.type="number";actual.min="0";actual.max="1440";actual.step="1";
      actual.value=t.actual===null||t.actual===undefined?"":String(t.actual);
      actual.setAttribute("aria-label","Actual minutes for "+t.title);
      const save=node("button","Save minutes");
      save.type="button";
      const status=node("span",t.actual===null||t.actual===undefined?"Not logged":t.actual+" min logged","logged");
      save.addEventListener("click",()=>{
        const v=actual.value.trim();
        if(v!==""&&(!/^\d+$/.test(v)||Number(v)>1440)){status.textContent="Use whole minutes from 0 to 1440.";return;}
        t.actual=v===""?null:Number(v);
        persist();status.textContent=t.actual===null?"Actual minutes cleared":t.actual+" min logged";renderFamily();
      });
      const remove=node("button","Remove");remove.type="button";remove.setAttribute("aria-label","Remove "+t.title);
      remove.addEventListener("click",()=>{
        if(!confirm("Remove this saved task?"))return;
        state.tasks=state.tasks.filter(row=>row.id!==t.id);
        persist();renderToday();renderFamily();
      });
      time.append(label,actual,save,status,remove);row.append(time);container.append(row);
    });
  }
  function createPractice(){
    if(!learner()){practiceProblem=null;$("question").textContent="Choose a learner to begin";return;}
    const track=$("practice-mode").value,level=$("practice-level").value;
    if(track==="words"){
      const w=WORDS[Math.floor(Math.random()*WORDS.length)];
      practiceProblem={track,answer:w.word,detail:w.sound,hint:w.hint};
    }else{
      const limit=level==="starter"?10:level==="builder"?30:12;
      let a=Math.floor(Math.random()*(limit+1)),b=Math.floor(Math.random()*(limit+1));
      const mul=level==="explorer"&&Math.random()>.35,sub=!mul&&Math.random()>.5;
      if(sub&&b>a)[a,b]=[b,a];
      const symbol=mul?"×":sub?"−":"+";
      practiceProblem={track,answer:String(mul?a*b:sub?a-b:a+b),
        detail:a+" "+symbol+" "+b+" = ?",hint:mul?"Try "+b+" groups of "+a+".":sub?"Count backward "+b+" from "+a+".":"Start at "+a+" and count forward "+b+"."};
    }
    practiceTries=0;practiceSolved=false;$("answer").disabled=false;$("check-answer").disabled=false;
    $("question-type").textContent=track==="words"?"BLEND THE SOUNDS":"SOLVE THE QUESTION";
    $("question").textContent=practiceProblem.detail;
    $("question-instruction").textContent=track==="words"?"Say each sound slowly and blend it.":"Take your time and show how you know.";
    $("answer").value="";feedback("practice-feedback","Trying is part of learning.");
    renderPracticeSummary();
  }
  function renderPracticeSummary(){
    const attempts=state.attempts.filter(a=>a.learnerId===state.selected&&a.day===$("school-date").value);
    const first=attempts.filter(a=>a.correct&&a.firstTry).length;
    $("practice-summary").textContent=attempts.length+" submitted answer"+(attempts.length===1?"":"s")+" today · "+first+" correct on a first try. Practice does not certify mastery.";
  }
  function renderPassage(){
    const p=PASSAGES[$("passage").value]||PASSAGES.seed;
    $("story-title").textContent=p.title;$("story-text").textContent=p.text;
    $("reading-question").textContent=p.question;
    $("story-text").style.fontSize=$("text-size").value+"em";
  }
  function renderScience(){
    const x=CHALLENGES[$("investigation").value]||CHALLENGES.shadow;
    $("science-question").textContent=x.question;
    $("materials").textContent=x.materials;
    $("method").textContent=x.method;
  }
  function renderFamily(){
    if(!weekAnchor)weekAnchor=monday($("school-date").value);
    const week=Array.from({length:7},(_,i)=>shift(weekAnchor,i));
    $("week-heading").textContent=dateLabel(week[0])+" — "+dateLabel(week[6]);
    const tasks=learner()?state.tasks.filter(t=>t.learnerId===state.selected&&week.includes(t.day)):[];
    const observed=tasks.filter(t=>Number.isInteger(t.actual)&&t.actual>=0);
    const planned=tasks.filter(t=>Number.isInteger(t.planned)&&t.planned>=0);
    $("week-tasks").textContent=tasks.length;
    $("week-done").textContent=tasks.filter(t=>t.done).length;
    $("week-planned").textContent=planned.length?planned.reduce((n,t)=>n+t.planned,0):"—";
    $("week-actual").textContent=observed.length?observed.reduce((n,t)=>n+t.actual,0):"—";
    const container=$("week-list");container.replaceChildren();
    week.forEach(day=>{
      const rows=tasks.filter(t=>t.day===day),card=node("article",undefined,"day-card"),h=node("header");
      h.append(node("span",dateLabel(day)),node("span",rows.filter(t=>t.done).length+" / "+rows.length+" done"));
      card.append(h);
      if(!rows.length)card.append(node("p","No saved tasks; this does not mean no learning occurred."));
      else{const list=node("ul");rows.forEach(t=>{
        const actual=t.actual===null||t.actual===undefined?"actual time not entered":t.actual+" min actual";
        list.append(node("li",t.subject+" · "+t.title+" · "+actual));
      });card.append(list);}
      container.append(card);
    });
    const noteList=$("notes-list");noteList.replaceChildren();
    const notes=learner()?state.notes.filter(n=>n.learnerId===state.selected&&week.includes(n.day)):[];
    if(!notes.length)noteList.append(node("p","No reading or science notes were saved for this week.","empty"));
    notes.slice().reverse().forEach(n=>{
      const card=node("article",undefined,"note-card");
      card.append(node("strong",dateLabel(n.day)+" · "+n.type+" · "+n.title),node("p",n.text));
      noteList.append(card);
    });
  }
  function show(name){
    view=name;
    document.querySelectorAll(".panel").forEach(p=>{p.hidden=p.id!=="panel-"+name;});
    document.querySelectorAll("[data-page]").forEach(b=>{
      if(b.dataset.page===name)b.setAttribute("aria-current","page");
      else b.removeAttribute("aria-current");
    });
    document.body.classList.toggle("is-play",name==="play");
    if(name!=="pattern")stopPattern();
    if(name==="family")renderFamily();
  }
  function render(){
    renderLearners();renderToday();renderFamily();renderPracticeSummary();renderCreations();
    if(!practiceProblem&&learner())createPractice();
    if(!learner()){$("question").textContent="Choose a learner to begin";}
  }
  $("school-date").value=localDay();weekAnchor=monday(localDay());
  $("new-learner").addEventListener("submit",event=>{
    event.preventDefault();const name=$("nickname").value.trim();
    if(name.length<1||name.length>40)return;
    const record={id:uid(),name};
    state.learners.push(record);state.selected=record.id;$("nickname").value="";
    persist();practiceProblem=null;render();show("play");
  });
  $("learner").addEventListener("change",()=>{state.selected=$("learner").value;persist();practiceProblem=null;render();});
  $("school-date").addEventListener("change",()=>{
    if(!parseDay($("school-date").value)){$("school-date").value=localDay();}
    weekAnchor=monday($("school-date").value);render();
  });
  document.querySelectorAll("[data-page]").forEach(b=>b.addEventListener("click",()=>show(b.dataset.page)));
  document.querySelectorAll("[data-open]").forEach(button=>button.addEventListener("click",()=>{
    const target=button.dataset.open;
    if(button.dataset.kind&&$("creation-kind"))$("creation-kind").value=button.dataset.kind;
    show(target);
  }));
  $("spark-next").addEventListener("click",()=>{sparkIndex=(sparkIndex+1)%IDEAS.length;renderIdea();});
  $("spark-use").addEventListener("click",()=>{
    resetCreationForm();$("creation-kind").value="trail";
    $("creation-title").value="An unexpected adventure";
    $("creation-body").value=IDEAS[sparkIndex%IDEAS.length]+"\n\nI wonder what happens next…";
    show("create");$("creation-body").focus();
  });
  $("shuffle-story").addEventListener("click",()=>{
    storyParts=[CHARACTERS[Math.floor(Math.random()*CHARACTERS.length)],
      PLACES[Math.floor(Math.random()*PLACES.length)],
      TWISTS[Math.floor(Math.random()*TWISTS.length)]];
    renderStorySparks();
  });
  $("use-story").addEventListener("click",()=>{
    resetCreationForm();$("creation-kind").value="story";
    $("creation-title").value="A very strange day";
    $("creation-body").value=storyParts[0]+" traveled to "+storyParts[1]+". Then they discovered "+storyParts[2]+".\n\nWhat happened next? ";
    $("creation-body").focus();
  });
  $("creation-form").addEventListener("submit",event=>{
    event.preventDefault();if(!ready())return;
    const title=$("creation-title").value.trim(),body=$("creation-body").value.trim(),kind=$("creation-kind").value;
    if(!title||!body){feedback("creation-feedback","Add a title and some words first.");return;}
    if(editingCreationId){
      const found=state.creations.find(x=>x.id===editingCreationId&&x.learnerId===state.selected);
      if(!found){feedback("creation-feedback","That creation is no longer saved.");resetCreationForm();return;}
      Object.assign(found,{title:title.slice(0,100),body:body.slice(0,5000),kind});
      persist();renderCreations();feedback("creation-feedback","Saved your changes in this browser.");
    }else{
      const saved=saveCreation(kind,title,body);
      feedback("creation-feedback",saved?"Saved! You can come back whenever you like.":"Your browser could not save. Export a backup if possible.");
    }
    resetCreationForm();
  });
  $("cancel-creation-edit").addEventListener("click",()=>{resetCreationForm();feedback("creation-feedback","Ready to make something new.");});
  $("pattern-play").addEventListener("click",playPattern);
  $("pattern-stop").addEventListener("click",()=>{stopPattern();feedback("pattern-feedback","Stopped. Change any beat and play again.");});
  $("pattern-random").addEventListener("click",()=>{stopPattern();pattern=pattern.map(()=>Math.floor(Math.random()*TONE_NAMES.length));renderPattern();feedback("pattern-feedback","Surprise pattern! Tap any beat to change it.");});
  $("pattern-clear").addEventListener("click",()=>{stopPattern();pattern=Array(8).fill(0);renderPattern();feedback("pattern-feedback","A fresh quiet pattern. Build it your way.");});
  $("pattern-save").addEventListener("click",()=>{
    if(!ready())return;
    const body="Eight beats: "+pattern.map(x=>TONE_NAMES[x]).join(" · ");
    const saved=saveCreation("pattern","My eight-beat music",body,{tones:pattern.slice()});
    feedback("pattern-feedback",saved?"Kept in My Creations. Come back and replay it anytime!":"Browser storage was unavailable.");
  });
  $("new-task").addEventListener("submit",event=>{
    event.preventDefault();if(!ready())return;
    const title=$("task-title").value.trim(),raw=$("planned").value.trim();
    if(!title)return;
    if(raw!==""&&(!/^\d+$/.test(raw)||Number(raw)>1440)){feedback("storage-state","INVALID PLANNED MINUTES");return;}
    state.tasks.push({id:uid(),learnerId:state.selected,day:$("school-date").value,title:title.slice(0,120),
      subject:$("task-subject").value,planned:raw===""?null:Number(raw),actual:null,done:false});
    $("task-title").value="";$("planned").value="";persist();renderToday();renderFamily();
  });
  $("practice-mode").addEventListener("change",createPractice);
  $("practice-level").addEventListener("change",createPractice);
  $("next-question").addEventListener("click",createPractice);
  $("hint").addEventListener("click",()=>{if(practiceProblem)feedback("practice-feedback","Hint: "+practiceProblem.hint);});
  $("practice-answer").addEventListener("submit",event=>{
    event.preventDefault();if(!ready()||!practiceProblem||practiceSolved)return;
    const answer=$("answer").value.trim();
    if(!answer)return;
    practiceTries++;
    const correct=answer.toLowerCase().replace(/\s+/g," ")===practiceProblem.answer.toLowerCase();
    state.attempts.push({id:uid(),learnerId:state.selected,day:$("school-date").value,
      type:practiceProblem.track,correct,firstTry:correct&&practiceTries===1});
    if(correct){practiceSolved=true;$("check-answer").disabled=true;$("answer").disabled=true;}
    persist();feedback("practice-feedback",correct?"That works! Try another when ready.":"Not quite. Try again or use a hint.");
    renderPracticeSummary();
  });
  $("passage").addEventListener("change",()=>{$("retell").value="";renderPassage();});
  $("text-size").addEventListener("change",renderPassage);
  $("read-aloud").addEventListener("click",()=>{
    const p=PASSAGES[$("passage").value]||PASSAGES.seed;
    if(!("speechSynthesis" in window)||!("SpeechSynthesisUtterance" in window)){
      feedback("reading-feedback","This browser does not provide read-aloud.");return;
    }
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(new SpeechSynthesisUtterance(p.text));
    feedback("reading-feedback","Reading with your device's voice.");
  });
  $("reading-note").addEventListener("submit",event=>{
    event.preventDefault();if(!ready())return;
    const text=$("retell").value.trim(),passage=PASSAGES[$("passage").value]||PASSAGES.seed;
    if(!text)return;
    state.notes.push({id:uid(),learnerId:state.selected,day:$("school-date").value,type:"Reading",
      title:passage.title,text:text.slice(0,1800)});
    persist();saveCreation("reading","Reading: "+passage.title,text);
    feedback("reading-feedback","Saved to Reading Room notes and My Creations.");
    $("retell").value="";renderFamily();
  });
  $("investigation").addEventListener("change",renderScience);
  $("science-note").addEventListener("submit",event=>{
    event.preventDefault();if(!ready())return;
    const tried=$("tried").value.trim(),observed=$("observed").value.trim(),prediction=$("prediction").value.trim();
    if(!tried||!observed){feedback("science-feedback","Record what you tried and actually observed.");return;}
    const x=CHALLENGES[$("investigation").value]||CHALLENGES.shadow;
    state.notes.push({id:uid(),learnerId:state.selected,day:$("school-date").value,type:"Science",
      title:x.question,text:("Tried: "+tried+". Observed: "+observed+(prediction?". Predicted: "+prediction:"")).slice(0,4000)});
    persist();saveCreation("experiment",x.question,"Tried: "+tried+"\nObserved: "+observed+(prediction?"\nPredicted: "+prediction:""));
    feedback("science-feedback","Saved to your notebook and My Creations.");
    $("tried").value="";$("observed").value="";$("prediction").value="";renderFamily();
  });
  $("previous-week").addEventListener("click",()=>{weekAnchor=shift(weekAnchor,-7);renderFamily();});
  $("next-week").addEventListener("click",()=>{weekAnchor=shift(weekAnchor,7);renderFamily();});
  $("print-week").addEventListener("click",()=>{show("family");window.print();});
  $("export-data").addEventListener("click",()=>{
    const blob=new Blob([JSON.stringify(state,null,2)],{type:"application/json"});
    const url=URL.createObjectURL(blob),a=node("a");a.href=url;a.download="online-school-browser-records.json";
    document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1500);
    feedback("backup-feedback","A browser-record backup was prepared. Keep it private.");
  });
  $("import-data").addEventListener("change",async event=>{
    const file=event.target.files[0];event.target.value="";
    if(!file)return;
    if(file.size>2000000){feedback("backup-feedback","File too large (maximum 2 MB).");return;}
    try{
      const data=JSON.parse(await file.text());
      if(!data||data.version!==1||!Array.isArray(data.learners)||!Array.isArray(data.tasks)||
         !Array.isArray(data.notes)||!Array.isArray(data.attempts)||
          (data.creations!==undefined&&!Array.isArray(data.creations))||data.learners.length>100||
         data.tasks.length>10000||data.notes.length>10000||data.attempts.length>50000||
          (data.creations||[]).length>2000||
         !data.learners.every(x=>typeof x.id==="string"&&typeof x.name==="string")||
         !data.tasks.every(x=>typeof x.id==="string"&&typeof x.learnerId==="string"&&typeof x.day==="string"&&typeof x.title==="string")||
         !data.notes.every(x=>typeof x.learnerId==="string"&&typeof x.day==="string"&&typeof x.text==="string")||
         !data.attempts.every(x=>typeof x.learnerId==="string"&&typeof x.day==="string")||
          !(data.creations||[]).every(x=>x&&typeof x.id==="string"&&typeof x.learnerId==="string"&&
           typeof x.title==="string"&&typeof x.body==="string"&&typeof x.kind==="string"&&
           x.title.length<=100&&x.body.length<=5000&&
           (x.tones===undefined||(Array.isArray(x.tones)&&x.tones.length===8&&
           x.tones.every(t=>Number.isInteger(t)&&t>=0&&t<TONE_NAMES.length)))))
        throw Error("Invalid browser school backup");
      if(!confirm("Replace the browser's existing learner records with this backup?"))return;
      state={version:1,learners:data.learners,tasks:data.tasks,notes:data.notes,attempts:data.attempts,creations:data.creations||[],
        selected:typeof data.selected==="string"?data.selected:""};
      persist();practiceProblem=null;render();feedback("backup-feedback","Backup restored in this browser.");
    }catch(err){feedback("backup-feedback","Import failed: "+err.message);}
  });
  $("clear-data").addEventListener("click",()=>{
    if(!confirm("Erase all local Online School browser records on this device? Export a backup first if you need one."))return;
    state=empty();practiceProblem=null;persist();render();feedback("backup-feedback","Local browser records cleared.");
  });
  renderPassage();renderScience();renderIdea();renderStorySparks();renderPattern();render();show("play");
})();