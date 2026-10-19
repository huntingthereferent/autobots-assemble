'use strict';
/* Recompute the two finite receivers from independent Trial04B observations.
 * No target blueprint geometry is inserted. This original WORLD source stays
 * separate from the physics integrator that consumes it.
 */
window.worldJunctionSource=(()=>{
const rad=.25,I=.03125,P=[3,1.35],V=[3,.12],S=[12,1.5];
const dot=(a,b)=>a[0]*b[0]+a[1]*b[1],add=(a,b)=>[a[0]+b[0],a[1]+b[1]];
const sub=(a,b)=>[a[0]-b[0],a[1]-b[1]],mul=(s,a)=>[s*a[0],s*a[1]];
const cross=(a,b)=>a[0]*b[1]-a[1]*b[0],rd=(n,k=9)=>+n.toFixed(k);
function face(deg){
 const n=[-Math.cos(deg*Math.PI/180),-Math.sin(deg*Math.PI/180)],t=[-n[1],n[0]];
 const first=(rad-dot(sub(P,S),n))/dot(V,n),p=add(P,mul(first,V));
 const jn=-2*dot(V,n),slip=dot(V,t);
 const jt=Math.max(-.4*jn,Math.min(.4*jn,-slip/(1+rad*rad/I)));
 const outgoing=add(V,add(mul(jn,n),mul(jt,t)));
 const normal=mul(-1/Math.hypot(...outgoing),outgoing);
 const original=add(add(p,mul(.25,outgoing)),mul(-rad,normal));
 const anchor=original.map(z=>rd(z,10)),nn=normal.map(z=>rd(z,10));
 const tangent=[-nn[1],nn[0]];
 const ends=[add(anchor,mul(-.5,tangent)).map(z=>rd(z)),
             add(anchor,mul(.5,tangent)).map(z=>rd(z))];
 return {id:'source-derived-'+deg+'-friction-0.4',
  source_original_angle:deg,source_friction:.4,anchor,normal:nn,endpoints:ends,
  origin_04B_branch_first_contact:rd(first,10),
  origin_04B_branch_receiver_contact:rd(first+.25,10),
  source_receipt_id:'contact-derived-face-1'};
}
function generate(){
 const surfaces=[face(0),face(20)],a=surfaces[0],b=surfaces[1];
 const ta=sub(a.endpoints[1],a.endpoints[0]),tb=sub(b.endpoints[1],b.endpoints[0]);
 const det=cross(ta,tb);
 if(Math.abs(det)<1e-5)throw Error('measured finite faces parallel');
 const delta=sub(b.anchor,a.anchor),u=cross(delta,tb)/det,v=cross(delta,ta)/det;
 if(Math.abs(u)>.5||Math.abs(v)>.5)throw Error('source faces do not intersect');
 const junction=add(a.anchor,mul(u,ta)).map(z=>rd(z));
 return {schema:'world-ab-connected-receiver-routing/v1',
 assembly_policy:'combine independent observed 04B receivers without moving or relabeling',
 source_experiment_is_separate_cross_run_branches:true,surfaces,junction,
 junction_local_coordinates:[rd(u),rd(v)],finite_intersection_verified:true,
 topology:{segments:2,intersections:1,connected_components:1,curved_segments:0},
 original_geometry_24x6_preserved:true,simultaneous_disc_multicontact_resolved:false};
}
return {generate};
})();