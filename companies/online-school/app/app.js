const dayInput = document.querySelector("#day");
const taskList = document.querySelector("#task-list");
const empty = document.querySelector("#empty");
const taskCount = document.querySelector("#task-count");
const doneCount = document.querySelector("#done-count");
const plannedTime = document.querySelector("#planned-time");
const remainingTime = document.querySelector("#remaining-time");
const rhythmList = document.querySelector("#rhythm-list");
const themeLabel = document.querySelector("#theme");
const dialog = document.querySelector("#task-dialog");
const form = document.querySelector("#task-form");
const error = document.querySelector("#form-error");

let tasks = [];
let state = null;
let filter = "all";

function todayISO() {
  const now = new Date();
  const local = new Date(now.getTime() - now.getTimezoneOffset() * 60000);
  return local.toISOString().slice(0, 10);
}

function hours(minutes) {
  if (!minutes) return "0h";
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return h && m ? `${h}h ${m}m` : h ? `${h}h` : `${m}m`;
}

function learnerLabel(ids) {
  if (!ids?.length) return "Shared";
  const names = Object.fromEntries((state?.learners || []).map(x => [x.id, x.display_name]));
  return ids.map(id => names[id] || id).join(" + ");
}

function currentTheme(day) {
  for (const week of state?.themes?.weeks || []) {
    const found = (week.days || []).find(item => item.date === day);
    if (found) return found.theme || week.label || "";
  }
  return "";
}

function renderRhythm() {
  rhythmList.innerHTML = "";
  for (const item of state?.schedule?.daily_rhythm || []) {
    const chip = document.createElement("div");
    chip.className = "rhythm-chip";
    const time = item.start ? `${item.start}${item.end ? "–" + item.end : ""}` : "";
    chip.innerHTML = time ? `<strong>${time}</strong>${item.label}` : item.label;
    rhythmList.append(chip);
  }
}

function render() {
  const day = dayInput.value;
  const visible = tasks
    .filter(task => task.date === day)
    .filter(task => filter === "all" || task.status === filter)
    .sort((a, b) => (a.scope + a.title).localeCompare(b.scope + b.title));

  taskList.innerHTML = "";
  for (const task of visible) {
    const row = document.createElement("article");
    row.className = "task";
    row.dataset.status = task.status;

    const check = document.createElement("input");
    check.type = "checkbox";
    check.className = "check";
    check.checked = task.status === "done";
    check.setAttribute("aria-label", `Mark ${task.title} complete`);
    check.addEventListener("change", () => updateTask(task.id, { status: check.checked ? "done" : "todo" }));

    const body = document.createElement("div");
    const title = document.createElement("div");
    title.className = "task-title";
    title.textContent = task.title;
    const meta = document.createElement("div");
    meta.className = "task-meta";
    meta.textContent = `${learnerLabel(task.learner_ids)} · ${task.scope || "task"}`;
    body.append(title, meta);
    if (task.notes) {
      const notes = document.createElement("div");
      notes.className = "task-notes";
      notes.textContent = task.notes;
      body.append(notes);
    }

    const time = document.createElement("div");
    time.className = "task-time";
    time.textContent = task.planned_minutes ? hours(task.planned_minutes) : "—";

    row.append(check, body, time);
    taskList.append(row);
  }

  empty.hidden = visible.length !== 0;

  const todayTasks = tasks.filter(task => task.date === day);
  const done = todayTasks.filter(task => task.status === "done");
  const totalMinutes = todayTasks.reduce((sum, task) => sum + (Number(task.planned_minutes) || 0), 0);
  const doneMinutes = done.reduce((sum, task) => sum + (Number(task.planned_minutes) || 0), 0);

  taskCount.textContent = todayTasks.length;
  doneCount.textContent = done.length;
  plannedTime.textContent = hours(totalMinutes);
  remainingTime.textContent = hours(Math.max(0, totalMinutes - doneMinutes));
  themeLabel.textContent = currentTheme(day);
}

async function ensureDay(day) {
  const response = await fetch(`/api/today?date=${encodeURIComponent(day)}`, { cache: "no-store" });
  if (!response.ok) throw new Error("Could not load school day");
  const payload = await response.json();
  const all = await fetch("/api/tasks", { cache: "no-store" }).then(r => r.json());
  tasks = all.tasks || [];
  render();
}

async function load() {
  state = await fetch("/api/state", { cache: "no-store" }).then(r => r.json());
  renderRhythm();
  await ensureDay(dayInput.value);
}

async function updateTask(id, patch) {
  const response = await fetch(`/api/tasks/${encodeURIComponent(id)}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(patch),
  });
  if (!response.ok) return;
  const updated = await response.json();
  tasks = tasks.map(task => task.id === id ? updated : task);
  render();
}

document.querySelectorAll(".filter").forEach(button => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".filter").forEach(x => x.classList.remove("active"));
    button.classList.add("active");
    filter = button.dataset.filter;
    render();
  });
});

dayInput.addEventListener("change", () => ensureDay(dayInput.value));
document.querySelector("#add-task").addEventListener("click", () => {
  error.hidden = true;
  form.reset();
  dialog.showModal();
});
document.querySelector("#close-dialog").addEventListener("click", () => dialog.close());
document.querySelector("#cancel-task").addEventListener("click", () => dialog.close());

form.addEventListener("submit", async event => {
  event.preventDefault();
  error.hidden = true;
  const data = new FormData(form);
  const learner = data.get("learner");
  const payload = {
    date: dayInput.value,
    title: data.get("title"),
    planned_minutes: Number(data.get("planned_minutes") || 0),
    learner_ids: learner ? [learner] : [],
    scope: learner ? "individual" : "shared",
    notes: data.get("notes") || "",
    source: "manual",
  };

  const response = await fetch("/api/tasks", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const result = await response.json().catch(() => ({}));
    error.textContent = result.error || "Could not add task";
    error.hidden = false;
    return;
  }
  tasks.push(await response.json());
  dialog.close();
  render();
});

dayInput.value = todayISO();
load().catch(err => {
  empty.hidden = false;
  empty.textContent = err.message;
});
