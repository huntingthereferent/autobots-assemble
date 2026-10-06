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

function areaCard(area) {
  const el = document.createElement("article");
  el.className = "area-card";
  el.id = "area-" + area.id;

  const heading = document.createElement("div");
  heading.className = "area-card-heading";
  const title = document.createElement("h3");
  title.textContent = area.name;
  const summary = document.createElement("p");
  summary.textContent = area.summary;
  heading.append(title, summary);

  const details = document.createElement("details");
  details.className = "area-details";
  const toggle = document.createElement("summary");
  toggle.textContent = "Open area";

  const fieldsLabel = document.createElement("p");
  fieldsLabel.className = "area-label";
  fieldsLabel.textContent = "Fields and entrances";
  const fields = document.createElement("div");
  fields.className = "area-chips";
  (area.entries || []).forEach(function(label) {
    const chip = document.createElement("span");
    chip.textContent = label;
    fields.appendChild(chip);
  });

  const toolsLabel = document.createElement("p");
  toolsLabel.className = "area-label";
  toolsLabel.textContent = "Things you can build here";
  const builders = document.createElement("div");
  builders.className = "area-chips builders";
  (area.builders || []).forEach(function(label) {
    const chip = document.createElement("span");
    chip.textContent = label;
    builders.appendChild(chip);
  });

  details.append(toggle, fieldsLabel, fields, toolsLabel, builders);
  el.append(heading, details);
  return el;
}

