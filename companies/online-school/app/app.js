const $ = q => document.querySelector(q);

const welcome = $("#welcome");
const workspace = $("#workspace");
const welcomeForm = $("#welcome-form");
const welcomeError = $("#welcome-error");
const dayInput = $("#day");
const observationDialog = $("#observation-dialog");
const observationForm = $("#observation-form");
const observationError = $("#observation-error");
const switchDialog = $("#switch-dialog");
const placementDialog = $("#placement-dialog");
const placementForm = $("#placement-form");
const placementError = $("#placement-error");

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

function person() {
  return school?.learners?.find(x => x.id === selectedLearnerId)
    || school?.learners?.[0]
    || null;
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

function subjectInfo(text) {
  const key = subjectFor(text);
  const map = {
    math: ["Math", "✏️"],
    reading: ["Reading", "📖"],
    writing: ["Writing", "📝"],
    science: ["Science", "🔬"],
    history: ["History", "🧭"],
    art: ["Art", "🎨"],
    movement: ["Movement", "🏃"],
    learning: ["Learning", "✨"]
  };
  return {key, label: map[key][0], icon: map[key][1]};
}

function minutesText(minutes) {
  const n = Number(minutes) || 0;
  if (!n) return "";
  if (n < 60) return `${n} min`;
  const h = Math.floor(n / 60);
  const m = n % 60;
  return m ? `${h}h ${m}m` : `${h}h`;
}

function setMode(hasLearners) {
  welcome.hidden = hasLearners;
  workspace.hidden = !hasLearners;
}

function renderLearners() {
  const current = person();
  $("#learner-tabs").replaceChildren(...school.learners.map(item => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "learner-chip" + (item.id === current.id ? " active" : "");
    button.textContent = item.display_name;
    button.onclick = () => {
      selectedLearnerId = item.id;
      render();
    };
    return button;
  }));

  const profile = $("#profile-button");
  profile.textContent = (current.display_name || "?").slice(0, 1).toUpperCase();
  profile.title = current.display_name;
}

function renderFocus(item) {
  const focus = item.front?.do_next || null;
  const relation = item.front?.learning_now || null;
  const root = $("#focus-content");
  const empty = $("#focus-empty");
  const done = $("#focus-done");
  const startTest = $("#focus-start-test");
  const tell = $("#focus-tell");

  root.replaceChildren();

  if (!focus) {
    empty.hidden = false;
    done.hidden = true;
    startTest.hidden = true;
    tell.hidden = false;
    done.dataset.taskId = "";
    startTest.dataset.subject = "";
    return;
  }

  empty.hidden = true;
  const subject = subjectInfo(focus.title + " " + (focus.notes || ""));
  const tag = document.createElement("span");
  tag.className = "focus-tag";
  tag.textContent = `${subject.icon} ${subject.label}`;

  const title = document.createElement("h2");
  title.textContent = focus.title;

  const description = document.createElement("p");
  description.textContent = focus.notes || "This is something school has put in front of you today.";

  const meta = document.createElement("div");
  meta.className = "focus-meta";
  if (focus.planned_minutes) {
    const time = document.createElement("span");
    time.className = "meta-pill";
    time.textContent = `⏱ ${minutesText(focus.planned_minutes)}`;
    meta.append(time);
  }
  if (relation) {
    const known = document.createElement("span");
    known.className = "meta-pill";
    known.textContent = `🧠 ${relation.referent}`;
    meta.append(known);
  }

  root.append(tag, title, description, meta);
  const isPlacement = focus.source === "placement";
  startTest.hidden = !isPlacement;
  startTest.dataset.subject = isPlacement ? (focus.meta?.placement_subject || "") : "";
  tell.hidden = isPlacement;
  done.hidden = isPlacement || focus.status === "done";
  done.dataset.taskId = isPlacement ? "" : focus.id;
}

