const $ = q => document.querySelector(q);

const dayInput = $("#day");
const learnerTabs = $("#learner-tabs");
const observationDialog = $("#observation-dialog");
const observationForm = $("#observation-form");
const observationError = $("#observation-error");
const taskDialog = $("#task-dialog");
const taskForm = $("#task-form");
const taskError = $("#task-error");

let school = null;
let state = null;
let selectedLearnerId = null;
let showAllObligations = false;

function todayISO() {
  const now = new Date();
  const local = new Date(now.getTime() - now.getTimezoneOffset() * 60000);
  return local.toISOString().slice(0, 10);
}

function lines(value) {
  return String(value || "").split("\n").map(x => x.trim()).filter(Boolean);
}

function hours(minutes) {
  const total = Number(minutes) || 0;
  const h = Math.floor(total / 60);
  const m = total % 60;
  return h && m ? `${h}h ${m}m` : h ? `${h}h` : `${m}m`;
}

function person() {
  return school?.learners?.find(x => x.id === selectedLearnerId) || school?.learners?.[0] || null;
}

function subjectFor(text) {
  const value = String(text || "").toLowerCase();
  if (/math|add|subtract|multip|divid|fraction|number|money|time|geometry/.test(value)) return "math";
  if (/read|phon|word|spell|vocab|decod/.test(value)) return "reading";
  if (/writ|handwriting/.test(value)) return "writing";
  if (/science|plant|weather|water|experiment/.test(value)) return "science";
  if (/history|social|missouri|trade|market/.test(value)) return "history";
  if (/art|creative|draw|paint/.test(value)) return "art";
  if (/physical|exercise|movement|pe /.test(value)) return "movement";
  return "learning";
}

function subjectLabel(text) {
  const map = {
    math:"Math", reading:"Reading", writing:"Writing", science:"Science",
    history:"History", art:"Art", movement:"Movement", learning:"Learning"
  };
  return map[subjectFor(text)];
}

function renderLearners() {
  learnerTabs.replaceChildren(...school.learners.map(item => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "learner-pill" + (item.id === selectedLearnerId ? " active" : "");
    button.innerHTML = `<span class="avatar"></span><span class="learner-copy"><strong></strong><small></small></span>`;
    button.querySelector(".avatar").textContent = (item.display_name || "?").slice(0,1).toUpperCase();
    button.querySelector("strong").textContent = item.display_name;
    const count = item.today_tasks.filter(x => x.status !== "done").length;
    button.querySelector("small").textContent = count ? `${count} thing${count === 1 ? "" : "s"} today` : "clear for now";
    button.onclick = () => { selectedLearnerId = item.id; render(); };
    return button;
  }));
}

function renderNow(item) {
  const front = item.front || {};
  const learning = front.learning_now;
  const root = $("#learning-now");
  root.innerHTML = "";
  $("#learning-empty").hidden = Boolean(learning);

  if (learning) {
    const subject = subjectFor(learning.referent);
    const label = document.createElement("span");
    label.className = `subject-tag subject-${subject}`;
    label.textContent = subjectLabel(learning.referent);

    const title = document.createElement("h2");
    title.textContent = learning.referent;

    root.append(label, title);

    if (learning.supported?.length) {
      const lead = document.createElement("p");
      lead.className = "now-lead";
      lead.textContent = learning.supported[0];
      root.append(lead);
    }

    if (learning.unsupported?.length) {
      const next = document.createElement("div");
      next.className = "still-working";
      next.innerHTML = `<span>Still working on</span><strong></strong>`;
      next.querySelector("strong").textContent = learning.unsupported[0];
      root.append(next);
    }
  }

  const nextTask = front.do_next;
  const nextRoot = $("#do-next");
  nextRoot.innerHTML = "";
  const complete = $("#complete-next");

  if (nextTask) {
    const subject = subjectFor(nextTask.title + " " + (nextTask.notes || ""));
    const label = document.createElement("span");
    label.className = `subject-tag subject-${subject}`;
    label.textContent = subjectLabel(nextTask.title);

    const title = document.createElement("h2");
    title.textContent = nextTask.title;

    const note = document.createElement("p");
    note.className = "next-note";
    note.textContent = nextTask.notes || "This is the next thing already in front.";

    const meta = document.createElement("div");
    meta.className = "next-meta";
    meta.textContent = nextTask.planned_minutes ? `about ${hours(nextTask.planned_minutes)}` : "when ready";

    nextRoot.append(label, title, note, meta);
    complete.hidden = false;
    complete.dataset.taskId = nextTask.id;
  } else {
    nextRoot.innerHTML = `<h2>Nothing assigned right now.</h2><p class="next-note">Follow what is actually happening.</p>`;
    complete.hidden = true;
    complete.dataset.taskId = "";
  }
}

