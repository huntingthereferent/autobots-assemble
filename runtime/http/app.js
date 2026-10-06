const $ = (q) => document.querySelector(q);
const errorBox = $("#error");

async function api(path, options = {}) {
  const response = await fetch(path, {
    cache: "no-store",
    headers: Object.assign(
      {"Content-Type": "application/json"},
      options.headers || {}
    ),
    ...options
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.error || response.statusText);
  return body;
}

function showError(err) {
  errorBox.textContent = err.message || String(err);
  errorBox.hidden = false;
  clearTimeout(showError.timer);
  showError.timer = setTimeout(() => { errorBox.hidden = true; }, 5000);
}

function item(title, meta, extra) {
  const el = document.createElement("div");
  el.className = "item";
  el.innerHTML =
    '<div class="item-head">' +
      '<div class="item-title"></div>' +
      (extra || "") +
    '</div>' +
    '<div class="meta"></div>';
  el.querySelector(".item-title").textContent = title;
  el.querySelector(".meta").textContent = meta || "";
  return el;
}

async function refreshStatus() {
  const s = await api("/api/status");
  const p = s.systems["personal-operations"];
  const r = s.runtime;
  const values = [
    ["Notes", p.notes],
    ["Plans", p.plans],
    ["Tasks", p.tasks],
    ["Live handoffs", r.handoffs]
  ];
  $("#stats").replaceChildren(...values.map(function(pair) {
    const el = document.createElement("article");
    el.className = "stat";
    el.innerHTML = "<span></span><strong></strong>";
    el.querySelector("span").textContent = pair[0];
    el.querySelector("strong").textContent = pair[1];
    return el;
  }));
}

async function refreshNotes() {
  const data = await api("/api/notes");
  $("#notes").replaceChildren(...data.notes.map(function(n) {
    return item(n.body, n.referent || "note", "");
  }));
}

async function refreshPlans() {
  const data = await api("/api/plans");
  $("#plans").replaceChildren(...data.plans.map(function(p) {
    return item(
      p.title,
      p.referent + " · " + p.steps.length + " step(s)",
      ""
    );
  }));
}

async function refreshTasks() {
  const data = await api("/api/tasks");
  $("#tasks").replaceChildren(...data.tasks.map(function(t) {
    const admitted = Boolean(t.admitted_handoff_id);
    const result = t.result && t.result.status;
    const extra = admitted
      ? '<span class="status ' + String(result || "ready").toLowerCase() + '">' + (result || "ADMITTED") + "</span>"
      : '<button class="admit" data-id="' + t.task_id + '">Admit</button>';
    const el = item(t.title, t.assignee + " · " + t.referent, extra);
    const button = el.querySelector(".admit");
    if (button) {
      button.addEventListener("click", async function() {
        try {
          await api("/api/tasks/" + encodeURIComponent(t.task_id) + "/admit", {
            method: "POST",
            body: "{}"
          });
          await refreshAll();
          await activateOhayo();
        } catch (err) { showError(err); }
      });
    }
    return el;
  }));
}

async function refreshHandoffs() {
  const data = await api("/api/handoffs");
  $("#handoffs").replaceChildren(...data.handoffs.map(function(h) {
    const title = (h.metadata && h.metadata.title) || h.required_relation;
    const source = (h.metadata && h.metadata.source_system) || h.from_actor;
    return item(
      title,
      h.to_actor + " · " + h.status + " · " + source,
      '<span class="status ' + h.status.toLowerCase() + '">' + h.status + "</span>"
    );
  }));
}

async function activateOhayo() {
  try {
    const result = await api("/api/activate?surface=ohayo&actor=james");
    $("#activation-note").textContent = result.note || "";
    $("#ohayo-list").replaceChildren(...result.items.map(function(x) {
      return item(
        x.title,
        x.status + " · " + x.referent,
        '<span class="status ' + x.status.toLowerCase() + '">' + x.status + "</span>"
      );
    }));
  } catch (err) { showError(err); }
}

async function refreshAll() {
  await Promise.all([
    refreshStatus(),
    refreshNotes(),
    refreshPlans(),
    refreshTasks(),
    refreshHandoffs()
  ]);
}

$("#ohayo").addEventListener("click", activateOhayo);

$("#note-form").addEventListener("submit", async function(event) {
  event.preventDefault();
  const f = new FormData(event.currentTarget);
  try {
    await api("/api/notes", {
      method: "POST",
      body: JSON.stringify({
        body: f.get("body"),
        referent: f.get("referent"),
        actor_id: "james"
      })
    });
    event.currentTarget.reset();
    await refreshAll();
  } catch (err) { showError(err); }
});

$("#plan-form").addEventListener("submit", async function(event) {
  event.preventDefault();
  const f = new FormData(event.currentTarget);
  try {
    await api("/api/plans", {
      method: "POST",
      body: JSON.stringify({
        title: f.get("title"),
        referent: f.get("referent"),
        actor_id: "james",
        steps: String(f.get("steps") || "").split("\n").map(function(x) {
          return x.trim();
        }).filter(Boolean)
      })
    });
    event.currentTarget.reset();
    await refreshAll();
  } catch (err) { showError(err); }
});

$("#task-form").addEventListener("submit", async function(event) {
  event.preventDefault();
  const f = new FormData(event.currentTarget);
  try {
    await api("/api/tasks", {
      method: "POST",
      body: JSON.stringify({
        title: f.get("title"),
        referent: f.get("referent"),
        assignee: f.get("assignee")
      })
    });
    event.currentTarget.reset();
    event.currentTarget.elements.assignee.value = "james";
    await refreshAll();
  } catch (err) { showError(err); }
});

refreshAll().then(activateOhayo).catch(showError);
