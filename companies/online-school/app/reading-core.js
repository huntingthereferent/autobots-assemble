"use strict";
(function(root,factory){const api=factory();if(typeof module==="object"&&module.exports)module.exports=api;root.SchoolReading=api;})(typeof window==="object"?window:globalThis,function(){
const PASSAGES=[
{id:"seed",label:"Starting words",title:"The Little Seed",level:"Short sentences",text:"A seed sat in the dirt. It had a little rain. The sun came out. The seed made a green sprout. Soon, a leaf reached for the light.",question:"What changed for the seed? Tell it in your own words."},
{id:"bridge",label:"Growing reader",title:"The Bridge of Stones",level:"A short story",text:"Mara wanted to cross the small stream. The water was too deep for her shoes. She found four flat stones beside the bank. She put them in a line and tested each one. The last stone moved, so Mara chose a wider one. This time the path held.",question:"What problem did Mara notice, and how did she change her plan?"},
{id:"sky",label:"Curious reader",title:"The Shape of a Shadow",level:"Observe and explain",text:"At breakfast, Leo noticed his shadow reached all the way across the porch. By lunchtime, it was short and tucked close to his feet. The porch had not moved. Leo wondered if the Sun's position could explain the change. He decided to draw his shadow at three different times the next day.",question:"What did Leo observe, and what would his next test help him find out?"}
];
function get(id){return PASSAGES.find(p=>p.id===id)||PASSAGES[0];}
function words(text){return String(text||"").match(/\S+|\s+/gu)||[];}
function speakable(text){return String(text||"").replace(/[\u0000-\u001f]+/g," ").trim().slice(0,4000);}
function cleanWord(s){return String(s||"").replace(/^[^\p{L}\p{N}]+|[^\p{L}\p{N}]+$/gu,"");}
return{PASSAGES,get,words,speakable,cleanWord};
});