'use strict';
/* WORLD Trial 06. Disc/swept finite-capsule dynamics, active event times,
 * endpoint caps, fail-closed simultaneous-contact and world-edge rules.
 * Uses the separately reconstructed owner-source geometry, not desired shapes.
 */
window.worldABContinuous=(()=>{
const R=.25,I=.03125,EPS=1e-9,CL=2e-7,STEP=.05,T=1.5,MAX=12;
const levels=[.9,1.05,1.2,1.6,1.8,2,2.25,1.3,1.322386,1.4],rd=x=>+x.toFixed(9);
const dot=(a,b)=>a[0]*b[0]+a[1]*b[1],add=(a,b)=>[a[0]+b[0],a[1]+b[1]];
const sub=(a,b)=>[a[0]-b[0],a[1]-b[1]],mul=(s,a)=>[s*a[0],s*a[1]];
const cp=x=>JSON.parse(JSON.stringify(x));
let state=null,cursor=0;
function nearest(p,s){
 const a=s.endpoints[0],b=s.endpoints[1],ab=sub(b,a);
 const t=Math.max(0,Math.min(1,dot(sub(p,a),ab)/dot(ab,ab)));
 return {distance:Math.hypot(...sub(p,add(a,mul(t,ab))))};
}
function events(p,v,segments,budget){
 const found=[],speed=dot(v,v);if(speed<=1e-10)return found;
 for(const s of segments){
  const [a,b]=s.endpoints,t0=sub(b,a),len=Math.hypot(...t0),tang=mul(1/len,t0),norm=[-tang[1],tang[0]];
  const signed=dot(sub(p,a),norm),rate=dot(v,norm);
  if(Math.abs(rate)>EPS)for(const side of [-1,1]){
   const n=mul(side,norm);if(dot(v,n)>=-EPS)continue;
   let dt=(side*R-signed)/rate;
   if(dt< -EPS||dt>budget+EPS)continue;dt=Math.max(0,dt);
   const center=add(p,mul(dt,v)),along=dot(sub(center,a),tang);
   if(along>EPS&&along<len-EPS)found.push({dt,id:s.id,feature:'interior',n,center});
  }
  for(let j=0;j<2;j++){
   const point=[a,b][j],d=sub(p,point),bval=dot(d,v),c=dot(d,d)-R*R;
   const discriminant=bval*bval-speed*c;if(discriminant<0)continue;
   let dt=(-bval-Math.sqrt(Math.max(0,discriminant)))/speed;
   if(dt< -EPS||dt>budget+EPS)continue;dt=Math.max(dt,0);
   const center=add(p,mul(dt,v)),delta=sub(center,point),distance=Math.hypot(...delta);
   if(distance<=1e-12)continue;
   const n=mul(1/distance,delta);
   if(dot(v,n)<-EPS)found.push({dt,id:s.id,feature:'endpoint-'+j,n,center});
  }
 }
 found.sort((a,b)=>a.dt-b.dt||a.id.localeCompare(b.id)||a.feature.localeCompare(b.feature));
 return found;
}
function edge(p,v,available){
 const cand=[];
 for(let axis=0;axis<2;axis++){
  let bound;if(v[axis]<-EPS)bound=R;
  else if(v[axis]>EPS)bound=axis===0?24-R:6-R;
  else continue;
  const t=(bound-p[axis])/v[axis];
  if(t>=-EPS&&t<=available+EPS)cand.push(Math.max(0,t));
 }
 return cand.length?Math.min(...cand):null;
}
function impulse(v,spin,n){
 const length=Math.hypot(...n);if(Math.abs(length-1)>1e-7)throw Error('bad surface normal');
 n=mul(1/length,n);
 const t=[-n[1],n[0]],approach=dot(v,n);if(approach>=-EPS)throw Error('not approaching');
 const jn=-2*approach,slip=dot(v,t)-spin*R;
 const jt=Math.max(-.4*jn,Math.min(.4*jn,-slip/(1+R*R/I)));
 const newV=add(v,add(mul(jn,n),mul(jt,t))),newW=spin-R*jt/I;
 const energy=(v,w)=>.5*dot(v,v)+.5*I*w*w;
 const before=energy(v,spin),after=energy(newV,newW);
 if(after>before+1e-8)throw Error('physical contact created energy');
 return {v:newV,w:newW,receipt:{normal_impulse:rd(jn),tangential_impulse:rd(jt),energy_before:rd(before),energy_after:rd(after)}};
}
function trace(y,segments){
 let p=[12,y],v=[-2,0],spin=0,theta=0,clock=0,status='completed',missing=null,min=Infinity;
 const contacts=[],frames=[{time:0,position:[12,rd(y)],velocity:[-2,0],spin:0,orientation:0}];
 for(let tick=1;tick<=Math.round(T/STEP);tick++){
  let available=tick*STEP-clock;
  while(available>EPS){
   const cand=events(p,v,segments,available),out=edge(p,v,available);
   if(out!==null&&(!cand.length||out<cand[0].dt-EPS)){
    theta+=spin*out;p=add(p,mul(out,v));clock+=out;available-=out;
    status='world-edge-reached-no-boundary-response';missing={time:rd(clock),center:p.map(rd)};break;
   }
   if(!cand.length){
    theta+=spin*available;p=add(p,mul(available,v));
    clock+=available;available=0;break;
   }
   const hit=cand[0],time=hit.dt;
   const touching=segments.filter(s=>nearest(hit.center,s).distance<=R+CL).map(s=>s.id);
   const ambiguity=new Set(touching).size>1||cand.slice(1).some(e=>Math.abs(e.dt-time)<1e-7&&e.id!==hit.id);
   theta+=spin*time;p=hit.center;clock+=time;available-=time;
   if(ambiguity){
    status='unresolved-multiple-contacts';
    missing={time:rd(clock),surfaces:[...new Set(touching)].sort(),center:p.map(rd)};break;
   }
   const oldV=v,oldW=spin,change=impulse(v,spin,hit.n);v=change.v;spin=change.w;
   contacts.push({time:rd(clock),surface_id:hit.id,feature:hit.feature,
    center:p.map(rd),normal:hit.n.map(rd),incoming_velocity:oldV.map(rd),
    outgoing_velocity:v.map(rd),incoming_spin:rd(oldW),outgoing_spin:rd(spin),...change.receipt});
   if(contacts.length>=MAX){
    status='unresolved-event-budget';missing={time:rd(clock)};break;
   }
  }
  for(const s of segments){
   const d=nearest(p,s).distance;min=Math.min(d,min);
   if(d<R-CL){
    status='penetration';missing={time:rd(clock),surface_id:s.id,distance:rd(d)};break;
   }
  }
  if(!(R-1e-7<=p[0]&&p[0]<=24-R+1e-7&&R-1e-7<=p[1]&&p[1]<=6-R+1e-7)){
   status='outside-world';missing={time:rd(clock)};
  }
  frames.push({time:rd(clock),position:p.map(rd),velocity:v.map(rd),spin:rd(spin),orientation:rd(theta)});
  if(status!=='completed')break;
 }
 return {entry_y:rd(y),status,frames,contacts,
  first_contact:contacts.length?contacts[0].surface_id:null,
  exit:frames.at(-1),minimum_frame_clearance:rd(min),unresolved:missing};
}
function generate(){
 const geometry=window.worldJunctionSource.generate();
 const a=levels.map(y=>trace(y,geometry.surfaces.slice(0,1)));
 const b=levels.map(y=>trace(y,geometry.surfaces));
 return {schema:'world-ab-connected-continuous-junction/v1',
  geometry,probe_levels:cp(levels),baseline_finite_capsule:a,connected_finite_capsule:b,
  completed_cases:b.filter(q=>q.status==='completed').length,
  unresolved_cases:b.filter(q=>q.status!=='completed').map(q=>({entry_y:q.entry_y,status:q.status})),
  finite_segment_endpoints_enabled:true,restitution:1,friction:.4,
  virtual_disc_radius:R,physical_world_dimensions:[24,6],
  multi_contact_manifold_solver:false,source_04B_branches_simultaneously_generated:false,
  full_original_blueprint_generated:false};
}
const canvas=document.getElementById('view'),ctx=canvas.getContext('2d');
const X=x=>20+x*39,Y=y=>15+y*42;
function drawLine(p,c){if(!p.length)return;
 ctx.strokeStyle=c;ctx.lineWidth=3;ctx.beginPath();ctx.moveTo(X(p[0][0]),Y(p[0][1]));
 for(const q of p.slice(1))ctx.lineTo(X(q[0]),Y(q[1]));ctx.stroke();}
function paint(){
 ctx.fillStyle='#102436';ctx.fillRect(0,0,960,310);
 ctx.strokeStyle='#2a5265';ctx.lineWidth=1;
 for(let x=0;x<24;x+=2){ctx.beginPath();ctx.moveTo(X(x),0);ctx.lineTo(X(x),310);ctx.stroke();}
 if(!state)return;
 state.geometry.surfaces.forEach((s,i)=>drawLine(s.endpoints,i?'#72d6b0':'#f0b681'));
 const idx=+document.getElementById('probe').value;
 const a=state.baseline_finite_capsule[idx],b=state.connected_finite_capsule[idx];
 for(const [caseData,c] of [[a,'#e8a77f'],[b,'#87d8fa']]){
  drawLine(caseData.frames.slice(0,cursor+1).map(q=>q.position),c);
 }
 const obs=b.frames[Math.min(cursor,b.frames.length-1)];
 ctx.fillStyle='#f3efdc';ctx.beginPath();ctx.arc(X(obs.position[0]),Y(obs.position[1]),R*39,0,Math.PI*2);ctx.fill();
 document.getElementById('status').textContent=
  'LOOK '+cursor+' | probe y='+b.entry_y+' | single: '+a.status+' | connected: '+b.status+
  ' | impacts '+b.contacts.length+' | x='+obs.position[0]+' y='+obs.position[1];
 document.getElementById('receipt').textContent=JSON.stringify({geometry:state.geometry,
  baseline:a,connected:b,observed:obs,multi_contact_claimed:false},null,2);
}
document.getElementById('run').onclick=()=>{
 try{state=generate();cursor=0;paint();}catch(e){state=null;document.getElementById('status').textContent='Rejected: '+e.message;}
};
document.getElementById('probe').onchange=()=>{cursor=0;paint();};
document.getElementById('next').onclick=()=>{if(state){cursor=Math.min(30,cursor+1);paint();}};
document.getElementById('prev').onclick=()=>{if(state){cursor=Math.max(0,cursor-1);paint();}};
document.getElementById('reset').onclick=()=>{state=null;cursor=0;paint();};
document.getElementById('export').onclick=()=>{
 if(!state)return;
 const u=URL.createObjectURL(new Blob([JSON.stringify(state,null,2)+'\n'],{type:'application/json'}));
 const a=document.createElement('a');a.href=u;a.download='world_ab_junction_observations.json';
 document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(u),1000);
};
return {generate,receipt:()=>state?cp(state):null,cursor:()=>cursor};
})();
