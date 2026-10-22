"use strict";
(function(root,factory){const api=factory();if(typeof module==="object"&&module.exports)module.exports=api;root.SchoolFamily=api;})(typeof window==="object"?window:globalThis,function(){
 const DAY=86400000;
 function monday(date){
  if(!/^\d{4}-\d{2}-\d{2}$/.test(date||""))throw Error("Expected ISO day");
  const ms=Date.parse(date+"T12:00:00Z");
  if(!Number.isFinite(ms)||new Date(ms).toISOString().slice(0,10)!==date)throw Error("Invalid date");
  const d=new Date(ms),offset=(d.getUTCDay()+6)%7;
  return new Date(ms-offset*DAY).toISOString().slice(0,10);
 }
 function week(date){const start=monday(date),base=Date.parse(start+"T12:00:00Z");return Array.from({length:7},(_,i)=>new Date(base+i*DAY).toISOString().slice(0,10));}
 function forLearner(task,learnerId){
  if(!learnerId||learnerId==="all")return true;
  const ids=Array.isArray(task.learner_ids)?task.learner_ids:[];
  return ids.includes(learnerId)||(task.scope==="shared"&&!ids.length);
 }
 function metrics(tasks,learnerId){
  const unique=new Map();
  for(const task of tasks||[]){
   if(!task||typeof task.id!=="string"||!forLearner(task,learnerId))continue;
   unique.set(task.id,task);
  }
  const rows=[...unique.values()],done=rows.filter(x=>x.status==="done");
  const minutes=rows.reduce((sum,t)=>sum+(Number.isFinite(Number(t.planned_minutes))?Math.max(0,Number(t.planned_minutes)):0),0);
  return{total:rows.length,done:done.length,remaining:rows.length-done.length,
   plannedMinutes:minutes,rows};
 }
 return{monday,week,forLearner,metrics};
});