function taskCard(task) {
  const info = subjectInfo(task.title + " " + (task.notes || ""));
  const card = document.createElement("article");
  card.className = "task-card" + (task.status === "done" ? " done" : "");
  card.dataset.subject = info.key;
  const isPlacement = task.source === "placement";
  card.dataset.placement = isPlacement ? "true" : "false";

  const icon = document.createElement("span");
  icon.className = "task-icon";
  icon.textContent = info.icon;

  const check = document.createElement("button");
  check.type = "button";
  check.className = "task-check";
  check.textContent = task.status === "done" ? "✓" : "";
  check.setAttribute("aria-label", `Mark ${task.title} ${task.status === "done" ? "not done" : "done"}`);
  if (isPlacement) {
    check.hidden = true;
    card.tabIndex = 0;
    card.setAttribute("role", "button");
    card.onclick = () => openPlacement(task.meta?.placement_subject || "");
    card.onkeydown = event => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        openPlacement(task.meta?.placement_subject || "");
      }
    };
  } else {
    check.onclick = async () => {
      await patchTask(task.id, {status: task.status === "done" ? "todo" : "done"});
    };
  }

  const copy = document.createElement("div");
  const title = document.createElement("strong");
  title.textContent = task.title;
  const meta = document.createElement("small");
  meta.textContent = [info.label, minutesText(task.planned_minutes)].filter(Boolean).join(" · ");
  copy.append(title, meta);

  card.append(icon, check, copy);
  return card;
}

function renderToday(item) {
  const own = item.today_tasks || [];
  $("#today-list").replaceChildren(...own.map(taskCard));
  $("#today-empty").hidden = own.length !== 0;
  $("#shared-list").replaceChildren(...(school.shared_today || []).map(taskCard));

  const left = own.filter(x => x.status !== "done").length;
  $("#today-summary").textContent = left ? `${left} left` : own.length ? "all done ✓" : "open";
}

function renderNotice(item) {
  const root = $("#recent-change");
  root.replaceChildren();
  const observation = item.front?.what_changed;

  if (!observation) {
    const empty = document.createElement("div");
    empty.className = "friendly-empty";
    empty.textContent = "Nothing saved here yet. If you notice something, figure something out, or get stuck, you can add it.";
    root.append(empty);
    return;
  }

  const card = document.createElement("article");
  card.className = "notice-card";
  card.innerHTML = `
    <span class="notice-icon">💡</span>
    <div>
      <strong></strong>
      <p></p>
    </div>
  `;
  card.querySelector("strong").textContent = observation.referent;
  card.querySelector("p").textContent = observation.observed;
  root.append(card);
}

function renderArtifacts(item) {
  const root = $("#artifacts");
  const artifacts = item.artifacts || [];
  root.replaceChildren(...artifacts.slice(0, 8).map(work => {
    const card = document.createElement("a");
    card.className = "creation-card";
    card.href = "./worksheet.html";
    card.innerHTML = `
      <span class="creation-icon">🗂️</span>
      <strong></strong>
      <small></small>
    `;
    card.querySelector("strong").textContent = work.title || "Saved work";
    card.querySelector("small").textContent = work.knowledge_goal || work.template || "open";
    return card;
  }));
  $("#artifacts-empty").hidden = artifacts.length !== 0;
}

function renderGrownup(item) {
  $("#obligations").replaceChildren(...(item.curriculum_obligations || []).map(target => {
    const row = document.createElement("div");
    row.className = "requirement-row";
    row.innerHTML = "<strong></strong><span></span>";
    row.querySelector("strong").textContent = target.title;
    row.querySelector("span").textContent = target.description;
    return row;
  }));

  $("#rhythm-list").replaceChildren(...(state?.schedule?.daily_rhythm || []).map(block => {
    const row = document.createElement("div");
    row.className = "rhythm-row";
    row.innerHTML = "<strong></strong><span></span>";
    row.querySelector("strong").textContent = block.label;
    row.querySelector("span").textContent = block.start
      ? `${block.start}${block.end ? "–" + block.end : ""}`
      : "flexible";
    return row;
  }));

  const relations = item.current_relations || [];
  $("#all-relations").replaceChildren(...relations.map(relation => {
    const row = document.createElement("div");
    row.className = "relation-row";
    row.innerHTML = "<strong></strong><p></p>";
    row.querySelector("strong").textContent = relation.referent;
    const parts = [
      ...(relation.supported || []).map(x => `available: ${x}`),
      ...(relation.unsupported || []).map(x => `not yet: ${x}`)
    ];
    row.querySelector("p").textContent = parts.join(" · ") || "evidence recorded";
    return row;
  }));

  $("#boundaries").replaceChildren(...(school.boundaries || []).map(text => {
    const p = document.createElement("p");
    p.textContent = text;
    return p;
  }));
}