function activityRow(task) {
  const row = document.createElement("article");
  const subject = subjectFor(task.title + " " + (task.notes || ""));
  row.className = `timeline-row subject-edge-${subject}`;
  row.dataset.status = task.status || "todo";

  const check = document.createElement("button");
  check.type = "button";
  check.className = "status-check";
  check.setAttribute("aria-label", `Mark ${task.title} complete`);
  check.textContent = task.status === "done" ? "✓" : "";
  check.onclick = async () => {
    await patchTask(task.id, {status: task.status === "done" ? "todo" : "done"});
  };

  const body = document.createElement("div");
  body.className = "timeline-body";
  const title = document.createElement("strong");
  title.textContent = task.title;
  const note = document.createElement("span");
  note.textContent = task.notes || subjectLabel(task.title);
  body.append(title, note);

  const time = document.createElement("span");
  time.className = "time";
  time.textContent = task.planned_minutes ? hours(task.planned_minutes) : "—";

  row.append(check, body, time);
  return row;
}

function renderToday(item) {
  const own = item.today_tasks || [];
  $("#today-list").replaceChildren(...own.map(activityRow));
  $("#today-empty").hidden = own.length !== 0;
  $("#shared-list").replaceChildren(...(school.shared_today || []).map(activityRow));
  const minutes = own.reduce((sum, x) => sum + (Number(x.planned_minutes) || 0), 0);
  $("#today-summary").textContent = own.length ? `${own.length} · ${hours(minutes)} planned` : "open";
}

function renderRecent(item) {
  const observation = item.front?.what_changed;
  const root = $("#recent-change");
  root.innerHTML = "";
  $("#observation-count").textContent = `${item.observation_count} observation${item.observation_count === 1 ? "" : "s"}`;

  if (!observation) {
    root.innerHTML = `<div class="empty-soft">Nothing recorded yet. That is okay—start from what you notice.</div>`;
    return;
  }

  const wrap = document.createElement("article");
  wrap.className = "change-card";
  wrap.innerHTML = `
    <span class="change-referent"></span>
    <p class="change-observed"></p>
    <div class="change-result"></div>
  `;
  wrap.querySelector(".change-referent").textContent = observation.referent;
  wrap.querySelector(".change-observed").textContent = observation.observed;
  const result = wrap.querySelector(".change-result");
  const bits = [
    ...(observation.supports || []).map(x => `Now: ${x}`),
    ...(observation.contradicts || []).map(x => `Changed: ${x}`)
  ];
  result.textContent = bits.join(" · ");
  root.append(wrap);
}

function renderNeeds(item) {
  const all = item.curriculum_obligations || [];
  const visible = showAllObligations ? all : all.slice(0, 4);
  const root = $("#obligations");
  root.replaceChildren(...visible.map(target => {
    const row = document.createElement("article");
    const subject = subjectFor(target.title + " " + target.description);
    row.className = "need-row";
    row.innerHTML = `
      <span class="need-dot subject-bg-${subject}"></span>
      <div><strong></strong><span></span></div>
    `;
    row.querySelector("strong").textContent = target.title;
    row.querySelector("span").textContent = target.description;
    return row;
  }));
  const toggle = $("#toggle-obligations");
  toggle.hidden = all.length <= 4;
  toggle.textContent = showAllObligations ? "Show less" : `Show all ${all.length}`;
}

function renderArtifacts(item) {
  const root = $("#artifacts");
  root.replaceChildren(...(item.artifacts || []).slice(0, 6).map(ws => {
    const link = document.createElement("a");
    const subject = subjectFor(ws.subject + " " + ws.title);
    link.className = "artifact-tile";
    link.href = "./worksheet.html";
    link.innerHTML = `
      <span class="artifact-icon subject-bg-${subject}">↗</span>
      <strong></strong>
      <small></small>
    `;
    link.querySelector("strong").textContent = ws.title || "Worksheet";
    link.querySelector("small").textContent = ws.knowledge_goal || subjectLabel(ws.subject || ws.title);
    return link;
  }));
  $("#artifacts-empty").hidden = Boolean(item.artifacts?.length);
}

function renderLearningDetails(item) {
  const root = $("#all-relations");
  root.innerHTML = "";
  if (!item.current_relations.length) {
    root.innerHTML = `<div class="empty-soft">No current relation recorded.</div>`;
    return;
  }
  item.current_relations.forEach(relation => {
    const block = document.createElement("div");
    block.className = "detail-relation";
    block.innerHTML = `<strong></strong><p></p>`;
    block.querySelector("strong").textContent = relation.referent;
    const bits = [
      ...(relation.supported || []).map(x => `available: ${x}`),
      ...(relation.unsupported || []).map(x => `not yet: ${x}`)
    ];
    block.querySelector("p").textContent = bits.join(" · ");
    root.append(block);
  });
}

