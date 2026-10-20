/* A/B-owned Canvas2D renderer. No Godot, third-party engine, physics, or worker. */
/* Model coordinates, rendering coordinates, and navigation history stay separate. */
(() => {
  "use strict";
  const $ = id => document.getElementById(id);
  const canvas = $("ab-canvas");
  const context = canvas.getContext("2d", {alpha:false});
  const labels = {state:$("current-state"),selected:$("selected-state"),history:$("history"),status:$("status"),source:$("source")};
  const colors = {bg:"#0b1120",grid:"#203044",a:"#44d9d5",b:"#ad90fa",gold:"#f3c56b",text:"#e4eaf3",muted:"#8495ae"};
  let model=null, byId=new Map(), current="", selected="", history=[], positions=new Map();
  let view={scale:1,offsetX:0,offsetY:0}, hover="", drag=null, animation=null;
  let demo={running:false,index:0,nextAt:0}, pending=false, lastSize="";
  let draws=0, error="", loaded=false;

  function refuse(message) {
    error=String(message); loaded=false; demo.running=false;
    labels.status.textContent="SOURCE REFUSED · "+error;
    labels.status.dataset.status="error";
    console.error("A/B native renderer refused source:",error);
    requestPaint();
    return false;
  }
  const stateKey=s=>s.join(",");
  function validState(s) {
    return Array.isArray(s)&&s.length===3&&s.every(v=>Number.isInteger(v)&&v>=0&&v<3);
  }
  function successor(s,a) {
    const [x,y,z]=s;
    if(a==="A")return[(x+1)%3,y,z];
    if(a==="B")return[x,(y+x+1)%3,(z+[0,1,2][y])%3];
    throw new Error("Only source actions A/B are admitted");
  }
  function validate(payload) {
    if(!payload||typeof payload!=="object"||Array.isArray(payload))throw Error("not a scene");
    if(payload.schema!=="ab-renderer/native-finite-scene/v1" ||
      payload.model!=="declared-finite-F3-cubed-phi012" ||
      payload.source!=="work/arc_like_maze/math.py::World" ||
      !/^[a-f0-9]{64}$/.test(payload.source_sha256||"") ||
      JSON.stringify(payload.phi)!=="[0,1,2]" ||
      payload.origin!=="0,0,0" ||
      payload.node_count!==27 || payload.edge_count!==54 ||
      !Array.isArray(payload.nodes)||payload.nodes.length!==27 ||
      typeof payload.presentation_boundary!=="string" ||
      !payload.presentation_boundary.includes("editorial"))throw Error("model/source contract mismatch");
    const rows=new Map();
    for(const row of payload.nodes) {
      if(!row || !validState(row.state) || row.id!==stateKey(row.state) ||
        !Number.isInteger(row.steps_from_origin) || row.steps_from_origin<0 ||
        !row.transitions || Object.keys(row.transitions).sort().join("")!=="AB" ||
        rows.has(row.id))throw Error("duplicate or invalid scene state");
      for(const action of "AB") {
        if(row.transitions[action]!==stateKey(successor(row.state,action)))
          throw Error("invented or changed A/B transition: "+row.id+":"+action);
      }
      rows.set(row.id,row);
    }
    if(!rows.has(payload.origin))throw Error("missing finite origin");
    const discovered=new Map([[payload.origin,0]]), queue=[payload.origin];
    for(let i=0;i<queue.length;i++) {
      for(const action of "AB") {
        const to=rows.get(queue[i]).transitions[action];
        if(!rows.has(to))throw Error("transition has no native destination");
        if(!discovered.has(to)){discovered.set(to,discovered.get(queue[i])+1);queue.push(to);}
      }
    }
    if(discovered.size!==27)throw Error("native graph disconnected");
    if(queue.some((id,i)=>id!==payload.nodes[i].id))throw Error("native breadth-first order differs");
    for(const [id,depth] of discovered)
      if(rows.get(id).steps_from_origin!==depth)throw Error("native BFS distance differs");
    if(typeof payload.example_actions!=="string" ||
      payload.example_actions.length>64 || !/^[AB]*$/.test(payload.example_actions) ||
      !Array.isArray(payload.example_states) ||
      payload.example_states.length!==payload.example_actions.length+1 ||
      payload.example_states[0]!==payload.origin)throw Error("invalid example path");
    let state=payload.origin;
    for(let i=0;i<payload.example_actions.length;i++) {
      state=rows.get(state).transitions[payload.example_actions[i]];
      if(payload.example_states[i+1]!==state)throw Error("unreplayable example transition");
    }
    return rows;
  }

  // This is VIEW layout, not mathematical state, a source measurement, or physics.
  function deriveLayout() {
    positions=new Map();
    const buckets=new Map();
    for(const row of model.nodes){
      if(!buckets.has(row.steps_from_origin))buckets.set(row.steps_from_origin,[]);
      buckets.get(row.steps_from_origin).push(row.id);
    }
    for(const [depth,ids] of buckets)
      ids.forEach((id,i)=>positions.set(id,{x:depth*178,y:(i-(ids.length-1)/2)*94}));
  }
  function dims() {
    const dpr=Math.min(window.devicePixelRatio||1,2);
    const rect=canvas.getBoundingClientRect();
    const w=Math.max(1,Math.round(rect.width)),h=Math.max(1,Math.round(rect.height));
    if(canvas.width!==Math.round(w*dpr)||canvas.height!==Math.round(h*dpr)){
      canvas.width=Math.round(w*dpr);canvas.height=Math.round(h*dpr);
    }
    context.setTransform(dpr,0,0,dpr,0,0);
    return {w,h};
  }
  function fitView() {
    if(!loaded)return;
    const {w,h}=dims();
    const all=[...positions.values()];
    const minX=Math.min(...all.map(p=>p.x))-48,maxX=Math.max(...all.map(p=>p.x))+48;
    const minY=Math.min(...all.map(p=>p.y))-48,maxY=Math.max(...all.map(p=>p.y))+48;
    view.scale=Math.max(.20,Math.min(1.8,Math.min((w-80)/(maxX-minX),(h-80)/(maxY-minY))));
    view.offsetX=w/2-(minX+maxX)/2*view.scale;
    view.offsetY=h/2-(minY+maxY)/2*view.scale;
    requestPaint();
  }
  const at=id=>{const p=positions.get(id);return{x:p.x*view.scale+view.offsetX,y:p.y*view.scale+view.offsetY}};
  function line(a,b,color,width=1,alpha=1){
    context.strokeStyle=color;context.lineWidth=width;context.globalAlpha=alpha;
    context.beginPath();context.moveTo(a.x,a.y);context.lineTo(b.x,b.y);context.stroke();context.globalAlpha=1;
  }
  function drawEdge(a,b,color,width=1,alpha=.18){
    const from=at(a),to=at(b),dx=to.x-from.x,dy=to.y-from.y,dist=Math.hypot(dx,dy);
    if(dist<2){context.globalAlpha=alpha;context.strokeStyle=color;context.lineWidth=width;
      context.beginPath();context.arc(from.x+10,from.y-11,10,0,Math.PI*2);context.stroke();context.globalAlpha=1;return;}
    const ux=dx/dist,uy=dy/dist,start={x:from.x+ux*16,y:from.y+uy*16};
    const end={x:to.x-ux*17,y:to.y-uy*17};
    line(start,end,color,width,alpha);
    const side=5;const back=9;
    line(end,{x:end.x-ux*back-uy*side,y:end.y-uy*back+ux*side},color,width,alpha);
    line(end,{x:end.x-ux*back+uy*side,y:end.y-uy*back-ux*side},color,width,alpha);
  }
  function paint(now) {
    pending=false;draws++;
    const {w,h}=dims();
    context.fillStyle=colors.bg;context.fillRect(0,0,w,h);
    context.strokeStyle=colors.grid;context.lineWidth=1;
    for(let x=(view.offsetX%46+46)%46;x<w;x+=46)line({x,y:0},{x,y:h},colors.grid,1,.25);
    for(let y=(view.offsetY%46+46)%46;y<h;y+=46)line({x:0,y},{x:w,y},colors.grid,1,.25);
    if(!loaded){
      context.fillStyle=colors.muted;context.font="15px monospace";
      context.fillText(error?"SOURCE REFUSED: "+error:"Opening native finite source…",24,42);
      return;
    }
    // Edges are completely generated from the source graph, not decorative joins.
    for(const row of model.nodes)
      for(const a of "AB")drawEdge(row.id,row.transitions[a],a==="A"?colors.a:colors.b,1,.15);
    const row=byId.get(current);
    for(const a of "AB")drawEdge(current,row.transitions[a],a==="A"?colors.a:colors.b,2.8,.94);
    for(const hst of history)drawEdge(hst.from,hst.to,colors.gold,2.4,.58);

    for(const row of model.nodes){
      const p=at(row.id),selectedRow=row.id===selected,currentRow=row.id===current;
      context.beginPath();context.arc(p.x,p.y,Math.max(8,11*view.scale),0,Math.PI*2);
      context.fillStyle=currentRow?"#175c62":selectedRow?"#334764":"#1a2b42";
      context.fill();context.strokeStyle=currentRow?colors.a:selectedRow?colors.gold:"#415a77";
      context.lineWidth=currentRow?2.5:1.2;context.stroke();
      if(view.scale>.37){
        context.font=Math.max(9,11*view.scale)+"px ui-monospace,monospace";
        context.fillStyle=colors.text;context.textAlign="center";
        context.fillText(row.id.replaceAll(",",""),p.x,p.y-14*view.scale);
        context.textAlign="start";
      }
    }
    let cursor=at(current);
    if(animation){
      const t=Math.min(1,(now-animation.at)/290);
      const start=at(animation.from),end=at(animation.to);
      // Motion between *screen positions* is not a new F3 state.
      cursor={x:start.x+(end.x-start.x)*t,y:start.y+(end.y-start.y)*t};
      if(t>=1)animation=null;
    }
    context.fillStyle=colors.gold;context.beginPath();context.arc(cursor.x,cursor.y,5.5,0,Math.PI*2);context.fill();
    if(animation||demo.running)requestPaint();
  }
  function updateLabels(){
    if(!loaded)return;
    labels.state.textContent="("+current+")";
    labels.selected.textContent="("+selected+")";
    labels.history.textContent=history.map(h=>h.action).join("")||"∅ (origin)";
    labels.source.textContent=model.source+" · SHA-256 "+model.source_sha256.slice(0,16)+"…";
    labels.status.textContent="SOURCE-VERIFIED FINITE PROJECTION · "+model.node_count+" states / "+model.edge_count+" directed edges";
    labels.status.dataset.status="ready";
    $("undo").disabled=history.length===0;
  }
  function advance(a,fromDemo=false){
    if(!loaded||a!=="A"&&a!=="B")return;
    if(!fromDemo)demo.running=false;
    const dest=byId.get(current).transitions[a];
    if(!byId.has(dest))return refuse("missing source edge destination");
    const prev=current;
    history.push({from:prev,action:a,to:dest});current=dest;selected=dest;
    animation={from:prev,to:dest,at:performance.now()};
    updateLabels();requestPaint();
  }
  function reset(){
    if(!loaded)return;
    demo.running=false;demo.index=0;history=[];current=model.origin;selected=current;animation=null;
    updateLabels();requestPaint();
  }
  function undo(){
    if(!loaded||!history.length)return;
    demo.running=false;const last=history.pop();
    current=last.from;selected=current;animation=null;updateLabels();requestPaint();
  }
  function play(){
    if(!loaded)return;
    reset();demo={running:true,index:0,nextAt:performance.now()};
    requestPaint();
  }
  function tick(now){
    // Kept separate from source-data steps: this only schedules recorded keys.
    if(!loaded||!demo.running)return;
    if(now>=demo.nextAt){
      if(demo.index>=model.example_actions.length)demo.running=false;
      else{
        advance(model.example_actions[demo.index],true);demo.index++;
        demo.nextAt=now+430;
      }
    }
  }
  // One browser frame loop, only while the scene is changing.
  function framed(now){tick(now);paint(now);}
  function requestPaint() {if(!pending){pending=true;requestAnimationFrame(framed);}}
  function pointerLocation(event){const r=canvas.getBoundingClientRect();return{x:event.clientX-r.left,y:event.clientY-r.top};}
  function pick(p){let best="",distance=21;for(const [id,pos] of positions){const t=at(id),d=Math.hypot(t.x-p.x,t.y-p.y);if(d<distance){best=id;distance=d;}}return best;}
  canvas.addEventListener("pointerdown",e=>{drag={...pointerLocation(e),offX:view.offsetX,offY:view.offsetY,moved:false};canvas.setPointerCapture(e.pointerId);});
  canvas.addEventListener("pointermove",e=>{
    if(!loaded)return;
    const p=pointerLocation(e);
    if(drag){const dx=p.x-drag.x,dy=p.y-drag.y;if(Math.hypot(dx,dy)>5)drag.moved=true;view.offsetX=drag.offX+dx;view.offsetY=drag.offY+dy;requestPaint();}
    else {const found=pick(p);if(hover!==found){hover=found;canvas.style.cursor=found?"pointer":"grab";}}
  });
  canvas.addEventListener("pointerup",e=>{if(!loaded||!drag)return;const p=pointerLocation(e);const moved=drag.moved;drag=null;
    if(!moved){const id=pick(p);if(id){selected=id;updateLabels();requestPaint();}}
  });
  canvas.addEventListener("wheel",e=>{
    if(!loaded)return;e.preventDefault();
    const pos=pointerLocation(e),scale=Math.max(.20,Math.min(2.8,view.scale*Math.exp(-e.deltaY*.0011)));
    const wx=(pos.x-view.offsetX)/view.scale,wy=(pos.y-view.offsetY)/view.scale;
    view.scale=scale;view.offsetX=pos.x-wx*scale;view.offsetY=pos.y-wy*scale;requestPaint();
  },{passive:false});
  $("step-a").addEventListener("click",()=>advance("A"));
  $("step-b").addEventListener("click",()=>advance("B"));
  $("reset").addEventListener("click",reset);
  $("undo").addEventListener("click",undo);
  $("play").addEventListener("click",play);
  $("fit").addEventListener("click",fitView);
  document.addEventListener("keydown",e=>{
    if(e.altKey||e.ctrlKey||e.metaKey||/^(INPUT|TEXTAREA)$/.test(document.activeElement?.tagName||""))return;
    if(e.key.toUpperCase()==="A"){advance("A");e.preventDefault();}
    if(e.key.toUpperCase()==="B"){advance("B");e.preventDefault();}
    if(e.key==="Backspace"){undo();e.preventDefault();}
    if(e.key.toUpperCase()==="R"){reset();e.preventDefault();}
    if(e.key.toUpperCase()==="P"){play();e.preventDefault();}
  });
  if(typeof ResizeObserver!=="undefined")new ResizeObserver(()=>requestPaint()).observe(canvas);
  window.addEventListener("resize",requestPaint);

  // Inspection is read-only; this interface is not an execution control API.
  window.__ABNativeView=Object.freeze({
    get loaded(){return loaded;},get error(){return error;},
    get current(){return current;},get selected(){return selected;},
    get actions(){return history.map(h=>h.action).join("");},
    get edgeCount(){return model?.edge_count||0;},get drawCount(){return draws;},
    get demoRunning(){return demo.running;},
    get sceneSchema(){return model?.schema||"";}
  });
  fetch("./ab-renderer-scene.json",{cache:"no-store"}).then(r=>{
    if(!r.ok)throw Error("scene source HTTP "+r.status);
    return r.json();
  }).then(data=>{
    byId=validate(data);model=data;current=data.origin;selected=current;
    deriveLayout();loaded=true;error="";updateLabels();fitView();
  }).catch(e=>refuse(e.message));
})();
