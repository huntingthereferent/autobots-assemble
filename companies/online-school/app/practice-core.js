"use strict";
(function(root,factory){
  const api=factory();
  if(typeof module==="object"&&module.exports)module.exports=api;
  root.SchoolPractice=api;
})(typeof window==="object"?window:globalThis,function(){
  const WORDS=[
    {word:"cat",sounds:"c · a · t",hint:"A small pet that purrs."},
    {word:"sun",sounds:"s · u · n",hint:"It lights the sky."},
    {word:"map",sounds:"m · a · p",hint:"It shows where places are."},
    {word:"fish",sounds:"f · i · sh",hint:"It swims in water."},
    {word:"ship",sounds:"sh · i · p",hint:"It can sail over water."},
    {word:"frog",sounds:"f · r · o · g",hint:"It can hop and croak."},
    {word:"rain",sounds:"r · ai · n",hint:"It falls from clouds."},
    {word:"moon",sounds:"m · oo · n",hint:"It shines in the night sky."}
  ];
  function number(n,random){return Math.floor(random()*n);}
  function newProblem(track,level,random=Math.random){
    if(track==="words"){
      const w=WORDS[number(WORDS.length,random)];
      return {track,prompt:"Blend the sounds",detail:w.sounds,answer:w.word,hint:w.hint};
    }
    if(!["starter","builder","explorer"].includes(level))level="starter";
    const limit=level==="starter"?10:level==="builder"?30:12;
    const multiply=level==="explorer"&&random()>.35;
    let a=number(limit+1,random),b=number(limit+1,random);
    const subtraction=!multiply&&random()>.5;
    if(subtraction&&b>a)[a,b]=[b,a];
    const op=multiply?"×":subtraction?"−":"+";
    return {track:"numbers",prompt:"What is the answer?",detail:a+" "+op+" "+b+" = ?",
      answer:String(multiply?a*b:subtraction?a-b:a+b),
      hint:multiply?"Try groups of "+a+".":subtraction?"Count backward "+b+" from "+a+".":"Start at "+a+" and count forward "+b+"."};
  }
  function normalize(answer){return String(answer??"").trim().toLowerCase().replace(/\s+/g," ");}
  function correct(problem,answer){return Boolean(problem)&&normalize(answer)===normalize(problem.answer);}
  function summary(attempts,firstTry){return {attempts:Math.max(0,attempts|0),firstTry:Math.min(Math.max(0,firstTry|0),Math.max(0,attempts|0))};}
  return {newProblem,correct,normalize,summary};
});