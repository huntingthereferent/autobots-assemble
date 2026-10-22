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

function cardChip(className, text) {
  const chip = document.createElement("span");
  chip.className = className;
  chip.textContent = String(text ?? "");
  return chip;
}
function statusClass(value) {
  return String(value ?? "unknown").toLowerCase().replace(/[^a-z0-9_-]/g, "-").slice(0,64);
}
function item(title, meta, extra) {
  const el = document.createElement("div");
  el.className = "item";
  const head = document.createElement("div");
  head.className = "item-head";
  const heading = document.createElement("div");
  heading.className = "item-title";
  heading.textContent = title;
  head.append(heading);
  if (extra) head.append(...(Array.isArray(extra) ? extra : [extra]));
  const sub = document.createElement("div");
  sub.className = "meta";
  sub.textContent = meta || "";
  el.append(head, sub);
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
      anchor ? cardChip("movement-anchor", anchor) : null
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
    let extra, button = null;
    if (admitted) {
      extra = cardChip("status " + statusClass(result || "ready"), result || "ADMITTED");
    } else {
      button = document.createElement("button");
      button.type = "button";
      button.className = "admit";
      button.dataset.id = String(t.task_id);
      button.textContent = "Admit";
      extra = button;
    }
    const el = item(t.title, t.assignee + " · " + t.referent, extra);
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
const TICKER_PREFERENCE_KEY = "continuityHiddenTickersV1";
let hiddenTickers = readHiddenTickers();

function readHiddenTickers() {
  try {
    const value = JSON.parse(localStorage.getItem(TICKER_PREFERENCE_KEY) || "[]");
    return new Set(Array.isArray(value) ? value.filter(x => typeof x === "string") : []);
  } catch (_) { return new Set(); }
}

function saveTickerChoices() {
  // Save presentation choices only; feed contents remain in memory.
  try { localStorage.setItem(TICKER_PREFERENCE_KEY, JSON.stringify([...hiddenTickers])); }
  catch (_) {}
}

// Native topic labels admit a witness to a layer; headlines never assign it.
const TICKER_DOMAINS = [
  {id: "world", name: "World", children: ["countries", "regions", "cities", "local"]},
  {id: "industry", name: "Industry / Factory", children: ["sectors", "companies", "production", "deliveries", "operations"]},
  {id: "markets", name: "Markets", children: ["stocks", "commodities", "currencies", "crypto"]},
  {id: "sports", name: "Sports", children: ["leagues", "teams", "games", "results", "standings"]},
  {id: "work", name: "Work", children: ["opportunities", "projects", "tasks", "handoffs"]},
  {id: "learning", name: "Learning", children: ["learners", "subjects", "assignments", "progress"]},
  {id: "research", name: "Research", children: ["questions", "experiments", "findings", "boundaries"]},
  {id: "household", name: "Personal / Household", children: ["calendar", "routines", "reminders", "household"]},
  {id: "culture", name: "Culture / Social", children: ["communities", "conversations", "music", "video", "events"]}
];

function nativeTickerTopics(item) {
  return Array.isArray(item.topics)
    ? item.topics.filter(topic => typeof topic === "string").map(topic => topic.trim().toLowerCase())
    : [];
}

function domainTickerLayers(items, sources = []) {
  const layers = [];
  TICKER_DOMAINS.forEach(function(domain) {
    const prefix = domain.id + ":";
    const rows = items.filter(function(item) {
      return nativeTickerTopics(item).some(topic => topic === domain.id || topic.startsWith(prefix));
    });
    const rootId = "domain:" + domain.id;
    const configured = sources.filter(source => nativeTickerTopics(source)
      .some(topic => topic === domain.id || topic.startsWith(prefix)));
    layers.push({id: rootId, name: domain.name, items: rows, domain: true, sources: configured});
    const branches = new Set(domain.children);
    // Source-provided paths add concrete countries, companies, leagues, etc.
    [...rows, ...configured].forEach(item => nativeTickerTopics(item).forEach(function(topic) {
      if (topic.startsWith(prefix) && topic.slice(prefix.length)) {
        const parts = topic.slice(prefix.length).split(":").filter(Boolean);
        parts.forEach((_, index) => branches.add(parts.slice(0, index + 1).join(":")));
      }
    }));
    branches.forEach(function(branch) {
      const topic = prefix + branch;
      const parentBranch = branch.includes(":") ? branch.slice(0, branch.lastIndexOf(":")) : "";
      layers.push({id: "domain:" + topic, parentId: parentBranch ? "domain:" + prefix + parentBranch : rootId,
        name: branch.split(":").slice(-1)[0], domain: true,
        sources: configured.filter(source => nativeTickerTopics(source)
          .some(tag => tag === topic || tag.startsWith(topic + ":"))),
        items: rows.filter(item => nativeTickerTopics(item).some(tag => tag === topic || tag.startsWith(topic + ":")))});
    });
  });
  return layers;
}

function tickerLayers(snapshot) {
  const items = snapshot.items || [];
  const layers = [
    {id: "all", name: "All feeds", items},
    ...["news", "social", "video", "community"].map(function(role) {
      return {id: "role:" + role, name: role[0].toUpperCase() + role.slice(1),
        items: items.filter(item => liveItemMatchesFilter(item, role))};
    }),
    ...domainTickerLayers(items, snapshot.sources || [])
  ];
  const sources = new Map((snapshot.sources || []).map(source => [source.id, source]));
  items.forEach(function(item) {
    if (!sources.has(item.source_id)) sources.set(item.source_id,
      {id: item.source_id, name: item.source_name || item.source_id, ok: null});
  });
  sources.forEach(function(source) {
    layers.push({id: "source:" + source.id, name: source.name,
      source, items: items.filter(item => item.source_id === source.id)});
  });
  return layers;
}

function tickerSummary(layer, snapshot) {
  const items = layer.items;
  const dated = items.map(item => ({item, time: Date.parse(item.published_at)}))
    .filter(entry => Number.isFinite(entry.time)).sort((a, b) => b.time - a.time);
  const sourceCount = new Set(items.map(item => item.source_id)).size;
  const unavailable = layer.source && layer.source.ok === false;
  const configured = layer.sources || [];
  const noAvailableSources = configured.length && configured.every(source => source.ok === false);
  const status = unavailable ? "Unavailable" :
    (items.length ? items.length + " witnesses · " + sourceCount + " feeds" :
      noAvailableSources ? "Sources unavailable" :
      layer.domain && !configured.length ? "No connected witnesses" : "No sampled items");
  return {
    status,
    latest: dated.length ? dated[0].item : null,
    from: dated.length ? dated[dated.length - 1].item.published_at : "",
    to: dated.length ? dated[0].item.published_at : "",
    fetchedAt: snapshot.fetched_at || "",
    undated: items.length - dated.length,
    reason: unavailable ? layer.source.reason || layer.source.error || "Provider unavailable" : ""
  };
}

function tickerSourceBranches(layer, snapshot) {
  const sources = new Map((snapshot.sources || []).map(source => [source.id, source]));
  const branches = new Map();
  (layer.sources || []).forEach(function(source) {
    branches.set(source.id, {id: layer.id + "/source:" + source.id,
      name: source.name, source, items: []});
  });
  layer.items.forEach(function(item) {
    if (!branches.has(item.source_id)) {
      branches.set(item.source_id, {id: layer.id + "/source:" + item.source_id,
        name: item.source_name || item.source_id || "Unknown source",
        source: sources.get(item.source_id), items: []});
    }
    branches.get(item.source_id).items.push(item);
  });
  return [...branches.values()];
}

function tickerCard(layer, snapshot, openIds, childLayers = []) {
  const data = tickerSummary(layer, snapshot);
  const ticker = document.createElement("details");
  ticker.className = "feed-ticker" + (layer.parentId ? " ticker-child" : "");
  ticker.dataset.ticker = layer.id;
  ticker.open = openIds.has(layer.id);
  const summary = document.createElement("summary");
  const name = document.createElement("strong");
  name.textContent = layer.name;
  const status = document.createElement("span");
  status.className = "ticker-status";
  status.textContent = data.status + (layer.items.length ? " · fetched sample" : "");
  const headline = document.createElement("span");
  headline.className = "ticker-headline";
  headline.textContent = data.latest ? data.latest.title : data.reason || "No dated headline";
  summary.append(name, status, headline);
  const scope = document.createElement("p");
  scope.className = "ticker-scope";
  scope.textContent = "Fetched: " + (data.fetchedAt || "not yet") +
    (data.from ? " · Published: " + data.from + " → " + data.to : "") +
    (data.undated ? " · " + data.undated + " undated" : "");
  ticker.append(summary, scope);
  childLayers.forEach(child => ticker.append(tickerCard(child, snapshot, openIds,
    snapshot.tickerChildren ? snapshot.tickerChildren.get(child.id) || [] : [])));
  // Domain witnesses remain under their native sources, without synthesizing claims.
  if (layer.domain) {
    const sources = document.createElement("details");
    sources.className = "ticker-source-nest";
    sources.dataset.ticker = layer.id + "/sources";
    sources.open = openIds.has(sources.dataset.ticker);
    const label = document.createElement("summary");
    label.textContent = "Sources · " + tickerSourceBranches(layer, snapshot).length;
    sources.append(label, ...tickerSourceBranches(layer, snapshot).map(source =>
      tickerCard(source, snapshot, openIds)));
    ticker.append(sources);
  } else ticker.append(...groupLiveItems(layer.items).map(liveEventCard));
  return ticker;
}

function openTickerIds(root) {
  const ids = new Set();
  function visit(node) {
    if (node.open && node.dataset && node.dataset.ticker) ids.add(node.dataset.ticker);
    Array.from(node.children || []).forEach(visit);
  }
  visit(root);
  return ids;
}

function renderTickers() {
  const layers = tickerLayers(liveFeedState);
  const choices = layers.map(function(layer) {
    const label = document.createElement("label");
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.checked = !hiddenTickers.has("*") && !hiddenTickers.has(layer.id);
    checkbox.addEventListener("change", function() {
      if (hiddenTickers.has("*")) {
        hiddenTickers.delete("*");
        layers.forEach(other => hiddenTickers.add(other.id));
      }
      if (checkbox.checked) hiddenTickers.delete(layer.id);
      else hiddenTickers.add(layer.id);
      saveTickerChoices();
      renderTickers();
    });
    label.append(checkbox, document.createTextNode(layer.parentId
      ? layer.id.slice(7).replace(/:/g, " / ") : layer.name));
    return label;
  });
  const openIds = openTickerIds($("#feed-tickers"));
  const visible = layers.filter(layer => !hiddenTickers.has("*") && !hiddenTickers.has(layer.id));
  const visibleIds = new Set(visible.map(layer => layer.id));
  const children = new Map();
  visible.forEach(function(layer) {
    if (layer.parentId && visibleIds.has(layer.parentId)) {
      if (!children.has(layer.parentId)) children.set(layer.parentId, []);
      children.get(layer.parentId).push(layer);
    }
  });
  const projection = {...liveFeedState, tickerChildren: children};
  const tickers = visible.filter(layer => !layer.parentId || !visibleIds.has(layer.parentId))
    .map(layer => tickerCard(layer, projection, openIds, children.get(layer.id) || []));
  $("#ticker-choices").replaceChildren(...choices);
  $("#feed-tickers").replaceChildren(...tickers);
  $("#feed-tickers").hidden = tickers.length === 0;
}

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

function trailLabels() {
  try {
    return JSON.parse(sessionStorage.getItem("continuityTraceLabels") || "[]");
  } catch (_) {
    return [];
  }
}

function updateTrailAfterTouch(touch, item, depth) {
  const labels = trailLabels();
  labels.push({
    source: item.source_name || item.source_id || "External",
    label: item.title || item.url
  });
  sessionStorage.setItem("continuityTraceLabels", JSON.stringify(labels.slice(-12)));
  sessionStorage.setItem("continuityTraceParent", touch.trace_id);
  sessionStorage.setItem("continuityTraceReferent", touch.referent_after || item.title || item.url);
  sessionStorage.setItem("continuityTraceDepth", String(depth));
  renderTrail();
}

function renderTrail() {
  const state = trailState();
  const path = $("#trail-path");
  const nodes = [];

  const root = document.createElement("span");
  root.className = "trail-node muted";
  root.textContent = "Mixed feed";
  nodes.push(root);

  trailLabels().slice(-3).forEach(function(entry) {
    const arrow = document.createElement("span");
    arrow.className = "trail-arrow";
    arrow.textContent = "→";

    const node = document.createElement("span");
    node.className = "trail-node";
    node.title = entry.label || entry.source;
    node.textContent = entry.source || entry.label;

    nodes.push(arrow, node);
  });

  path.replaceChildren(...nodes);
  $("#trail-depth").textContent = state.depth + " touch" + (state.depth === 1 ? "" : "es");
}

function resetTrail() {
  sessionStorage.removeItem("continuityTraceParent");
  sessionStorage.removeItem("continuityTraceReferent");
  sessionStorage.removeItem("continuityTraceDepth");
  sessionStorage.removeItem("continuityTraceLabels");
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
    surface_kind: item.provider_surface || item.medium || "external",
    locator: item.url,
    provider: item.provider || item.source_name || item.source_id || "",
    label: item.title || "",
    referent_before: state.referent,
    relation: "open live feed item",
    referent_after: item.title || item.url,
    what_changed: "moved from the mixed live feed into an external source",
    provenance: [
      "live-feed:" + (item.source_id || "unknown"),
      "provider:" + (item.provider || item.source_name || "unknown"),
      item.publisher ? "publisher:" + item.publisher : "",
      item.medium ? "medium:" + item.medium : "",
      item.topic_basis && item.topic_basis.feed_url ? "coverage-feed:" + item.topic_basis.feed_url : "",
      ...((item.topics || []).map(function(topic) { return "topic:" + topic; })),
      ...((item.roles || []).map(function(role) { return "role:" + role; })),
      String(item.id || "")
    ].filter(Boolean)
  };

  try {
    const touch = await api("/api/traces", {
      method: "POST",
      body: JSON.stringify(payload)
    });
    updateTrailAfterTouch(touch, item, state.depth + 1);
    refreshStatus().catch(showError);
  } catch (err) {
    if (state.parent && /parent trace does not exist/i.test(err.message || "")) {
      payload.parent_trace_id = "";
      const touch = await api("/api/traces", {
        method: "POST",
        body: JSON.stringify(payload)
      });
      sessionStorage.removeItem("continuityTraceLabels");
      updateTrailAfterTouch(touch, item, 1);
      return;
    }
    throw err;
  }
}

