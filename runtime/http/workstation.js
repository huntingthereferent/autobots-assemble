"use strict";
// Read-only observer: no POST, arbitrary HTML insertion, local source execution or persisted UI state.
const $ = (selector) => document.querySelector(selector);
const POLL_MS = 15000;
let current = null;
let updating = false;

function el(tag, cls, value) {
  const item = document.createElement(tag);
  if (cls) item.className = cls;
  if (value !== undefined && value !== null) item.textContent = String(value);
  return item;
}
function status(status) {
  const value = String(status || "UNKNOWN");
  const style = value === "MATCHES_ADMISSION" || value === "AVAILABLE" || value === "COMPLETE" ? "good" :
    ["SOURCE_CHANGED", "UNREADABLE", "EDITION_UNREADABLE", "FAILED", "BLOCKED"].includes(value) ? "bad" :
    ["READY", "UNKNOWN", "ACTIVE", "EDITION_NOT_REGISTERED"].includes(value) ? "warn" : "";
  return el("span", "pill " + style, value.replaceAll("_", " "));
}
function put(selector, elements, empty) {
  $(selector).replaceChildren(...(elements.length ? elements : [el("p", "empty", empty)]));
}
function detail(label, content) {
  const node = el("details", "detail"), summary = el("summary", "", label), pre = el("pre", "", JSON.stringify(content, null, 2));
  node.append(summary, pre);
  return node;
}
function renderEd(edition) {
  const card = el("article", "entry"), head = el("div", "line");
  head.append(el("strong", "name", edition.worker_id + " / " + edition.version_id), status(edition.state));
  card.append(head, el("p", "meta", "From " + (edition.parent_version || "selected source")));
  if (edition.state === "AVAILABLE") {
    card.append(el("p", "code", "Current: " + edition.current_fingerprint));
    const mods = el("div", "sep");
    mods.append(el("span", "", "Files " + edition.file_count),
      el("span", "", "Modified " + edition.modified.length),
      el("span", "", "Added " + edition.added.length),
      el("span", "", "Deleted " + edition.deleted.length));
    card.append(mods);
    if (edition.source_modified) card.append(status("SOURCE_CHANGED"));
    if (edition.source_modified) card.append(detail("View changed filenames", {
      modified: edition.modified, added: edition.added, deleted: edition.deleted}));
  } else card.append(el("p", "meta", "Manifest/source inventory could not be read."));
  return card;
}
function inspectionPanel(report) {
  // Process-specific fields are data, not executable behavior.
  const panel = el("details", "detail inspection");
  panel.append(el("summary", "", "Inspect · " + report.title));
  panel.append(el("p", "minor", report.scope));
  for (const [label, rows] of [["Declared inputs", report.inputs], ["Recorded outputs", report.outputs]]) {
    const block = el("section", "inspect-section");
    block.append(el("h3", "", label));
    const list = el("dl", "inspect-grid");
    for (const row of rows) {
      list.append(el("dt", "", row.label), el("dd", "", row.value));
    }
    if (!rows.length) block.append(el("p", "minor", "No fields recorded."));
    else block.append(list);
    panel.append(block);
  }
  const notes = el("ul", "inspect-notes");
  for (const note of report.notes) notes.append(el("li", "", note));
  panel.append(notes);
  return panel;
}
function renderJob(job) {
  const card = el("article", "entry"), head = el("div", "line");
  head.append(el("strong", "name", job.title), status(job.status));
  card.append(head, el("p", "meta", job.worker_id + " / " + job.version_id),
    el("p", "minor", job.required_relation), el("p", "code", "Job " + job.job_id));
  const foot = el("div", "sep");
  foot.append(status(job.source_state), el("span", "", job.verification.replaceAll("-", " ")));
  card.append(foot);
  if (job.lane_refs.length) card.append(el("p", "minor", "Workspace lane: " + job.lane_refs.join(", ")));
  if (job.missing_witnesses.length) card.append(el("p", "minor", "Missing: " + job.missing_witnesses.join(", ")));
  if (job.inspection) card.append(inspectionPanel(job.inspection));
  card.append(detail("Result and evidence", {result: job.result, evidence: job.evidence, source_at_admission: job.edition_fingerprint}));
  card.append(detail("Recorded event trail", job.events));
  return card;
}
function renderLane(lane) {
  const card = el("article", "entry"), head = el("div", "line");
  head.append(el("strong", "name", lane.label), lane.focused ? status("FOCUSED") : el("span", "minor", "Return point"));
  card.append(head, el("p", "meta", lane.referent));
  if (lane.next_movement) card.append(el("p", "minor", "Next: " + lane.next_movement));
  if (lane.preserved) card.append(el("p", "minor", "Preserved: " + lane.preserved));
  card.append(el("p", "code", lane.return_event_id));
  return card;
}
function updateFilters(items) {
  const control = $("#filter-worker"), selected = control.value;
  const names = [...new Set(items)].filter(Boolean).sort();
  control.replaceChildren(el("option", "", "All processes"), ...names.map(name => {
    const option = el("option", "", name); option.value = name; return option;
  }));
  control.value = names.includes(selected) ? selected : "";
}
function render(data) {
  current = data;
  for (const [id, value] of Object.entries({workers:data.counts.workers, editions:data.counts.editions,
    jobs:data.counts.jobs, ready:data.counts.ready, complete:data.counts.recorded_complete})) {
    $("#count-" + id).textContent = String(value);
  }
  updateFilters([...data.editions.map(x => x.worker_id), ...data.jobs.map(x => x.worker_id)]);
  renderFiltered();
}
function renderFiltered() {
  if (!current) return;
  const worker = $("#filter-worker").value, choice = $("#filter-status").value;
  const editions = current.editions.filter(x => !worker || x.worker_id === worker);
  const jobs = current.jobs.filter(x => (!worker || x.worker_id === worker) && (!choice || x.status === choice));
  const lanes = current.workspace.lanes;
  put("#editions", editions.map(renderEd), "No local versions for this process.");
  put("#jobs", jobs.map(renderJob), "No admitted jobs match these filters. Copying a process does not create work.");
  put("#lanes", lanes.map(renderLane), "No saved lane journal. Project state remains in its original system.");
  $("#edition-label").textContent = editions.length + " editions";
  $("#job-label").textContent = jobs.length + " jobs";
  $("#lane-label").textContent = lanes.length + " lanes";
  $("#selection-note").textContent = (worker || choice) ? "Filtered local records" : "Showing recorded local state";
}
async function refresh() {
  if (updating) return;
  updating = true;
  try {
    const res = await fetch("/api/workstation", {cache:"no-store", credentials:"same-origin"});
    if (!res.ok) throw new Error("HTTP " + res.status);
    const data = await res.json();
    if (data.read_only !== true) throw new Error("server did not declare a read-only projection");
    render(data);
    $("#connection").className = "connection online";
    $("#connection").textContent = "Connected locally";
    $("#checked-at").textContent = "Read at " + new Date().toLocaleTimeString();
    $("#notice").hidden = true;
  } catch (error) {
    $("#connection").className = "connection offline";
    $("#connection").textContent = "Unavailable";
    $("#notice").textContent = "Could not read local workstation state. " + error.message + ". Any previous results are stale.";
    $("#notice").hidden = false;
  } finally {updating = false;}
}
$("#refresh").addEventListener("click", refresh);
$("#filter-worker").addEventListener("change", renderFiltered);
$("#filter-status").addEventListener("change", renderFiltered);
document.addEventListener("visibilitychange", () => {if (!document.hidden) refresh();});
setInterval(() => {if (!document.hidden) refresh();}, POLL_MS);
refresh();