async function refreshAreas() {
  const data = await api("/site_catalog.json");
  $("#area-grid").replaceChildren(...(data.areas || []).map(areaCard));
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
    ["Live handoffs", r.handoffs],
    ["Traversal touches", r.touches || 0]
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
    const anchor = e.movement_anchor || "";
    return item(
      e.title,
      when + (anchor ? " · " + anchor : "") + " · " + e.referent,
      anchor ? '<span class="movement-anchor">' + anchor + '</span>' : ""
    );
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


let liveFeedState = {items: [], sources: [], fetched_at: ""};
let liveFeedFilter = "balanced";

function trailSessionId() {
  let value = sessionStorage.getItem("continuityTraceSession");
  if (!value) {
    value = (crypto.randomUUID ? crypto.randomUUID() : "session-" + Date.now());
    sessionStorage.setItem("continuityTraceSession", value);
  }
  return value;
}

function trailState() {
  return {
    parent: sessionStorage.getItem("continuityTraceParent") || "",
    referent: sessionStorage.getItem("continuityTraceReferent") || "Live mixed feed",
    depth: Number(sessionStorage.getItem("continuityTraceDepth") || "0")
  };
}

function renderTrail() {
  const state = trailState();
  $("#trail-current").textContent = state.referent;
  $("#trail-depth").textContent = state.depth + " touch" + (state.depth === 1 ? "" : "es");
}

function resetTrail() {
  sessionStorage.removeItem("continuityTraceParent");
  sessionStorage.removeItem("continuityTraceReferent");
  sessionStorage.removeItem("continuityTraceDepth");
  renderTrail();
}

function relativeTime(value) {
  if (!value) return "";
  const when = new Date(value);
  if (Number.isNaN(when.getTime())) return value;
  const seconds = Math.max(0, Math.floor((Date.now() - when.getTime()) / 1000));
  if (seconds < 60) return seconds + "s";
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return minutes + "m";
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return hours + "h";
  return Math.floor(hours / 24) + "d";
}

function metricText(metrics) {
  const parts = [];
  if (metrics && Number.isFinite(Number(metrics.score))) parts.push(String(metrics.score) + " score");
  if (metrics && Number.isFinite(Number(metrics.comments))) parts.push(String(metrics.comments) + " comments");
  return parts.join(" · ");
}

async function recordLiveTouch(item) {
  const state = trailState();
  const payload = {
    session_id: trailSessionId(),
    parent_trace_id: state.parent,
    surface_kind: item.source_kind || "external",
    locator: item.url,
    provider: item.source_name || item.source_id || "",
    label: item.title || "",
    referent_before: state.referent,
    relation: "open live feed item",
    referent_after: item.title || item.url,
    what_changed: "moved from the mixed live feed into an external source",
    provenance: ["live-feed:" + (item.source_id || "unknown"), String(item.id || "")]
  };

  try {
    const touch = await api("/api/traces", {
      method: "POST",
      body: JSON.stringify(payload)
    });
    sessionStorage.setItem("continuityTraceParent", touch.trace_id);
    sessionStorage.setItem("continuityTraceReferent", touch.referent_after || item.title || item.url);
    sessionStorage.setItem("continuityTraceDepth", String(state.depth + 1));
    renderTrail();
    refreshStatus().catch(showError);
  } catch (err) {
    if (state.parent && /parent trace does not exist/i.test(err.message || "")) {
      payload.parent_trace_id = "";
      const touch = await api("/api/traces", {
        method: "POST",
        body: JSON.stringify(payload)
      });
      sessionStorage.setItem("continuityTraceParent", touch.trace_id);
      sessionStorage.setItem("continuityTraceReferent", touch.referent_after || item.title || item.url);
      sessionStorage.setItem("continuityTraceDepth", "1");
      renderTrail();
      return;
    }
    throw err;
  }
}

function liveFeedCard(item) {
  const article = document.createElement("article");
  article.className = "live-item";
  article.dataset.kind = item.source_kind || "external";
  article.dataset.source = item.source_id || "";

  const head = document.createElement("div");
  head.className = "live-item-head";

  const source = document.createElement("div");
  source.className = "live-source";
  const sourceName = document.createElement("strong");
  sourceName.textContent = item.source_name || item.source_id || "External";
  const context = document.createElement("span");
  context.textContent = [item.context, relativeTime(item.published_at)].filter(Boolean).join(" · ");
  source.append(sourceName, context);

  const kind = document.createElement("span");
  kind.className = "source-chip";
  kind.textContent = item.native_type || item.source_kind || "external";
  head.append(source, kind);

  const title = document.createElement("h3");
  title.className = "live-title";
  title.textContent = item.title || "(untitled)";

  const byline = document.createElement("div");
  byline.className = "live-byline";
  const pieces = [];
  if (item.author) pieces.push(item.author);
  const metrics = metricText(item.metrics);
  if (metrics) pieces.push(metrics);
  byline.textContent = pieces.join(" · ");

  const snippet = document.createElement("p");
  snippet.className = "live-snippet";
  snippet.textContent = item.snippet || "";
  snippet.hidden = !item.snippet;

  const actions = document.createElement("div");
  actions.className = "live-actions";
  const open = document.createElement("button");
  open.className = "live-open";
  open.type = "button";
  open.textContent = item.source_kind === "video" ? "Watch" : "Open source";
  open.addEventListener("click", function() {
    const popup = window.open("about:blank", "_blank");
    recordLiveTouch(item).catch(showError).finally(function() {
      if (popup) {
        popup.opener = null;
        popup.location = item.url;
      } else {
        window.location.href = item.url;
      }
    });
  });

  const locator = document.createElement("span");
  locator.className = "live-locator";
  try {
    locator.textContent = new URL(item.url).hostname.replace(/^www\./, "");
  } catch (_) {
    locator.textContent = item.url;
  }
  actions.append(open, locator);

  article.append(head, title, byline, snippet, actions);
  return article;
}

function renderLiveSources() {
  const rows = (liveFeedState.sources || []).map(function(source) {
    const el = document.createElement("div");
    el.className = "live-source-status" + (source.ok ? " ok" : " unavailable");

    const copy = document.createElement("div");
    const name = document.createElement("strong");
    name.textContent = source.name;
    const meta = document.createElement("span");
    meta.textContent = source.ok
      ? source.count + " live · " + source.access
      : (source.reason || source.error || "unavailable");
    copy.append(name, meta);

    const mark = document.createElement("span");
    mark.className = "source-state";
    mark.textContent = source.ok ? "LIVE" : "—";
    el.append(copy, mark);
    return el;
  });
  $("#live-sources").replaceChildren(...rows);
}

function balancedLiveItems(items) {
  const groups = new Map();
  items.forEach(function(item) {
    const key = item.source_id || item.source_name || "external";
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(item);
  });
  const queues = Array.from(groups.values()).sort(function(a, b) {
    return String(b[0] && b[0].published_at || "").localeCompare(
      String(a[0] && a[0].published_at || "")
    );
  });
  const out = [];
  let moved = true;
  while (moved) {
    moved = false;
    queues.forEach(function(queue) {
      if (queue.length) {
        out.push(queue.shift());
        moved = true;
      }
    });
  }
  return out;
}

function renderLiveFeed() {
  const all = liveFeedState.items || [];
  let items;
  if (liveFeedFilter === "balanced") {
    items = balancedLiveItems(all);
  } else if (liveFeedFilter === "latest") {
    items = all;
  } else {
    items = balancedLiveItems(all.filter(function(item) {
      return item.source_kind === liveFeedFilter;
    }));
  }
  $("#live-feed").replaceChildren(...items.map(liveFeedCard));
  $("#empty-live-feed").hidden = items.length > 0;
  renderLiveSources();
}

async function refreshLiveFeed(force = false) {
  const data = await api("/api/live-feed" + (force ? "?force=1" : ""));
  liveFeedState = data;
  renderLiveFeed();
}

async function refreshHandoffs() {
  const data = await api("/api/handoffs");
  $("#handoffs").replaceChildren(...data.handoffs.map(function(h) {
    const title = (h.metadata && h.metadata.title) || h.required_relation;
    const source = (h.metadata && h.metadata.source_system) || h.from_actor;
    const el = item(
      title,
      h.to_actor + " · " + h.status + " · " + source,
      '<span class="source-chip">' + source + '</span><span class="status ' + h.status.toLowerCase() + '">' + h.status + "</span>"
    );
    el.classList.add("movement-entry");
    return el;
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
    const anchor = x.movement_anchor || "";
    return item(
      x.title,
      when + (anchor ? " · " + anchor : "") + " · " + x.referent,
      anchor ? '<span class="movement-anchor">' + anchor + '</span>' : ""
    );
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
    refreshAreas(),
    refreshLiveFeed(),
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

document.querySelectorAll("[data-live-filter]").forEach(function(button) {
  button.addEventListener("click", function() {
    liveFeedFilter = button.dataset.liveFilter || "all";
    document.querySelectorAll("[data-live-filter]").forEach(function(candidate) {
      candidate.classList.toggle("active", candidate === button);
    });
    renderLiveFeed();
  });
});

$("#refresh-live-feed").addEventListener("click", function() {
  refreshLiveFeed(true).catch(showError);
});

$("#reset-trail").addEventListener("click", resetTrail);
renderTrail();

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
        starts_at: f.get("starts_at"),
        movement_anchor: f.get("movement_anchor")
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
setInterval(function() {
  refreshLiveFeed(false).catch(showError);
}, 60000);
document.addEventListener("visibilitychange", function() {
  if (!document.hidden) {
    refreshAttention();
    refreshLiveFeed(false).catch(showError);
  }
});
