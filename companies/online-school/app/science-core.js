"use strict";
(function(root,factory){const api=factory();if(typeof module==="object"&&module.exports)module.exports=api;root.SchoolScience=api;})(typeof window==="object"?window:globalThis,function(){
const CHALLENGES=[
{id:"shadow",title:"Where does a shadow go?",question:"Does a shadow stay the same size and direction throughout the day?",materials:"Sunlight, paper, pencil and a safe place to observe",method:"Mark the same object's shadow at two different times. Record the clock times and the shape. Never look directly at the Sun."},
{id:"water",title:"Which surface holds a drop?",question:"How does one drop of water behave on different surfaces?",materials:"A few drops of water, a spoon, a towel and two safe surfaces",method:"Ask an adult before using household surfaces. Put one small drop on each. Record how it moves or spreads. Dry everything afterward."},
{id:"paper",title:"Can paper make a bridge?",question:"How does changing the shape of paper affect what it can hold?",materials:"Paper, two books and light objects such as erasers",method:"Bridge two books with a sheet of paper. Try a flat sheet, then fold it. Observe each result using only light objects."}
];
function choose(id){return CHALLENGES.find(x=>x.id===id)||CHALLENGES[0]}
function normalized(field){return String(field??"").trim().replace(/\s+/g," ").slice(0,1800)}
function buildObservation(data){
 const question=normalized(data.question),prediction=normalized(data.prediction),method=normalized(data.method),
  observed=normalized(data.observed),next=normalized(data.next),learner=normalized(data.learner);
 if(!learner)throw Error("Choose a learner first.");
 if(!question)throw Error("Enter the question.");
 if(!method)throw Error("Describe what you tried.");
 if(!observed)throw Error("Record what you actually observed before saving.");
 return {learner_id:learner,referent:"Science Notebook / "+question,
 observed:"Method tried: "+method+". Observation: "+observed+(prediction?". Prediction: "+prediction:"")+(next?". Next step: "+next:""),
 supports:[],contradicts:[],provenance:["online-school:science-notebook:v1"]};
}
return {CHALLENGES,choose,normalized,buildObservation};
});