function renderSwitchList() {
  const current = person();
  $("#switch-list").replaceChildren(...school.learners.map(item => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "switch-person";
    button.innerHTML = `
      <span class="switch-avatar"></span>
      <span><strong></strong><small></small></span>
    `;
    button.querySelector(".switch-avatar").textContent = item.display_name.slice(0,1).toUpperCase();
    button.querySelector("strong").textContent = item.display_name;
    button.querySelector("small").textContent = item.id === current.id ? "You’re here now" : "Open this space";
    button.onclick = () => {
      selectedLearnerId = item.id;
      switchDialog.close();
      render();
    };
    return button;
  }));
}

function render() {
  const item = person();
  if (!item) {
    setMode(false);
    return;
  }

  setMode(true);
  renderLearners();

  $("#hello-name").textContent = `Hey, ${item.display_name}!`;
  const grade = item.adult
    ? `Age ${item.age} · unbounded workspace`
    : item.grade_context
      ? `Age ${item.age ?? "?"} · Grade ${item.grade_context} · your space`
      : `Age ${item.age ?? "?"} · your space`;
  $("#day-greeting").textContent = grade;
  $("#academic-lab").hidden = !item.adult;

  renderFocus(item);
  renderToday(item);
  renderNotice(item);
  renderArtifacts(item);
  renderGrownup(item);
  renderSwitchList();

  const learnerName = encodeURIComponent(item.display_name || item.id);
  const adultMode = item.adult ? "&mode=adult" : "";
  $("#studio-link").href = `./worksheet.html?learner=${learnerName}${adultMode}`;
  $("#create-worksheet-link").href = `./worksheet.html?learner=${learnerName}${adultMode}`;
  $("#academic-print-link").href = `./worksheet.html?learner=${learnerName}&mode=adult`;
}

async function load() {
  const day = dayInput.value;
  const [schoolResponse, stateResponse] = await Promise.all([
    fetch(`/api/school?date=${encodeURIComponent(day)}`, {cache:"no-store"}),
    fetch("/api/state", {cache:"no-store"})
  ]);

  if (!schoolResponse.ok || !stateResponse.ok) {
    throw new Error("Could not open the workspace");
  }

  school = await schoolResponse.json();
  state = await stateResponse.json();

  if (!school.learners?.length) {
    selectedLearnerId = null;
    setMode(false);
    return;
  }

  if (!selectedLearnerId || !school.learners.some(x => x.id === selectedLearnerId)) {
    selectedLearnerId = school.learners[0].id;
  }
  render();
}

async function patchTask(id, patch) {
  const response = await fetch(`/api/tasks/${encodeURIComponent(id)}`, {
    method:"PATCH",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify(patch)
  });
  if (!response.ok) throw new Error("Could not update that");
  await load();
}

async function createLearner(data) {
  const response = await fetch("/api/learners", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify(data)
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.error || "Could not create your space");
  selectedLearnerId = body.id;
  return body;
}

welcomeForm.addEventListener("submit", async event => {
  event.preventDefault();
  welcomeError.hidden = true;
  const data = new FormData(welcomeForm);
  try {
    await createLearner({
      display_name:data.get("display_name"),
      age:data.get("age"),
      grade_context:data.get("grade_context")
    });
    welcomeForm.reset();
    await load();
  } catch (err) {
    welcomeError.textContent = err.message;
    welcomeError.hidden = false;
  }
});


async function openPlacement(subject) {
  const learner = person();
  if (!learner || !subject) return;
  placementError.hidden = true;
  const response = await fetch(`/api/placement?learner=${encodeURIComponent(learner.id)}`, {cache:"no-store"});
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    alert(body.error || "Could not open placement");
    return;
  }

  const section = (body.sections || []).find(item => item.subject === subject);
  if (!section) {
    alert("Placement section not found");
    return;
  }

  placementForm.dataset.subject = subject;
  $("#placement-title").textContent = section.title;
  $("#placement-intro").textContent = section.description || "";
  const root = $("#placement-items");
  root.replaceChildren();

  if (subject === "mathematics") {
    let currentBand = "";
    for (const item of section.diagnostic.items || []) {
      if (item.band !== currentBand) {
        currentBand = item.band;
        const band = document.createElement("div");
        band.className = "placement-band";
        band.textContent = item.band_label;
        root.append(band);
      }
      const row = document.createElement("label");
      row.className = "placement-item";
      row.innerHTML = "<small></small><strong></strong><input autocomplete=\"off\">";
      row.querySelector("small").textContent = item.domain.replaceAll("-", " ");
      row.querySelector("strong").textContent = item.prompt;
      row.querySelector("input").name = item.id;
      root.append(row);
    }
  } else {
    const prompts = section.prompts || [];
    prompts.forEach((prompt, index) => {
      const row = document.createElement("label");
      row.className = "placement-item";
      row.innerHTML = "<strong></strong><textarea></textarea>";
      row.querySelector("strong").textContent = prompt;
      row.querySelector("textarea").name = `q${index + 1}`;
      root.append(row);
    });
  }

  placementDialog.showModal();
}

