"use strict";
(function(){
  const $=id=>document.getElementById(id);
  const kits={
    math:{template:"arithmetic",title:"Number Lab · Warm-up",subject:"Math",goal:"Solve and explain a small set of arithmetic problems.",instructions:"Show how you reached an answer. Change the questions as needed."},
    words:{template:"spelling",title:"Word Lab · Sounds and spelling",subject:"Reading / writing",goal:"Connect sounds, spelling, and the meaning of familiar words.",instructions:"Read each word, say the sounds, and write it your way."},
    reflection:{template:"custom",title:"Wonder Journal · Think and write",subject:"Science / writing",goal:"Notice something in the world and explain what happened.",instructions:"Use your own observation. There is no pre-filled correct conclusion."}
  };
  const feedback=$("kit-feedback");
  document.querySelectorAll("[data-kit]").forEach(button=>{
    button.addEventListener("click",()=>{
      const kit=kits[button.dataset.kit];
      if(!kit)return;
      $("template").value=kit.template;
      $("template").dispatchEvent(new Event("change",{bubbles:true}));
      $("ws-title").value=kit.title;
      $("subject").value=kit.subject;
      $("knowledge-goal").value=kit.goal;
      $("instructions").value=kit.instructions;
      $("columns").value=kit.template==="arithmetic"?"2":"1";
      if(kit.template==="arithmetic"){
        const prompt=$("math-prompt"),topic=$("math-topic"),count=$("count");
        if(prompt)prompt.value="Addition and subtraction within 20. Mix a few short word problems.";
        if(topic)topic.value="mixed";
        if(count)count.value="10";
      }else if(kit.template==="spelling"){
        const input=$("words");
        if(input)input.value="cat, map, rain, ship, moon";
      }else if(kit.template==="custom"){
        const input=$("custom-items");
        if(input)input.value="What did you notice? :: Teacher review.\nWhat changed as you looked closer? :: Teacher review.\nWhat would you try next? :: Teacher review.\nWhat evidence could you keep? :: Teacher review.";
      }
      document.querySelectorAll("[data-kit]").forEach(b=>b.setAttribute("aria-pressed",String(b===button)));
      feedback.textContent="Loaded "+button.querySelector("strong").textContent+" starter. Edit any part before printing.";
      $("generate-worksheet").click();
    });
  });
})();