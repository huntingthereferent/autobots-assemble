const $ = q => document.querySelector(q);

const dayInput = $("#day");
const learnerTabs = $("#learner-tabs");
const relationsEl = $("#relations");
const noRelations = $("#no-relations");
const obligationsEl = $("#obligations");
const todayList = $("#today-list");
const sharedList = $("#shared-list");
const todayEmpty = $("#today-empty");
const artifactsEl = $("#artifacts");
const artifactsEmpty = $("#artifacts-empty");
const observationForm = $("#observation-form");
const observationError = $("#observation-error");
const taskDialog = $("#task-dialog");
const taskForm = $("#task-form");
const taskError = $("#task-error");

let school = null;
let state = null;
let selectedLearnerId = null;

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

function learner() {
  return school?.learners?.find(x => x.id === selectedLearnerId) || school?.learners?.[0] || null;
}

function renderLearnerTabs() {
  learnerTabs.replaceChildren(...school.learners.map(person => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "learner-tab" + (person.id === selectedLearnerId ? " active" : "");
    button.innerHTML = `<strong></strong><span></span>`;
    button.querySelector("strong").textContent = person.display_name;
    button.querySelector("span").textContent = person.current_relations.length
      ? `${person.current_relations.length} current relation(s)`
      : "ground from observation";
    button.addEventListener("click", () => {
      selectedLearnerId = person.id;
      render();
    });
    return button;
  }));
}

function relationCard(relation) {
  const el = document.createElement("article");
  el.className = "relation";
  const supported = relation.supported?.length
    ? relation.supported.map(x => `<li></li>`).join("")
    : "";
  const unsupported = relation.unsupported?.length
    ? relation.unsupported.map(x => `<li></li>`).join("")
    : "";
  el.innerHTML = `
    <div class="relation-top">
      <strong class="relation-referent"></strong>
      <span class="relation-evidence"></span>
    </div>
    <div class="relation-grid">
      <div class="relation-supported" ${supported ? "" : "hidden"}><span>Supported now</span><ul>${supported}</ul></div>
      <div class="relation-unsupported" ${unsupported ? "" : "hidden"}><span>Not supported now</span><ul>${unsupported}</ul></div>
    </div>
  `;
  el.querySelector(".relation-referent").textContent = relation.referent;
  el.querySelector(".relation-evidence").textContent = `${relation.evidence_refs?.length || 0} evidence ref(s)`;
  [...el.querySelectorAll(".relation-supported li")].forEach((node, i) => node.textContent = relation.supported[i]);
  [...el.querySelectorAll(".relation-unsupported li")].forEach((node, i) => node.textContent = relation.unsupported[i]);
  return el;
}

function activityRow(task) {
  const row = document.createElement("article");
  row.className = "activity";
  row.dataset.status = task.status || "todo";

  const check = document.createElement("input");
  check.type = "checkbox";
  check.className = "check";
  check.checked = task.status === "done";
  check.setAttribute("aria-label", `Mark ${task.title} complete`);
  check.addEventListener("change", async () => {
    await patchTask(task.id, {status: check.checked ? "done" : "todo"});
  });

  const body = document.createElement("div");
  const title = document.createElement("strong");
  title.textContent = task.title;
  const meta = document.createElement("div");
  meta.className = "meta";
  const relation = task.meta?.curriculum_standard ? ` · ${task.meta.curriculum_standard}` : "";
  meta.textContent = `${task.scope || "activity"}${relation}`;
  body.append(title, meta);
  if (task.notes) {
    const note = document.createElement("div");
    note.className = "activity-note";
    note.textContent = task.notes;
    body.append(note);
  }

  const time = document.createElement("span");
  time.className = "time";
  time.textContent = task.planned_minutes ? hours(task.planned_minutes) : "—";
  row.append(check, body, time);
  return row;
}

function renderRelations(person) {
  relationsEl.replaceChildren(...person.current_relations.map(relationCard));
  noRelations.hidden = person.current_relations.length !== 0;
  $("#observation-count").textContent = `${person.observation_count} observation(s)`;
}

function renderToday(person) {
  const own = person.today_tasks || [];
  todayList.replaceChildren(...own.map(activityRow));
  todayEmpty.hidden = own.length !== 0;
  sharedList.replaceChildren(...(school.shared_today || []).map(activityRow));
  const planned = own.reduce((sum, x) => sum + (Number(x.planned_minutes) || 0), 0);
  $("#today-summary").textContent = `${own.length} movement(s) · ${hours(planned)} planned`;
}