$("#focus-start-test").onclick = event => {
  openPlacement(event.currentTarget.dataset.subject || "");
};
$("#close-placement").onclick = () => placementDialog.close();

placementForm.addEventListener("submit", async event => {
  event.preventDefault();
  placementError.hidden = true;
  const learner = person();
  const subject = placementForm.dataset.subject;
  const data = new FormData(placementForm);
  const responses = {};
  for (const [key, value] of data.entries()) {
    responses[key] = String(value).trim();
  }

  try {
    const response = await fetch("/api/placement/submit", {
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify({
        learner_id: learner.id,
        subject,
        responses
      })
    });
    const body = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(body.error || "Could not submit placement");
    placementDialog.close();

    if (subject === "mathematics" && body.result?.start_band) {
      alert(`Math starting band: ${body.result.start_band}`);
    }
    await load();
  } catch (err) {
    placementError.textContent = err.message;
    placementError.hidden = false;
  }
});

function openObservation() {
  observationError.hidden = true;
  observationForm.reset();
  const focus = person()?.front?.do_next;
  if (focus) observationForm.elements.referent.value = focus.title;
  observationDialog.showModal();
}

$("#focus-tell").onclick = openObservation;
$("#add-notice").onclick = openObservation;
$("#close-observation").onclick = () => observationDialog.close();

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
        provenance:[`online-school:kid-workspace:${dayInput.value}`]
      })
    });
    const body = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(body.error || "Could not save that");
    observationDialog.close();
    await load();
  } catch (err) {
    observationError.textContent = err.message;
    observationError.hidden = false;
  }
});

$("#focus-done").onclick = async event => {
  const id = event.currentTarget.dataset.taskId;
  if (id) await patchTask(id, {status:"done"});
};

$("#profile-button").onclick = () => switchDialog.showModal();
$("#close-switch").onclick = () => switchDialog.close();
$("#add-person").onclick = () => {
  switchDialog.close();
  setMode(false);
  welcomeForm.elements.display_name.focus();
};

document.querySelectorAll("[data-jump]").forEach(button => {
  button.onclick = () => {
    const key = subjectFor(button.dataset.jump);
    const match = [...document.querySelectorAll(".task-card")].find(card => card.dataset.subject === key);
    if (match) {
      match.scrollIntoView({behavior:"smooth", block:"center"});
      match.animate(
        [{transform:"scale(1)"},{transform:"scale(1.035)"},{transform:"scale(1)"}],
        {duration:420}
      );
    } else {
      $("#today").scrollIntoView({behavior:"smooth", block:"start"});
    }
  };
});


const academicPrompts = {
  research: "What are you researching?",
  reading: "What are you reading or trying to understand?",
  notes: "What are you taking notes on?",
  writing: "What are you writing?",
  projects: "What are you building or making?",
  experiments: "What are you testing?",
  "sources-citations": "What source trail are you working on?",
  artifacts: "What are you making or preserving?"
};

document.querySelectorAll("button[data-academic]").forEach(button => {
  button.onclick = async () => {
    const kind = button.dataset.academic;
    const title = window.prompt(academicPrompts[kind] || "What are you working on?");
    if (!title?.trim()) return;
    const item = person();
    const response = await fetch("/api/tasks", {
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify({
        date:dayInput.value,
        title:title.trim(),
        planned_minutes:null,
        learner_ids:[item.id],
        scope:"individual",
        kind:"academic",
        notes:`Academic tool: ${kind}`,
        source:"adult-academic-workspace",
        meta:{academic_tool:kind, unbounded:true}
      })
    });
    if (!response.ok) {
      const body = await response.json().catch(() => ({}));
      alert(body.error || "Could not add that");
      return;
    }
    await load();
    $("#today").scrollIntoView({behavior:"smooth", block:"start"});
  };
});

dayInput.onchange = load;
dayInput.value = todayISO();

load().catch(err => {
  setMode(false);
  welcomeError.textContent = err.message;
  welcomeError.hidden = false;
});