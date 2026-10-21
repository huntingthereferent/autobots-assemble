/* A/B Studio: independent, local-only multitrack DAW prototype. Copyright 2026 James Muneoka. */
(()=>{'use strict';
const C=window.ABAudioCore;
const $=id=>document.getElementById(id);
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const copy=x=>JSON.parse(JSON.stringify(x));
const inst=['drums','bass','keys','lead','pad'];
const colors={drums:'#a4a2df',bass:'#76c7ae',keys:'#9ebad7',lead:'#e4ac84',pad:'#bba6d4',audio:'#d7ac70'};
let serial=0;const id=prefix=>prefix+'-'+(++serial)+'-'+Date.now().toString(36);
const assets=new Map();
const empty=()=>({schema:'ab-studio-v1',name:'Untitled movement',bpm:120,meter:'4/4',master:.8,tracks:[]});
let project=empty(),selected={track:null,clip:null},cursor=0,pxBeat=54,history=[],future=[],snapshots={A:null,B:null},events=[];
let audio=null,master=null,analyser=null,sources=[],playing=false,startBeat=0,startAudio=0,frame=0,recording=null;
function log(s){events.unshift(new Date().toLocaleTimeString()+' · '+s);events=events.slice(0,25);$('event-log').innerHTML=events.map(x=>'<div>'+esc(x)+'</div>').join('');}
function notice(s,bad=false){$('status').textContent=s;$('status').style.color=bad?'#ed9a9e':'#89d6d3';}
function remember(){history.push(copy(project));if(history.length>40)history.shift();future=[];}
function mutate(fn,label){remember();fn();if(label)log(label);render();}
function findTrack(){return project.tracks.find(x=>x.id===selected.track);}
function findClip(){const t=findTrack();return t&&t.clips.find(x=>x.id===selected.clip);}
function createTrack(type,name){return {id:id('t'),type,name:name||type.toUpperCase()+' '+(project.tracks.length+1),instrument:type==='audio'?'none':type,
gain:.78,pan:0,filter:18000,drive:0,delay:0,mute:false,solo:false,auto:[],clips:[]};}
function addTrack(type){mutate(()=>{const t=createTrack(type);project.tracks.push(t);selected={track:t.id,clip:null};},'Added '+type+' track');}
function midiClip(t,beat,length,notes,name){const c={id:id('c'),kind:'midi',name:name||'Pattern',beat,length,notes:notes||[]};t.clips.push(c);return c;}
function note(n,s,d=.5,v=.8){return {n,s,d,v};}
function demo(){
project=empty();const drum=createTrack('midi','Drum circuit');drum.instrument='drums';
const bass=createTrack('midi','Low orbit');bass.instrument='bass';
const keys=createTrack('midi','Chords');keys.instrument='keys';
const audioTrack=createTrack('audio','Imported / recorded audio');
project.tracks.push(drum,bass,keys,audioTrack);
const beatDrum=[];for(let i=0;i<16;i++){if(i%4===0||i%4===2)beatDrum.push(note(36,i,.18,1));if(i%4===2)beatDrum.push(note(38,i,.2,.7));beatDrum.push(note(42,i,.09,.3));}
midiClip(drum,0,16,beatDrum,'Drum loop');midiClip(bass,0,16,[0,1.5,2,3.5,4,5.5,6,7.5,8,9.5,10,11.5,12,13.5,14,15.5].map((s,i)=>note([36,36,43,43,41,41,43,41][i%8],s,.42,.65)),'Bass figure');
const chords=[];[[48,52,55],[45,48,52],[41,45,48],[43,47,50]].forEach((ch,i)=>ch.forEach(n=>chords.push(note(n,i*4,3.75,.34))));
midiClip(keys,0,16,chords,'Progression');selected={track:drum.id,clip:drum.clips[0].id};cursor=0;
}
function render(){
$('project-name').value=project.name;$('bpm').value=project.bpm;$('meter').value=project.meter;$('master-volume').value=project.master;
$('arrangement-stats').textContent=project.tracks.length+' tracks · '+project.tracks.reduce((n,t)=>n+t.clips.length,0)+' clips';
renderSources();renderTimeline();renderInspector();renderRoll();renderAB();renderClock();
$('undo').disabled=!history.length;$('redo').disabled=!future.length;
}
function renderSources(){
$('instruments').innerHTML=inst.map(n=>'<button class="source-item" data-instrument="'+n+'"><span>'+esc(n.toUpperCase())+'</span><small>+ MIDI</small></button>').join('');
$('instruments').querySelectorAll('button').forEach(b=>b.onclick=()=>{addTrack('midi');const t=findTrack();mutate(()=>{t.instrument=b.dataset.instrument;const c=midiClip(t,cursor,4,[],'New '+t.instrument);selected.clip=c.id;},'Created '+b.dataset.instrument+' pattern');});
$('assets').innerHTML=assets.size?[...assets.values()].map(x=>'<button class="source-item" data-asset="'+esc(x.id)+'"><span>'+esc(x.name.slice(0,25))+'</span><small>'+Math.round(x.bytes.length/1024)+'KB</small></button>').join(''):'<span class="muted">Import a WAV/MP3 to add sound</span>';
$('assets').querySelectorAll('button').forEach(b=>b.onclick=()=>placeAudio(b.dataset.asset));
}
function beatsPerBar(){return project.meter==='3/4'||project.meter==='6/8'?3:project.meter==='5/4'?5:4;}
function renderTimeline(){
const total=64,barBeats=beatsPerBar();
const grid=$('ruler');grid.innerHTML='';
const trackWidth=total*pxBeat;
$('arrangement-inner').style.width=(172+trackWidth)+'px';
grid.style.width=(172+trackWidth)+'px';
for(let beat=0;beat<total;beat+=barBeats){const l=document.createElement('div');l.className='bar-label';l.style.width=(Math.min(barBeats,total-beat)*pxBeat)+'px';l.textContent='BAR '+(Math.floor(beat/barBeats)+1);grid.append(l);}
grid.onclick=e=>{const r=grid.getBoundingClientRect();cursor=clamp(Math.round((e.clientX-r.left-172)/pxBeat*4)/4,0,64);renderClock();};
const laneHost=$('lanes');laneHost.innerHTML='';
for(const t of project.tracks){
const row=document.createElement('div');row.className='lane';row.innerHTML='<div class="lane-head '+(selected.track===t.id?'selected':'')+'"><div class="lane-title">'+esc(t.name)+'</div><div class="lane-type">'+esc(t.type==='audio'?'audio':'MIDI · '+t.instrument)+'</div><div class="lane-actions"><button data-action="mute" class="'+(t.mute?'active':'')+'">M</button><button data-action="solo" class="'+(t.solo?'active':'')+'">S</button><button data-action="add">+ Clip</button></div></div><div class="lane-body" style="--bar-w:'+(barBeats*pxBeat)+'px;width:'+trackWidth+'px"></div>';
const head=row.querySelector('.lane-head');head.onclick=e=>{if(e.target.closest('button'))return;selected={track:t.id,clip:null};render();};
head.querySelector('[data-action=mute]').onclick=()=>mutate(()=>{t.mute=!t.mute;},'Mute '+t.name+' '+t.mute);
head.querySelector('[data-action=solo]').onclick=()=>mutate(()=>{t.solo=!t.solo;},'Solo '+t.name+' '+t.solo);
head.querySelector('[data-action=add]').onclick=()=>addClip(t);
const body=row.querySelector('.lane-body');
body.ondblclick=e=>{if(e.target.closest('.clip'))return;cursor=snapped((e.clientX-body.getBoundingClientRect().left)/pxBeat);addClip(t);};
for(const c of t.clips){
const div=document.createElement('div');div.className='clip '+(selected.clip===c.id?'selected':'');div.style.left=(c.beat*pxBeat)+'px';div.style.width=(c.length*pxBeat-3)+'px';div.style.background=t.type==='audio'?'#77502b':colors[t.instrument]||colors.keys;div.style.color='#0a1720';
div.innerHTML='<strong>'+esc(c.name)+'</strong><div class="clip-detail">'+(c.kind==='midi'?c.notes.length+' notes':'audio source')+' · '+c.length.toFixed(2)+' beats</div>';
if(c.kind==='midi'){const mini=document.createElement('div');mini.className='clip-notes';c.notes.slice(0,128).forEach(n=>{const bar=document.createElement('i');bar.style.left=(n.s/c.length*100)+'%';bar.style.width=(Math.max(1,n.d/c.length*100))+'%';bar.style.bottom=((n.n-32)*.18)+'px';mini.append(bar);});div.append(mini);}
div.onclick=e=>{e.stopPropagation();selected={track:t.id,clip:c.id};renderInspector();renderRoll();renderTimeline();};
div.ondblclick=e=>{e.stopPropagation();selected={track:t.id,clip:c.id};renderInspector();renderRoll();};
div.oncontextmenu=e=>{e.preventDefault();selected={track:t.id,clip:c.id};render();$('clip-menu-title').textContent=c.name;$('clip-menu').showModal();};
div.onpointerdown=e=>{if(e.button!==0)return;e.stopPropagation();const initial=c.beat,at=e.clientX;let moved=false;div.setPointerCapture(e.pointerId);div.onpointermove=ev=>{const delta=snapped((ev.clientX-at)/pxBeat);const movedBeat=clamp(initial+delta,0,64-c.length);if(Math.abs(movedBeat-initial)>.001){moved=true;div.style.left=(movedBeat*pxBeat)+'px';}};
div.onpointerup=ev=>{div.onpointermove=null;div.onpointerup=null;const val=clamp(initial+snapped((ev.clientX-at)/pxBeat),0,64-c.length);if(moved&&val!==initial)mutate(()=>{c.beat=val;selected={track:t.id,clip:c.id};},'Moved '+c.name+' from '+initial+' to '+val);};};
body.append(div);
}
laneHost.append(row);
}
$('playhead').style.left=(172+cursor*pxBeat)+'px';
}
function snapped(x){const step=Number($('snap').value);return step?Math.round(x/step)*step:Math.round(x*100)/100;}
function addClip(t){if(t.type==='audio'){notice('Import or select an audio asset before placing an audio clip',true);$('audio-file').click();return;}mutate(()=>{const c=midiClip(t,clamp(cursor,0,60),4,[],'MIDI '+(t.clips.length+1));selected={track:t.id,clip:c.id};},'Added MIDI clip');}
function placeAudio(assetId){
const asset=assets.get(assetId);if(!asset||!asset.buffer){notice('Audio decoding not ready',true);return;}
let t=findTrack();if(!t||t.type!=='audio')t=project.tracks.find(x=>x.type==='audio');
if(!t){t=createTrack('audio','Imported audio');project.tracks.push(t);}
const length=clamp(asset.buffer.duration*project.bpm/60,.25,64);
mutate(()=>{const c={id:id('c'),kind:'audio',name:asset.name,assetId,beat:clamp(cursor,0,Math.max(0,64-length)),length,offset:0};t.clips.push(c);selected={track:t.id,clip:c.id};},'Placed audio '+asset.name);
notice('Audio source placed · changes to BPM use playback-rate resampling (pitch changes).');
}
function renderInspector(){
const t=findTrack(),c=findClip();$('selection-label').textContent=c?'CLIP + TRACK':t?'TRACK':'NONE';
if(!t){$('inspector-body').innerHTML='<p class="minor">Choose a track to inspect its signal flow.</p>';return;}
$('inspector-body').innerHTML='<label>NAME <input id="track-name" value="'+esc(t.name)+'" maxlength="80"></label>'+
'<div class="control-row"><label>TYPE <input value="'+esc(t.type)+'" disabled></label><label>INSTRUMENT <select id="instrument">'+(t.type==='audio'?'<option>none</option>':inst.map(n=>'<option '+(t.instrument===n?'selected':'')+'>'+n+'</option>').join(''))+'</select></label></div>'+
'<div class="control-row"><label>GAIN <input id="track-gain" type="range" min="0" max="1.5" step=".01" value="'+t.gain+'"></label><label>PAN <input id="track-pan" type="range" min="-1" max="1" step=".05" value="'+t.pan+'"></label></div>'+
'<div class="control-row"><label>LOWPASS Hz <input id="track-filter" type="range" min="160" max="20000" step="10" value="'+t.filter+'"></label><label>DRIVE <input id="track-drive" type="range" min="0" max=".95" step=".05" value="'+t.drive+'"></label><label>DELAY <input id="track-delay" type="range" min="0" max=".55" step=".05" value="'+t.delay+'"></label></div>'+
'<div class="control-row"><button id="auto-add">+ Volume point at cursor</button><button id="delete-track">Delete track</button></div>'+
'<div class="minor">VOLUME AUTOMATION · '+t.auto.map(x=>x.beat.toFixed(2)+'→'+x.value.toFixed(2)).join(' · ')+'</div>'+
(c?'<div class="group-title">CLIP · '+esc(c.kind)+'</div><div class="control-row"><label>START BEAT <input id="clip-start" type="number" min="0" max="63" step=".25" value="'+c.beat+'"></label><label>LEN BEATS <input id="clip-length" type="number" min=".25" max="64" step=".25" value="'+c.length+'"></label></div><label>CLIP NAME <input id="clip-name" maxlength="80" value="'+esc(c.name)+'"></label>':'');
$('track-name').onchange=e=>mutate(()=>{t.name=e.target.value.slice(0,80);},'Renamed track');
$('instrument').onchange=e=>mutate(()=>{t.instrument=e.target.value;},'Changed instrument');
for(const [el,key] of [['track-gain','gain'],['track-pan','pan'],['track-filter','filter'],['track-drive','drive'],['track-delay','delay']])$(el).onchange=e=>mutate(()=>{t[key]=Number(e.target.value);},'Changed '+key);
$('auto-add').onclick=()=>mutate(()=>{t.auto=t.auto.filter(x=>Math.abs(x.beat-cursor)>.001);t.auto.push({beat:cursor,value:t.gain});t.auto.sort((a,b)=>a.beat-b.beat);},'Added automation point');
$('delete-track').onclick=()=>mutate(()=>{project.tracks=project.tracks.filter(x=>x.id!==t.id);selected={track:null,clip:null};},'Removed track');
if(c){$('clip-start').onchange=e=>mutate(()=>{c.beat=clamp(Number(e.target.value)||0,0,64-c.length);},'Moved clip');$('clip-length').onchange=e=>mutate(()=>{c.length=clamp(Number(e.target.value)||.25,.25,64-c.beat);},'Resized clip');$('clip-name').onchange=e=>mutate(()=>{c.name=e.target.value.slice(0,80);},'Renamed clip');}
}
function noteName(n){return ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B'][n%12]+(Math.floor(n/12)-1);}
function renderRoll(){
const t=findTrack(),c=findClip();$('editor-label').textContent=c?(c.name+' · '+c.kind):'Select a MIDI clip';
if(!c||c.kind!=='midi'){$('piano-roll').innerHTML='<p class="minor">Choose a MIDI clip to edit notes. Click + Clip on a MIDI track to create one.</p>';return;}
const step=Number($('note-grid').value),cols=Math.min(64,Math.ceil(c.length/step));const host=$('piano-roll');host.innerHTML='';
for(let n=72;n>=48;n--){
const row=document.createElement('div');row.className='roll-row';const label=document.createElement('div');label.className='roll-name';label.textContent=noteName(n);row.append(label);
for(let i=0;i<cols;i++){const at=i*step;const isOn=c.notes.some(x=>x.n===n&&Math.abs(x.s-at)<step/3);const cell=document.createElement('button');cell.className='roll-cell '+(i%Math.max(1,Math.round(1/step))===0?'beat ':'')+(isOn?'filled':'');cell.title=noteName(n)+' at beat '+at;cell.setAttribute('aria-label',cell.title);cell.onclick=()=>mutate(()=>{const k=c.notes.findIndex(x=>x.n===n&&Math.abs(x.s-at)<step/3);if(k>=0)c.notes.splice(k,1);else c.notes.push(note(n,at,Math.min(Number($('note-length').value),c.length-at),.72));},'Edited '+noteName(n));row.append(cell);}
host.append(row);
}
}
function renderAB(){const a=snapshots.A,b=snapshots.B;const summary=p=>p?p.tracks.length+' tracks, '+p.tracks.reduce((n,t)=>n+t.clips.length,0)+' clips':'empty';
let diff='';if(a&&b){const ca=a.tracks.reduce((n,t)=>n+t.clips.length,0),cb=b.tracks.reduce((n,t)=>n+t.clips.length,0);diff='<br>Δ tracks '+(b.tracks.length-a.tracks.length)+' · Δ clips '+(cb-ca)+' · Δ BPM '+(b.bpm-a.bpm)+' · same state '+(JSON.stringify(a)===JSON.stringify(b)?'YES':'NO');}
$('ab-info').innerHTML='A: '+summary(a)+'<br>B: '+summary(b)+diff+'<br><small>Recall restores arrangement/mix controls, not removed source bytes.</small>';
}
function renderClock(){const barBeats=beatsPerBar(),bar=Math.floor(cursor/barBeats)+1,beat=Math.floor(cursor%barBeats)+1,sub=Math.round(cursor%1*100);$('clock').textContent=String(bar).padStart(3,'0')+' · '+String(beat).padStart(2,'0')+' · '+String(sub).padStart(2,'0');$('playhead').style.left=(172+cursor*pxBeat)+'px';}
function context(){if(!audio){audio=new (window.AudioContext||window.webkitAudioContext)();master=audio.createGain();analyser=audio.createAnalyser();analyser.fftSize=256;master.connect(analyser);analyser.connect(audio.destination);}master.gain.value=project.master;return audio;}
function distortionCurve(amount){const curve=new Float32Array(1024);const k=amount*100;for(let i=0;i<1024;i++){const x=i/512-1;curve[i]=(1+k)*x/(1+k*Math.abs(x));}return curve;}
function strip(ctx,t,output,fromBeat,toBeat,at){
const input=ctx.createGain(),filter=ctx.createBiquadFilter(),drive=ctx.createWaveShaper(),gain=ctx.createGain(),pan=ctx.createStereoPanner();
filter.type='lowpass';filter.frequency.value=clamp(t.filter,160,20000);drive.curve=distortionCurve(t.drive);drive.oversample='2x';
input.connect(filter);filter.connect(drive);drive.connect(gain);gain.connect(pan);pan.pan.value=t.pan;pan.connect(output);
const anySolo=project.tracks.some(x=>x.solo);
const on=!t.mute&&(!anySolo||t.solo);
const scalar=on?1:0;
let prev={beat:0,value:t.gain};let next=null;
for(const p of t.auto){if(p.beat<=fromBeat)prev=p;else{next=p;break;}}
let initial=prev.value;if(next&&next.beat>prev.beat)initial=prev.value+(next.value-prev.value)*clamp((fromBeat-prev.beat)/(next.beat-prev.beat),0,1);
gain.gain.setValueAtTime(initial*scalar,at);
for(const p of t.auto.filter(x=>x.beat>fromBeat&&x.beat<=toBeat))gain.gain.linearRampToValueAtTime(p.value*scalar,at+(p.beat-fromBeat)*60/project.bpm);
if(t.delay>0){const delay=ctx.createDelay(1),wet=ctx.createGain(),feedback=ctx.createGain();delay.delayTime.value=.22;wet.gain.value=t.delay;feedback.gain.value=.18;pan.connect(delay);delay.connect(wet);wet.connect(output);delay.connect(feedback);feedback.connect(delay);}
return input;
}
function noteSchedule(ctx,dest,n,when,duration,instrument,velocity){
const vol=clamp((velocity||.7),.03,1);
const env=ctx.createGain();env.gain.setValueAtTime(.0001,when);
const end=when+Math.max(.025,duration);
env.gain.linearRampToValueAtTime(instrument==='pad'?.12*vol:.3*vol,when+(instrument==='pad'?.11:.008));
env.gain.setTargetAtTime(.0001,Math.max(when+.015,end-.055),.024);env.connect(dest);
if(instrument==='drums'){
if(n.n===38||n.n===42||n.n===46){const length=Math.min(.30,duration+.06),frames=Math.max(256,Math.ceil(ctx.sampleRate*length)),buf=ctx.createBuffer(1,frames,ctx.sampleRate),arr=buf.getChannelData(0);for(let i=0;i<frames;i++){const x=Math.sin(i*12.9898+78.233)*43758.5453;arr[i]=(x-Math.floor(x))*2-1;}const noise=ctx.createBufferSource();noise.buffer=buf;const f=ctx.createBiquadFilter();f.type='highpass';f.frequency.value=n.n===38?680:4400;noise.connect(f);f.connect(env);noise.start(when);noise.stop(Math.min(end,when+length));sources.push(noise);return;}
const o=ctx.createOscillator();o.type='sine';o.frequency.setValueAtTime(155,when);o.frequency.exponentialRampToValueAtTime(46,when+.14);o.connect(env);o.start(when);o.stop(Math.min(end,when+.22));sources.push(o);return;
}
const o=ctx.createOscillator();o.type={bass:'sawtooth',keys:'triangle',pad:'sine',lead:'square'}[instrument]||'triangle';
o.frequency.value=440*Math.pow(2,(n.n-69)/12);o.connect(env);o.start(when);o.stop(end+.08);sources.push(o);
}
function schedule(ctx,p,fromBeat,toBeat,out,at,localAssets=assets){
const spb=60/p.bpm;
for(const t of p.tracks){const target=strip(ctx,t,out,fromBeat,toBeat,at);
for(const c of t.clips){const endBeat=c.beat+c.length;if(c.beat>=toBeat||endBeat<=fromBeat)continue;
if(c.kind==='midi'){for(const n of c.notes){const b=c.beat+n.s,e=b+n.d;if(e<=fromBeat||b>=toBeat)continue;const st=Math.max(b,fromBeat),dur=Math.min(e,toBeat)-st;noteSchedule(ctx,target,n,at+(st-fromBeat)*spb,dur*spb,t.instrument,n.v);}}
else if(c.kind==='audio'){const asset=localAssets.get(c.assetId);if(!asset||!asset.buffer)continue;
const st=Math.max(c.beat,fromBeat),dur=Math.min(endBeat,toBeat)-st;
const rate=asset.buffer.duration/Math.max(.01,c.length*spb);
const offset=(c.offset+(st-c.beat))*spb*rate;
if(offset>=asset.buffer.duration)continue;
const src=ctx.createBufferSource();src.buffer=asset.buffer;src.playbackRate.value=rate;src.connect(target);src.start(at+(st-fromBeat)*spb,offset,Math.max(.001,dur*spb*rate));sources.push(src);
}}}
}
function stop(){if(recording&&recording.state==='recording')recording.stop();playing=false;cancelAnimationFrame(frame);for(const s of sources.splice(0)){try{s.stop()}catch{}}$('play').textContent='▶ Play';$('audio-state').textContent='Audio stopped';}
async function play(){if(playing){stop();return;}try{const ctx=context();await ctx.resume();const from=cursor;const upper=$('loop').checked?Number($('loop-end').value):64;
if(from>=upper){cursor=0;}startBeat=cursor;startAudio=ctx.currentTime+.04;sources=[];playing=true;schedule(ctx,project,startBeat,upper,master,startAudio);$('play').textContent='❚❚ Pause';$('audio-state').textContent='Live Web Audio';
const tick=()=>{if(!playing)return;cursor=startBeat+(ctx.currentTime-startAudio)*project.bpm/60;if(cursor>=upper){if($('loop').checked){stop();cursor=Number($('loop-start').value);play();return;}stop();cursor=clamp(upper,0,64);renderClock();return;}renderClock();drawMeter();frame=requestAnimationFrame(tick);};tick();}catch(e){stop();notice('Playback failed: '+e.message,true);}}
function drawMeter(){const el=$('master-meter'),g=el.getContext('2d'),w=el.width=el.clientWidth*devicePixelRatio,h=el.height=26*devicePixelRatio;g.fillStyle='#091720';g.fillRect(0,0,w,h);if(!analyser)return;const a=new Uint8Array(analyser.frequencyBinCount);analyser.getByteTimeDomainData(a);let sum=0;for(const x of a)sum+=Math.pow((x-128)/128,2);const rms=clamp(Math.sqrt(sum/a.length)*2,0,1);g.fillStyle=rms>.83?'#ed9a9e':'#89d6d3';g.fillRect(0,0,rms*w,h);g.strokeStyle='#d5e1eaaa';g.strokeRect(0,0,w,h);}
function download(name,blob){const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name.replace(/[^\w.-]+/g,'_');document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1500);}
function wavEncode(buf){const channels=Math.min(2,buf.numberOfChannels),n=buf.length;if(n>44100*90)throw Error('WAV export limited to 90 seconds');const bytes=44+n*channels*2;const ab=new ArrayBuffer(bytes),v=new DataView(ab);
const tag=(off,str)=>{for(let i=0;i<str.length;i++)v.setUint8(off+i,str.charCodeAt(i));};tag(0,'RIFF');v.setUint32(4,bytes-8,true);tag(8,'WAVE');tag(12,'fmt ');v.setUint32(16,16,true);v.setUint16(20,1,true);v.setUint16(22,channels,true);v.setUint32(24,buf.sampleRate,true);v.setUint32(28,buf.sampleRate*channels*2,true);v.setUint16(32,channels*2,true);v.setUint16(34,16,true);tag(36,'data');v.setUint32(40,bytes-44,true);
const arrays=Array.from({length:channels},(_,k)=>buf.getChannelData(k));let off=44;for(let i=0;i<n;i++)for(let k=0;k<channels;k++){const x=clamp(arrays[k][i],-1,1);v.setInt16(off,x<0?x*32768:x*32767,true);off+=2;}return ab;
}
async function exportWav(stem=false){
try{stop();const span=clamp(Math.max(16,...project.tracks.flatMap(t=>t.clips.map(c=>c.beat+c.length))),1,64);const sec=span*60/project.bpm;if(sec>90)throw Error('Export exceeds 90s; shorten clips or raise BPM');
const tracks=stem?project.tracks.slice():[null];if(stem)notice('Exporting '+tracks.length+' separate tracks · allow multiple downloads');
for(const t of tracks){const p=copy(project);if(t){p.tracks=p.tracks.filter(x=>x.id===t.id);p.tracks[0].mute=false;p.tracks[0].solo=false;}const off=new OfflineAudioContext(2,Math.ceil(sec*44100),44100),out=off.createGain();out.gain.value=p.master;out.connect(off.destination);sources=[];schedule(off,p,0,span,out,0);const rendered=await off.startRendering();download(project.name+(t?'_'+t.name:'_mix')+'.wav',new Blob([wavEncode(rendered)],{type:'audio/wav'}));}
sources=[];notice(stem?'Stem WAVs rendered locally (downloads may require browser permission)':'Mixed WAV rendered and exported');log(stem?'Exported stems':'Exported mix');
}catch(e){notice('WAV export: '+e.message,true);}}
function midiBytes(){
const ppq=480, events=[];const push=(tick,bytes)=>events.push({tick,bytes});
for(const t of project.tracks)for(const c of t.clips)if(c.kind==='midi')for(const n of c.notes){const on=Math.max(0,Math.round((c.beat+n.s)*ppq)),off=Math.max(on+1,Math.round((c.beat+n.s+n.d)*ppq));push(on,[0x90,n.n,Math.round(clamp(n.v,0,1)*127)]);push(off,[0x80,n.n,0]);}
events.sort((a,b)=>a.tick-b.tick||a.bytes[0]-b.bytes[0]);const data=[0,0xff,0x51,3,...[(Math.round(60000000/project.bpm)>>16)&255,(Math.round(60000000/project.bpm)>>8)&255,Math.round(60000000/project.bpm)&255]];
function vlq(v){let x=v&127;const out=[];while((v>>=7)>0){x<<=8;x|=(v&127)|128;}while(true){out.push(x&255);if(x&128)x>>=8;else break;}return out;}
let prev=0;for(const e of events){data.push(...vlq(e.tick-prev),...e.bytes);prev=e.tick;}data.push(0,0xff,0x2f,0);
const be=(n,k)=>Array.from({length:k},(_,i)=>(n>>>((k-i-1)*8))&255);
return new Uint8Array([...Array.from('MThd').map(c=>c.charCodeAt(0)),...be(6,4),0,0,0,1,1,224,...Array.from('MTrk').map(c=>c.charCodeAt(0)),...be(data.length,4),...data]);
}
function exportMidi(){try{const bytes=midiBytes();download(project.name+'.mid',new Blob([bytes],{type:'audio/midi'}));notice('MIDI exported · note lanes are merged into one Standard MIDI track');}catch(e){notice(e.message,true);}}
async function registerAudio(file){if(file.size>25e6||file.size<1)throw Error('Audio must be 1 byte–25 MB');if(assets.size>=16)throw Error('Limit 16 local assets');
const bytes=new Uint8Array(await file.arrayBuffer()),buf=await context().decodeAudioData(bytes.buffer.slice(0));if(buf.duration>180)throw Error('Audio exceeds 3-minute import boundary');
let hash='unavailable';if(crypto.subtle){const digest=await crypto.subtle.digest('SHA-256',bytes);hash=[...new Uint8Array(digest)].map(x=>x.toString(16).padStart(2,'0')).join('');}
const asset={id:id('a'),name:file.name.slice(0,120),type:file.type||'audio/wav',hash,bytes,buffer:buf};assets.set(asset.id,asset);log('Audio bytes '+file.name+' · SHA-256 '+hash.slice(0,16));return asset;}
async function importAudio(files){for(const f of Array.from(files||[])){try{const asset=await registerAudio(f);placeAudio(asset.id);}catch(e){notice('Import '+f.name+': '+e.message,true);}}$('audio-file').value='';render();}
async function importMidi(file){if(!file)return;try{const raw=new Uint8Array(await file.arrayBuffer()),parsed=C.parseMidi(raw);if(!parsed.notes.length)throw Error('No supported MIDI notes');
if(parsed.durationMs>180000)throw Error('MIDI longer than three minutes');
mutate(()=>{const t=createTrack('midi',file.name.slice(0,60));const notes=parsed.notes.slice(0,2048).map(n=>({n:n.midi,s:n.startMs/1000*project.bpm/60,d:(n.endMs-n.startMs)/1000*project.bpm/60,v:n.velocity/127}));const length=clamp(Math.ceil(parsed.durationMs/1000*project.bpm/60),1,64);midiClip(t,0,length,notes.filter(x=>x.s<64),'Imported MIDI');project.tracks.push(t);selected={track:t.id,clip:t.clips[0].id};},'Imported MIDI '+file.name);notice('Imported '+parsed.notes.length+' MIDI notes (first 2,048 retained; real-time timing mapped at project BPM)');}catch(e){notice('MIDI import: '+e.message,true);}finally{$('midi-file').value='';}}
function base64(bytes){let out='';for(let i=0;i<bytes.length;i+=8192)out+=String.fromCharCode(...bytes.subarray(i,i+8192));return btoa(out);}
function unbase64(s){const raw=atob(s),out=new Uint8Array(raw.length);for(let i=0;i<raw.length;i++)out[i]=raw.charCodeAt(i);return out;}
function save(){try{const payload={format:'ab-studio-v1',project,assets:[...assets.values()].map(a=>({id:a.id,name:a.name,type:a.type,hash:a.hash,data:base64(a.bytes)}))};const data=JSON.stringify(payload);if(data.length>52e6)throw Error('Project too large for single-file save (50 MB cap)');download(project.name+'.abstudio.json',new Blob([data],{type:'application/json'}));notice('Project and imported source bytes exported · local JSON');log('Saved project');}catch(e){notice('Save failed: '+e.message,true);}}
function validateProject(p){if(!p||p.schema!=='ab-studio-v1'||!Array.isArray(p.tracks)||p.tracks.length>48||!C.finite(p.bpm,40,240)||!C.finite(p.master,0,1.5))throw Error('Unsupported project schema/limits');
for(const t of p.tracks){if(!t.id||!Array.isArray(t.clips)||t.clips.length>128||!Array.isArray(t.auto)||t.auto.length>512||!['audio','midi'].includes(t.type))throw Error('Unsupported track');
for(const c of t.clips){if(!['audio','midi'].includes(c.kind)||!C.finite(c.beat,0,64)||!C.finite(c.length,.01,64)||c.beat+c.length>64.00001)throw Error('Invalid clip bounds');if(c.kind==='midi'&&(!Array.isArray(c.notes)||c.notes.length>4096||c.notes.some(n=>!Number.isInteger(n.n)||n.n<0||n.n>127||!C.finite(n.s,0,64)||!C.finite(n.d,.001,64)||!C.finite(n.v,0,1))))throw Error('Invalid MIDI note');}
}}
async function openProject(file){if(!file)return;try{if(file.size>55e6)throw Error('Project exceeds 55 MB');const parsed=JSON.parse(await file.text());if(parsed.format!=='ab-studio-v1'||!Array.isArray(parsed.assets)||parsed.assets.length>16)throw Error('Not an A/B Studio project');validateProject(parsed.project);const incoming=new Map();
for(const item of parsed.assets){if(typeof item.data!=='string'||item.data.length>34e6)throw Error('Asset out of bounds');const bytes=unbase64(item.data),buf=await context().decodeAudioData(bytes.buffer.slice(0));incoming.set(item.id,{id:item.id,name:item.name,type:item.type,hash:item.hash,bytes,buffer:buf});}
stop();assets.clear();for(const [key,v] of incoming)assets.set(key,v);project=parsed.project;history=[];future=[];selected={track:project.tracks[0]?.id||null,clip:null};cursor=0;log('Opened project '+project.name);render();notice('Project opened with '+assets.size+' local audio source(s)');}catch(e){notice('Open failed: '+e.message,true);}finally{$('project-file').value='';}}
async function recordMic(){if(recording&&recording.state==='recording'){recording.stop();return;}
if(!navigator.mediaDevices?.getUserMedia||!window.MediaRecorder){notice('Microphone recording unavailable in this browser/context',true);return;}
try{const stream=await navigator.mediaDevices.getUserMedia({audio:true});const chunks=[];recording=new MediaRecorder(stream);const at=cursor;recording.ondataavailable=e=>{if(e.data.size)chunks.push(e.data);};recording.onstop=async()=>{stream.getTracks().forEach(t=>t.stop());$('record').textContent='● Mic record';try{const blob=new Blob(chunks,{type:recording.mimeType||'audio/webm'});const f=new File([blob],'recording-'+Date.now()+'.webm',{type:blob.type});const asset=await registerAudio(f);cursor=at;placeAudio(asset.id);notice('Recorded microphone audio placed on the timeline');}catch(e){notice('Recording decode failed: '+e.message,true);}};recording.start();$('record').textContent='■ Finish take';notice('Microphone active · click Finish take to insert it');}catch(e){notice('Microphone permission/recording: '+e.message,true);}}
function removeClip(){const t=findTrack(),c=findClip();if(!t||!c)return;mutate(()=>{t.clips=t.clips.filter(x=>x!==c);selected.clip=null;},'Deleted '+c.name);}
function duplicateClip(){const t=findTrack(),c=findClip();if(!t||!c)return;if(c.beat+c.length*2>64){notice('Not enough room to duplicate here',true);return;}mutate(()=>{const x=copy(c);x.id=id('c');x.beat+=x.length;x.name+=' copy';t.clips.push(x);selected.clip=x.id;},'Duplicated clip');}
function splitClip(){const t=findTrack(),c=findClip();if(!t||!c||cursor<=c.beat+.01||cursor>=c.beat+c.length-.01){notice('Place cursor within selected clip before splitting',true);return;}mutate(()=>{const left=cursor-c.beat,right=c.length-left;const other=copy(c);other.id=id('c');other.beat=cursor;other.length=right;c.length=left;if(c.kind==='midi'){other.notes=c.notes.filter(n=>n.s+n.d>left).map(n=>({...n,s:Math.max(0,n.s-left),d:Math.min(n.s+n.d-left,right)-Math.max(0,n.s-left)}));c.notes=c.notes.filter(n=>n.s<left).map(n=>({...n,d:Math.min(n.d,left-n.s)}));}else other.offset=(c.offset||0)+left;t.clips.push(other);selected.clip=other.id;},'Split clip');}
function buildKeys(){const keys=$('keys'),white=[60,62,64,65,67,69,71,72],black=[61,63,66,68,70];keys.innerHTML='';white.forEach(n=>{const b=document.createElement('button');b.className='key';b.textContent=noteName(n);b.onclick=()=>audition(n);keys.append(b);});const positions=[12.5,25,50,62.5,75];black.forEach((n,i)=>{const b=document.createElement('button');b.className='key sharp';b.style.left=positions[i]+'%';b.textContent=noteName(n);b.onclick=()=>audition(n);keys.append(b);});}
async function audition(n){try{const ctx=context();await ctx.resume();const t=findTrack();noteSchedule(ctx,master,{n},ctx.currentTime+.005,.4,t?.instrument||'keys',.8);}catch(e){notice('Keyboard: '+e.message,true);}}
function wire(){
$('play').onclick=play;$('stop').onclick=()=>{stop();cursor=0;renderClock();};$('record').onclick=recordMic;
$('add-midi').onclick=()=>addTrack('midi');$('add-audio').onclick=()=>addTrack('audio');
$('import-audio').onclick=()=>$('audio-file').click();$('audio-file').onchange=e=>importAudio(e.target.files);
$('import-midi').onclick=()=>$('midi-file').click();$('midi-file').onchange=e=>importMidi(e.target.files[0]);
$('new-project').onclick=()=>{stop();assets.clear();history=[];future=[];snapshots={A:null,B:null};project=empty();selected={track:null,clip:null};cursor=0;log('New blank project');render();};
$('save-project').onclick=save;$('open-project').onclick=()=>$('project-file').click();$('project-file').onchange=e=>openProject(e.target.files[0]);
$('export-wav').onclick=()=>exportWav(false);$('export-stems').onclick=()=>exportWav(true);$('export-midi').onclick=exportMidi;
$('bpm').onchange=e=>mutate(()=>{project.bpm=clamp(Number(e.target.value)||120,40,240);},'Tempo '+e.target.value);
$('meter').onchange=e=>mutate(()=>{project.meter=e.target.value;},'Meter '+e.target.value);
$('project-name').onchange=e=>mutate(()=>{project.name=e.target.value.slice(0,100)||'Untitled movement';},'Project renamed');
$('master-volume').onchange=e=>mutate(()=>{project.master=Number(e.target.value);if(master)master.gain.value=project.master;},'Master volume');
$('zoom').oninput=e=>{pxBeat=Number(e.target.value);renderTimeline();};
$('snap').onchange=()=>notice('Snap '+$('snap').selectedOptions[0].textContent);
$('note-grid').onchange=renderRoll;
$('quantize').onclick=()=>{const c=findClip();if(!c||c.kind!=='midi')return;const step=Number($('note-grid').value);mutate(()=>{c.notes.forEach(n=>n.s=Math.round(n.s/step)*step);},'Quantized notes');};
$('duplicate').onclick=duplicateClip;$('split').onclick=splitClip;$('delete-clip').onclick=removeClip;
$('context-duplicate').onclick=()=>{$('clip-menu').close();duplicateClip();};$('context-delete').onclick=()=>{$('clip-menu').close();removeClip();};$('context-close').onclick=()=>$('clip-menu').close();
for(const key of ['A','B']){$('store-'+key.toLowerCase()).onclick=()=>{snapshots[key]=copy(project);log('Stored state '+key);renderAB();};$('recall-'+key.toLowerCase()).onclick=()=>{if(!snapshots[key]){notice('State '+key+' is empty',true);return;}stop();mutate(()=>{project=copy(snapshots[key]);selected={track:project.tracks[0]?.id||null,clip:null};},'Recalled state '+key);};}
$('undo').onclick=()=>{if(!history.length)return;stop();future.push(copy(project));project=history.pop();selected={track:project.tracks[0]?.id||null,clip:null};render();};
$('redo').onclick=()=>{if(!future.length)return;stop();history.push(copy(project));project=future.pop();selected={track:project.tracks[0]?.id||null,clip:null};render();};
document.addEventListener('keydown',e=>{if(e.target.closest('input,select,textarea,dialog'))return;
if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='z'){e.preventDefault();if(e.shiftKey)$('redo').click();else $('undo').click();return;}
if(e.code==='Space'){e.preventDefault();$('play').click();return;}
const mapping='awsedftgyhujk',idx=mapping.indexOf(e.key.toLowerCase()),notes=[60,61,62,63,64,65,66,67,68,69,70,71,72];if(idx>=0&&!e.repeat)audition(notes[idx]);
});
window.addEventListener('beforeunload',e=>{if(history.length){e.preventDefault();e.returnValue='';}});
}
if(!C){document.body.textContent='A/B Studio requires its local audio-intake-core.js dependency.';return;}
demo();buildKeys();wire();render();log('Loaded demo arrangement · native worker not invoked');notice('Demo arrangement ready · Play uses browser Web Audio');
})();