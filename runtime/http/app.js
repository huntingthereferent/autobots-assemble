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

function localDateKey(date = new Date()) {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  return y + "-" + m + "-" + d;
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
  const d = s.systems["day-to-day"];
  const c = s.systems.calendar;
  const r = s.runtime;
  const values = [
    ["Notes", p.notes],
    ["Plans", p.plans],
    ["Tasks", p.tasks],
    ["Reminders", d.reminders],
    ["Calendar", c.events],
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

async function refreshCalendar() {
  const data = await api("/api/calendar");
  $("#calendar-events").replaceChildren(...data.events.map(function(e) {
    const when = e.starts_at || e.due_at || e.recurrence || "calendar";
    return item(e.title, when + " · " + e.referent, "");
  }));
}

async function refreshReminders() {
  const data = await api("/api/reminders");
  $("#reminders").replaceChildren(...data.reminders.map(function(r) {
    const when = r.local_time || r.cadence;
    return item(r.text, when + " · " + r.referent, "");
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

function renderAttention(result) {
  const tasks = result.tasks || result.items || [];
  const calendar = result.calendar || [];
  const reminders = result.reminders || [];

  $("#attention-tasks").replaceChildren(...tasks.map(function(x) {
    return item(
      x.title,
      x.status + " · " + x.referent,
      '<span class="status ' + x.status.toLowerCase() + '">' + x.status + "</span>"
    );
  }));

  $("#attention-calendar").replaceChildren(...calendar.map(function(x) {
    const when = x.starts_at || x.due_at || x.recurrence || "calendar";
    return item(x.title, when + " · " + x.referent, "");
  }));

  $("#attention-reminders").replaceChildren(...reminders.map(function(x) {
    const when = x.local_time || x.cadence || "reminder";
    const el = item(
      x.text,
      when + " · " + x.referent,
      '<button class="ack-reminder" data-id="' + x.id + '">Done today</button>'
    );
    el.querySelector(".ack-reminder").addEventListener("click", async function() {
      try {
        await api("/api/reminders/" + encodeURIComponent(x.id) + "/ack", {
          method: "POST",
          body: JSON.stringify({local_date: localDateKey()})
        });
        await refreshAll();
      } catch (err) { showError(err); }
    });
    return el;
  }));
}

async function refreshAttention() {
  try {
    const result = await api("/api/attention?actor=james");
    renderAttention(result);
  } catch (err) { showError(err); }
}

async function activateOhayo() {
  try {
    const result = await api("/api/activate?surface=ohayo&actor=james");
    $("#activation-note").textContent = result.note || "";
    renderAttention(result);
  } catch (err) { showError(err); }
}

async function refreshAll() {
  await Promise.all([
    refreshStatus(),
    refreshNotes(),
    refreshPlans(),
    refreshCalendar(),
    refreshReminders(),
    refreshTasks(),
    refreshHandoffs(),
    refreshAttention()
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

$("#calendar-form").addEventListener("submit", async function(event) {
  event.preventDefault();
  const f = new FormData(event.currentTarget);
  try {
    await api("/api/calendar", {
      method: "POST",
      body: JSON.stringify({
        title: f.get("title"),
        referent: f.get("referent"),
        participants: ["james"],
        starts_at: f.get("starts_at")
      })
    });
    event.currentTarget.reset();
    await refreshAll();
  } catch (err) { showError(err); }
});

$("#reminder-form").addEventListener("submit", async function(event) {
  event.preventDefault();
  const f = new FormData(event.currentTarget);
  try {
    await api("/api/reminders", {
      method: "POST",
      body: JSON.stringify({
        text: f.get("text"),
        referent: f.get("referent"),
        actor_id: "james",
        cadence: "daily",
        local_time: f.get("local_time")
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

setInterval(refreshAttention, 60000);
document.addEventListener("visibilitychange", function() {
  if (!document.hidden) refreshAttention();
});
