"use strict";
const $ = (selector) => document.querySelector(selector);
const POLL_MS = 10000;
let lastPollStarted = false;
let lastSuccess = 0;

function node(tag, className, value) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (value !== undefined && value !== null) element.textContent = String(value);
  return element;
}
function dateLabel(raw) {
  if (!raw) return "No recorded movement";
  const value = new Date(raw);
  return Number.isNaN(value.getTime()) ? String(raw) : value.toLocaleString();
}
function labelStatus(value) {
  return String(value || "UNKNOWN").replaceAll("_", " ");
}
function statusPill(status) {
  const value = String(status || "").toUpperCase();
  const className = ["BLOCKED", "FAILED", "UNKNOWN", "PARTIAL"].includes(value) ? "warn"
    : value === "ACTIVE" ? "live"
    : ["READY", "WAITING", "COMPLETE"].includes(value) ? "neutral" : "";
  return node("span", "pill " + className, value);
}
function replaceItems(selector, items, emptyMessage) {
  const target = $(selector);
  target.replaceChildren(...(items.length ? items : [node("p", "empty", emptyMessage)]));
}
function renderAgents(agents) {
  const rows = agents.map(agent => {
    const entry = node("article", "entry");
    const main = node("div", "entry-main");
    main.append(node("span", "entry-name", agent.referent), statusPill(agent.status));
    const meta = node("p", "entry-meta",
      "Generation " + agent.generation + " · " + agent.birth_reason.replaceAll("_", " "));
    const foot = node("div", "entry-foot");
    foot.append(node("span", "", "Loop " + agent.loop_status),
      node("span", "", "Last event: " + (agent.last_event_type || "none")),
      node("span", "", dateLabel(agent.last_event_at)));
    entry.append(main, meta, foot);
    return entry;
  });
  replaceItems("#agents", rows, "No recorded agents.");
  $("#agent-count").textContent = agents.length + " recorded";
}
function renderTasks(tasks) {
  const rows = tasks.map(task => {
    const entry = node("article", "entry");
    const main = node("div", "entry-main");
    main.append(node("span", "entry-name", task.title), statusPill(task.status));
    entry.append(main,
      node("p", "entry-meta", task.source + " · " + task.referent),
      node("div", "entry-foot", "Native source: " + (task.source_ref || "not supplied")));
    return entry;
  });
  replaceItems("#tasks", rows, "No admitted tasks.");
  $("#task-count").textContent = tasks.length + " recorded";
}
function renderEvents(events) {
  const rows = events.map(event => {
    const line = node("li");
    line.append(
      node("strong", "", event.event_type.replaceAll("_", " ") +
        (event.status ? " · " + event.status : "")),
      node("p", "", event.subject.toUpperCase() + " · " + event.label),
      node("span", "time", dateLabel(event.at))
    );
    if (event.evidence_refs.length) {
      line.append(node("p", "", "Witness: " + event.evidence_refs.join(", ")));
    }
    return line;
  });
  const target = $("#events");
  target.replaceChildren(...(rows.length ? rows : [node("li", "empty", "No events recorded.")]));
}
function connectionRow(label, text, connected) {
  const row = node("div", "connection-row");
  row.append(node("span", "", label), node("strong", connected ? "on" : "off", text));
  return row;
}
function renderConnections(connections) {
  const r = connections.repository_work, a = connections.agents,
    h = connections.handoff_runtime, s = connections.systems;
  const rows = [
    connectionRow("Repository task source", r.available ? "Connected · " + r.eligible_active_rows + " entries" : "Not connected", r.available),
    connectionRow("Durable event journal", h.durable ? "Connected" : "Not durable", h.durable),
    connectionRow("A/B evaluator", a.ab_evaluator_connected ? "Registered" : "Not registered", a.ab_evaluator_connected),
    connectionRow("Closure verifier", a.closure_admitter_connected ? "Registered" : "Not registered", a.closure_admitter_connected),
    connectionRow("Autonomous worker", a.autonomous_worker_running ? "Reported running" : "Not running", a.autonomous_worker_running),
    connectionRow("Online School input", s.online_school_registered ? "Registered" : "Not registered", s.online_school_registered),
    connectionRow("Factory input", s.factory_registered ? "Registered" : "Not registered", s.factory_registered)
  ];
  $("#connections").replaceChildren(...rows);
}
function render(snapshot) {
  const c = snapshot.counts;
  const mode = snapshot.monitor.mode.replaceAll("_", " ");
  $("#mode-title").textContent = mode.charAt(0).toUpperCase() + mode.slice(1);
  $("#mode-detail").textContent = snapshot.monitor.detail;
  $("#n-agents").textContent = c.agents_total;
  $("#n-active").textContent = c.agents_active_recorded;
  $("#n-ready").textContent = c.agents_ready;
  $("#n-tasks").textContent = c.tasks_open;
  $("#n-tasks-sub").textContent = c.tasks_total + " admitted task records";
  $("#n-closed").textContent = c.loops_closed;
  $("#n-unresolved").textContent = c.agents_unresolved;
  $("#last-event").textContent = dateLabel(snapshot.last_event_at);
  renderAgents(snapshot.agents);
  renderTasks(snapshot.tasks);
  renderEvents(snapshot.events);
  renderConnections(snapshot.connections);
}
async function refreshMonitor() {
  if (lastPollStarted) return;
  lastPollStarted = true;
  $("#connection").textContent = "Checking…";
  try {
    const response = await fetch("/api/monitor?actor=james", {cache: "no-store"});
    if (!response.ok) throw new Error("Runtime returned HTTP " + response.status);
    const snapshot = await response.json();
    if (!snapshot.read_only) throw new Error("Expected a read-only monitor response");
    render(snapshot);
    lastSuccess = Date.now();
    $("#connection").className = "connection online";
    $("#connection").textContent = "Runtime responding";
    $("#checked-at").textContent = "Checked " + dateLabel(snapshot.generated_at);
    $("#offline-notice").hidden = true;
  } catch (error) {
    $("#connection").className = "connection offline";
    $("#connection").textContent = "Connection lost";
    $("#offline-notice").textContent = "Unable to read Continuity. Showing the last successful snapshot" +
      (lastSuccess ? " from " + dateLabel(new Date(lastSuccess).toISOString()) : " (none yet)") +
      ". " + error.message;
    $("#offline-notice").hidden = false;
  } finally {
    lastPollStarted = false;
  }
}
$("#refresh").addEventListener("click", refreshMonitor);
document.addEventListener("visibilitychange", () => {
  if (!document.hidden) refreshMonitor();
});
setInterval(() => {
  if (!document.hidden) refreshMonitor();
}, POLL_MS);
refreshMonitor();