function renderSchedule() {
  const tasks = (state?.tasks || []).filter(x => x.date === dayInput.value);
  $("#all-tasks").replaceChildren(...tasks.map(activityRow));
  $("#task-total").textContent = `${tasks.length} scheduled`;
  $("#rhythm-list").replaceChildren(...(state?.schedule?.daily_rhythm || []).map(item => {
    const chip = document.createElement("div");
    chip.className = "rhythm-chip";
    const when = item.start ? `${item.start}${item.end ? "–" + item.end : ""}` : "";
    chip.innerHTML = `<strong></strong><span></span>`;
    chip.querySelector("strong").textContent = when;
    chip.querySelector("span").textContent = item.label;
    return chip;
  }));
}

function render() {
  const item = person();
  if (!item) return;

  renderLearners();
  renderNow(item);
  renderToday(item);
  renderRecent(item);
  renderNeeds(item);
  renderArtifacts(item);
  renderLearningDetails(item);
  renderSchedule();

  const learnerQuery = encodeURIComponent(item.display_name || item.id);
  $("#worksheet-studio-link").href = `./worksheet.html?learner=${learnerQuery}`;
  $("#create-worksheet-link").href = `./worksheet.html?learner=${learnerQuery}`;

  const select = taskForm.elements.learner;
  select.replaceChildren(
    new Option("Shared / everyone", ""),
    ...school.learners.map(x => new Option(x.display_name, x.id))
  );
}

async function load() {
  const day = dayInput.value;
  const [schoolResponse, stateResponse] = await Promise.all([
    fetch(`/api/school?date=${encodeURIComponent(day)}`, {cache:"no-store"}),
    fetch("/api/state", {cache:"no-store"})
  ]);
  if (!schoolResponse.ok || !stateResponse.ok) throw new Error("Could not load Online School");
  school = await schoolResponse.json();
  state = await stateResponse.json();

  if (!selectedLearnerId || !school.learners.some(x => x.id === selectedLearnerId)) {
    selectedLearnerId = school.learners[0]?.id || null;
  }

  $("#boundaries").replaceChildren(...(school.boundaries || []).map(text => {
    const p = document.createElement("p");
    p.textContent = text;
    return p;
  }));
  render();
}

async function patchTask(id, patch) {
  const response = await fetch(`/api/tasks/${encodeURIComponent(id)}`, {
    method:"PATCH",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify(patch)
  });
  if (!response.ok) throw new Error("Could not update activity");
  await load();
}

function openObservation() {
  observationError.hidden = true;
  observationForm.reset();
  observationDialog.showModal();
}

$("#show-observation").onclick = openObservation;
$("#show-observation-2").onclick = openObservation;
$("#close-observation").onclick = () => observationDialog.close();
$("#cancel-observation").onclick = () => observationDialog.close();

observationForm.addEventListener("submit", async event => {
  event.preventDefault();
  observationError.hidden = true;
  const item = person();
  const data = new FormData(observationForm);
  try {
    const response = await fetch("/api/observations", {
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify({
        learner_id:item.id,
        referent:data.get("referent"),
        observed:data.get("observed"),
        supports:lines(data.get("supports")),
        contradicts:lines(data.get("contradicts")),
        provenance:[`online-school:observation:${dayInput.value}`]
      })
    });
    const body = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(body.error || "Could not save observation");
    observationDialog.close();
    await load();
  } catch (err) {
    observationError.textContent = err.message;
    observationError.hidden = false;
  }
});

$("#complete-next").onclick = async event => {
  const id = event.currentTarget.dataset.taskId;
  if (id) await patchTask(id, {status:"done"});
};

$("#open-schedule").onclick = () => {
  document.querySelector("#today").scrollIntoView({behavior:"smooth", block:"start"});
};

$("#toggle-obligations").onclick = () => {
  showAllObligations = !showAllObligations;
  renderNeeds(person());
};

dayInput.onchange = load;

$("#add-task").onclick = () => {
  taskError.hidden = true;
  taskForm.reset();
  taskDialog.showModal();
};
$("#close-dialog").onclick = () => taskDialog.close();
$("#cancel-task").onclick = () => taskDialog.close();

taskForm.addEventListener("submit", async event => {
  event.preventDefault();
  taskError.hidden = true;
  const data = new FormData(taskForm);
  const learnerId = data.get("learner");
  try {
    const response = await fetch("/api/tasks", {
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify({
        date:dayInput.value,
        title:data.get("title"),
        planned_minutes:Number(data.get("planned_minutes") || 0),
        learner_ids:learnerId ? [learnerId] : [],
        scope:learnerId ? "individual" : "shared",
        notes:data.get("notes") || "",
        source:"manual"
      })
    });
    const body = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(body.error || "Could not add activity");
    taskDialog.close();
    await load();
  } catch (err) {
    taskError.textContent = err.message;
    taskError.hidden = false;
  }
});

dayInput.value = todayISO();
load().catch(err => {
  $("#learning-now").innerHTML = `<h2>Could not load school.</h2><p class="next-note"></p>`;
  $("#learning-now .next-note").textContent = err.message;
});