function renderObligations(person) {
  obligationsEl.replaceChildren(...person.curriculum_obligations.map(target => {
    const el = document.createElement("article");
    el.className = "obligation";
    el.innerHTML = `<div><span class="code"></span><strong></strong></div><p></p>`;
    el.querySelector(".code").textContent = target.code;
    el.querySelector("strong").textContent = target.title;
    el.querySelector("p").textContent = target.description;
    return el;
  }));
}

function renderArtifacts(person) {
  artifactsEl.replaceChildren(...person.artifacts.map(ws => {
    const el = document.createElement("a");
    el.className = "artifact";
    el.href = "./worksheet.html";
    el.innerHTML = `<strong></strong><span></span>`;
    el.querySelector("strong").textContent = ws.title || "Worksheet";
    const standard = ws.provenance?.standard || ws.knowledge_goal || ws.template || "artifact";
    el.querySelector("span").textContent = standard;
    return el;
  }));
  artifactsEmpty.hidden = person.artifacts.length !== 0;
}

function renderSchedule() {
  const tasks = (state?.tasks || []).filter(x => x.date === dayInput.value);
  $("#all-tasks").replaceChildren(...tasks.map(activityRow));
  $("#task-total").textContent = `${tasks.length} scheduled movement(s)`;

  $("#rhythm-list").replaceChildren(...(state?.schedule?.daily_rhythm || []).map(item => {
    const el = document.createElement("div");
    el.className = "rhythm-chip";
    const when = item.start ? `${item.start}${item.end ? "–" + item.end : ""}` : "";
    el.innerHTML = when ? `<strong></strong><span></span>` : `<span></span>`;
    if (when) el.querySelector("strong").textContent = when;
    el.querySelector("span").textContent = item.label;
    return el;
  }));
}

function render() {
  const person = learner();
  if (!person) return;

  renderLearnerTabs();
  $("#learner-heading").textContent = person.display_name;
  $("#grade-context").textContent = person.grade_context ? `Grade ${person.grade_context} obligation context` : "No grade obligation context";
  renderRelations(person);
  renderToday(person);
  renderObligations(person);
  renderArtifacts(person);
  renderSchedule();

  const learnerQuery = encodeURIComponent(person.display_name || person.id);
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
    fetch(`/api/school?date=${encodeURIComponent(day)}`, {cache: "no-store"}),
    fetch("/api/state", {cache: "no-store"})
  ]);
  if (!schoolResponse.ok || !stateResponse.ok) throw new Error("Could not load school workspace");
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
    method: "PATCH",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(patch)
  });
  if (!response.ok) return;
  await load();
}

observationForm.addEventListener("submit", async event => {
  event.preventDefault();
  observationError.hidden = true;
  const person = learner();
  const data = new FormData(observationForm);
  try {
    const response = await fetch("/api/observations", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        learner_id: person.id,
        referent: data.get("referent"),
        observed: data.get("observed"),
        supports: lines(data.get("supports")),
        contradicts: lines(data.get("contradicts")),
        provenance: [`online-school:observation:${dayInput.value}`]
      })
    });
    const body = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(body.error || "Could not record observation");
    observationForm.reset();
    await load();
  } catch (err) {
    observationError.textContent = err.message;
    observationError.hidden = false;
  }
});

dayInput.addEventListener("change", load);

$("#add-task").addEventListener("click", () => {
  taskError.hidden = true;
  taskForm.reset();
  taskDialog.showModal();
});
$("#close-dialog").addEventListener("click", () => taskDialog.close());
$("#cancel-task").addEventListener("click", () => taskDialog.close());

taskForm.addEventListener("submit", async event => {
  event.preventDefault();
  taskError.hidden = true;
  const data = new FormData(taskForm);
  const learnerId = data.get("learner");
  try {
    const response = await fetch("/api/tasks", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        date: dayInput.value,
        title: data.get("title"),
        planned_minutes: Number(data.get("planned_minutes") || 0),
        learner_ids: learnerId ? [learnerId] : [],
        scope: learnerId ? "individual" : "shared",
        notes: data.get("notes") || "",
        source: "manual"
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
  $("#learner-heading").textContent = "School workspace unavailable";
  noRelations.hidden = false;
  noRelations.textContent = err.message;
});