function openLiveItem(item) {
  const popup = window.open("about:blank", "_blank");
  recordLiveTouch(item).catch(showError).finally(function() {
    if (popup) {
      popup.opener = null;
      popup.location = item.url;
    } else {
      window.location.href = item.url;
    }
  });
}

function liveFeedCard(item) {
  const article = document.createElement("article");
  article.className = "live-item";
  const roles = item.roles || [];
  article.dataset.kind = item.medium === "video"
    ? "video"
    : (roles[0] || item.provider_surface || "external");
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

  const identity = document.createElement("div");
  identity.className = "identity-chips";
  const labels = []
    .concat(item.medium ? [item.medium] : [])
    .concat(item.roles || []);
  Array.from(new Set(labels)).slice(0, 3).forEach(function(label) {
    const chip = document.createElement("span");
    chip.className = "source-chip";
    chip.textContent = label;
    identity.appendChild(chip);
  });
  head.append(source, identity);

  const title = document.createElement("h3");
  title.className = "live-title";
  const titleLink = document.createElement("button");
  titleLink.type = "button";
  titleLink.className = "live-title-link";
  titleLink.textContent = item.title || "(untitled)";
  titleLink.addEventListener("click", function() {
    openLiveItem(item);
  });
  title.appendChild(titleLink);

  const byline = document.createElement("div");
  byline.className = "live-byline";
  const pieces = [];
  if (item.author) pieces.push(item.author);
  if (item.topic_basis && item.topic_basis.kind === "publisher_feed_scope") {
    if (item.country) pieces.push("Source jurisdiction: " + item.country + " · Language: " + (item.language || "unspecified"));
    pieces.push("Coverage: " + (item.topics || []).join(", ") + " · publisher feed scope");
  }
  const metrics = metricText(item.metrics);
  if (metrics) pieces.push(metrics);
  try {
    pieces.push(new URL(item.url).hostname.replace(/^www\./, ""));
  } catch (_) {}
  byline.textContent = pieces.join(" · ");

  const snippet = document.createElement("p");
  snippet.className = "live-snippet";
  snippet.textContent = item.snippet || "";
  snippet.hidden = !item.snippet;

  article.append(head, title, byline, snippet);
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

function liveItemMatchesFilter(item, filter) {
  if (filter === "all" || filter === "balanced" || filter === "latest") return true;
  const roles = item.roles || [];
  if (filter === "video") return item.medium === "video";
  return roles.includes(filter);
}

function liveGroupingEvidence(item) {
  let locator = "";
  try {
    const url = new URL(item.url);
    if (["http:", "https:"].includes(url.protocol) && url.pathname !== "/") {
      url.hash = "";
      locator = url.href;
    }
  } catch (_) {}
  const title = String(item.title || "").trim().replace(/\s+/g, " ").toLowerCase();
  // Truncated or short generic headlines cannot establish a shared referent.
  const headline = title.length >= 32 && title.split(" ").length >= 6
    && !title.endsWith("…") ? title : "";
  const time = item.published_at ? Date.parse(item.published_at) : NaN;
  return {locator, headline, time};
}

function groupLiveItems(items) {
  // A display relationship only: no synthesized headline, claim or durable event.
  // Require one common witness across the entire group; never chain A~B~C.
  const groups = [];
  items.forEach(function(item) {
    const evidence = liveGroupingEvidence(item);
    const group = groups.find(function(candidate) {
      const witnesses = candidate.items.map(liveGroupingEvidence);
      return (evidence.locator && witnesses.every(function(other) {
        return other.locator === evidence.locator;
      })) || (evidence.headline && Number.isFinite(evidence.time)
        && witnesses.every(function(other) {
          return other.headline === evidence.headline && Number.isFinite(other.time);
        }) && Math.max(evidence.time, ...witnesses.map(x => x.time))
          - Math.min(evidence.time, ...witnesses.map(x => x.time)) <= 86400000);
    });
    if (group) group.items.push(item);
    else groups.push({items: [item]});
  });
  return groups;
}

function liveEventCard(group) {
  if (group.items.length === 1) return liveFeedCard(group.items[0]);
  const section = document.createElement("section");
  section.className = "live-event";
  const evidence = group.items.map(liveGroupingEvidence);
  const sameLocator = evidence[0].locator && evidence.every(function(other) {
    return other.locator === evidence[0].locator;
  });
  const label = document.createElement("p");
  label.className = "live-event-label";
  label.textContent = group.items.length + " source witnesses · "
    + (sameLocator ? "shared source URL" : "matching headline within 24h")
    + " · claims kept separate";
  section.append(label, ...group.items.map(liveFeedCard));
  return section;
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
      return liveItemMatchesFilter(item, liveFeedFilter);
    }));
  }
  $("#live-feed").replaceChildren(...groupLiveItems(items).map(liveEventCard));
  $("#empty-live-feed").hidden = items.length > 0;
  renderLiveSources();
  renderTickers();
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
      [cardChip("source-chip", source),
       cardChip("status " + statusClass(h.status), h.status)]
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
      cardChip("status " + statusClass(x.status), x.status)
    );
  }));

  $("#attention-calendar").replaceChildren(...calendar.map(function(x) {
    const when = x.starts_at || x.due_at || x.recurrence || "calendar";
    const anchor = x.movement_anchor || "";
    return item(
      x.title,
      when + (anchor ? " · " + anchor : "") + " · " + x.referent,
      anchor ? cardChip("movement-anchor", anchor) : null
    );
  }));

  $("#attention-reminders").replaceChildren(...reminders.map(function(x) {
    const when = x.local_time || x.cadence || "reminder";
    const button = document.createElement("button");
    button.type = "button";
    button.className = "ack-reminder";
    button.dataset.id = String(x.id);
    button.textContent = "Done today";
    const el = item(x.text, when + " · " + x.referent, button);
    button.addEventListener("click", async function() {
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

async function activateOhayo({start = false} = {}) {
  try {
    // Passive page loads never create work; explicit button activation may.
    const result = start
      ? await api("/api/ohayo", {
          method: "POST",
          body: JSON.stringify({actor_id: "james"})
        })
      : await api("/api/activate?surface=ohayo&actor=james");
    const summary = result.agent_summary || {};
    const counts = "Agents: " + (summary.total || 0) +
      " · Ready: " + (summary.ready || 0) +
      " · Complete: " + (summary.complete || 0) +
      " · Closed loops: " + (summary.closed_loops || 0);
    const last = (result.agent_activity || []).slice(-2)
      .map(x => x.event + " · " + x.agent_id).join(" / ");
    $("#activation-note").textContent =
      (result.agent_note || result.note || "") + " " + counts +
      (last ? " · Recent: " + last : "");
    renderAttention(result);
    if (start) await Promise.all([refreshStatus(), refreshHandoffs()]);
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

$("#ohayo").addEventListener("click", () => activateOhayo({start: true}));

$("#show-all-tickers").addEventListener("click", function() {
  hiddenTickers.clear();
  saveTickerChoices();
  renderTickers();
});
$("#hide-all-tickers").addEventListener("click", function() {
  hiddenTickers.add("*");
  saveTickerChoices();
  renderTickers();
});

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
