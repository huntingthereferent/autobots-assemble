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
  // Process-specific fields are provided as data by a registered native
  // inspector. This generic renderer never evaluates or interprets them.
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
  if (job.preferred_selection_event) card.append(el("p", "code", "Preferred selection used: " + job.preferred_selection_event));
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
  renderControls();
  renderPromotion();
  renderResearch();
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
const ID_PATTERN = /^[a-zA-Z0-9][a-zA-Z0-9_.-]{0,79}$/;
const FINITE = "finite-correspondence-process";
const INTEGRATED = "finite-correspondence-integrated";
const FACTORY = "factory-machine-simulation-process";
function option(value, label) {
  const item = el("option", "", label);
  item.value = value;
  return item;
}
function renderControls() {
  if (!current) return;
  const editionEl = $("#control-edition"), old = editionEl.value;
  const available = current.editions.filter(x => x.state === "AVAILABLE");
  editionEl.replaceChildren(option("", "Choose an edition"),
    ...available.map(x => option(x.worker_id + "/" + x.version_id, x.worker_id + " / " + x.version_id)));
  editionEl.value = available.some(x => x.worker_id + "/" + x.version_id === old) ? old : "";
  updateControlJobs();
}
function updateControlJobs() {
  if (!current) return;
  const selected = $("#control-edition").value, jobEl = $("#control-job"), oldJob = jobEl.value;
  const jobs = current.jobs.filter(x => x.worker_id + "/" + x.version_id === selected);
  jobEl.replaceChildren(option("", "Choose recorded job"),
    ...jobs.map(x => option(x.job_id, x.job_id + " · " + x.status)));
  jobEl.value = jobs.some(x => x.job_id === oldJob) ? oldJob : "";
  updateControlCommand();
}
function updateControlCommand() {
  const edition = $("#control-edition").value, action = $("#control-action").value;
  const parts = edition.split("/");
  const worker = parts[0], version = parts[1];
  const selected = current && current.editions.find(x => x.worker_id === worker && x.version_id === version);
  let note = "Select a worker edition.", commands = "No command selected.";
  const prefix = "python -m systems.workspace.controls --data-dir runtime/data ";
  $("#control-job").disabled = action !== "job";
  $("#control-new-job").disabled = action !== "prepare";
  if (selected && ID_PATTERN.test(worker) && ID_PATTERN.test(version)) {
    if (selected.source_modified) {
      note = "Selected edition changed from its source copy. Review its files before trusting execution.";
    } else note = "Commands are for the authorized local terminal, never sent by this page.";
    if (action === "prepare") {
      if (worker === FINITE) {
        const id = $("#control-new-job").value.trim();
        if (!ID_PATTERN.test(id)) {
          note = "Choose a simple job ID (letters, numbers, dots, dashes or underscore).";
          commands = "Invalid job ID.";
        } else {
          commands = prefix + "prepare --worker " + worker + " --version " + version + " --inputs-file runtime/data/finite-inputs.json\n" +
            prefix + "admit-finite --version " + version + " --inputs-file runtime/data/finite-inputs.json --job-id " + id +
            " --confirm-admit " + id + " --from-actor local-operator\n" +
            "# After admission, inspect this job and explicitly authorize execution below.";
        }
      } else if (worker === INTEGRATED) {
        const id = $("#control-new-job").value.trim();
        if (!ID_PATTERN.test(id)) {
          note = "Enter a simple job ID for this bounded CP30 signature check.";
          commands = "Invalid job ID.";
        } else {
          commands = prefix + "prepare --worker " + worker + " --version " + version +
            " --inputs-file runtime/data/cp30-attestation-input.json\n" +
            prefix + "admit-integrated --version " + version +
            " --inputs-file runtime/data/cp30-attestation-input.json --job-id " + id +
            " --confirm-admit " + id + " --from-actor local-operator\n" +
            "# Review supplied public key trust anchors. A signed claim is not real-world owner identity.";
        }
      } else {
        note = "Factory stages must originate in FactorySystem; use the recorded job operation.";
        commands = "No arbitrary Factory admission is available.";
      }
    } else {
      const jobId = $("#control-job").value;
      const job = current.jobs.find(x => x.job_id === jobId && x.worker_id === worker && x.version_id === version);
      if (!job || !ID_PATTERN.test(jobId)) {
        note = "Choose a recorded job for this exact edition.";
        commands = "No recorded job selected.";
      } else {
        commands = prefix + "inspect --job-id " + jobId + "\n" +
          (job.status === "COMPLETE" ? prefix + "reverify --job-id " + jobId :
            job.status === "READY" && job.source_state === "MATCHES_ADMISSION" ?
              prefix + "execute --job-id " + jobId + " --confirm-execute " + jobId :
              "# Job is not ready for execution; inspect its recorded wall first.");
        if (job.source_state !== "MATCHES_ADMISSION") note = "Source is not pinned to the visible edition; execution must not proceed.";
      }
    }
  }
  $("#control-note").textContent = note;
  $("#control-command").textContent = commands;
  $("#control-copy").disabled = !commands.startsWith(prefix);
}
$("#control-edition").addEventListener("change", updateControlJobs);
$("#control-action").addEventListener("change", updateControlCommand);
$("#control-job").addEventListener("change", updateControlCommand);
$("#control-new-job").addEventListener("input", updateControlCommand);
$("#control-copy").addEventListener("click", async () => {
  const command = $("#control-command").textContent;
  if (!command.startsWith("python -m systems.workspace.controls ")) return;
  try {
    await navigator.clipboard.writeText(command);
    $("#control-note").textContent = "Copied for local terminal review; no job was admitted or run.";
  } catch (_error) {
    $("#control-note").textContent = "Clipboard unavailable. Select the command text to copy manually.";
  }
});

function renderPromotion() {
  if (!current) return;
  const leftEl = $("#compare-left"), rightEl = $("#compare-right"), jobEl = $("#promote-job");
  const oldLeft = leftEl.value, oldRight = rightEl.value, oldJob = jobEl.value;
  const versions = current.editions.filter(x => x.state === "AVAILABLE");
  leftEl.replaceChildren(option("", "Choose first edition"), ...versions.map(x =>
    option(x.worker_id + "/" + x.version_id, x.worker_id + " / " + x.version_id)));
  leftEl.value = versions.some(x => x.worker_id + "/" + x.version_id === oldLeft) ? oldLeft : "";
  const worker = leftEl.value.split("/")[0];
  const eligible = versions.filter(x => x.worker_id === worker && x.worker_id + "/" + x.version_id !== leftEl.value);
  rightEl.replaceChildren(option("", "Choose second edition"), ...eligible.map(x => option(x.worker_id + "/" + x.version_id, x.version_id)));
  rightEl.value = eligible.some(x => x.worker_id + "/" + x.version_id === oldRight) ? oldRight : "";
  const jobs = current.jobs.filter(x => x.worker_id + "/" + x.version_id === leftEl.value && x.status === "COMPLETE" && x.source_state === "MATCHES_ADMISSION");
  jobEl.replaceChildren(option("", "Choose supporting job"), ...jobs.map(x => option(x.job_id, x.job_id)));
  jobEl.value = jobs.some(x => x.job_id === oldJob) ? oldJob : "";
  const left = versions.find(x => x.worker_id + "/" + x.version_id === leftEl.value);
  const right = versions.find(x => x.worker_id + "/" + x.version_id === rightEl.value);
  const job = jobs.find(x => x.job_id === jobEl.value);
  const prefix = "python -m systems.workspace.controls --data-dir runtime/data ";
  const commands = [];
  if (left && right) commands.push(prefix + "compare --worker " + left.worker_id + " --left-version " + left.version_id + " --right-version " + right.version_id);
  if (left && job && left.worker_id !== INTEGRATED) commands.push(prefix + "reverify --job-id " + job.job_id + "\n" +
    prefix + "promote --worker " + left.worker_id + " --version " + left.version_id +
    " --supporting-job " + job.job_id + " --confirm-version " + left.version_id +
    " --confirm-fingerprint " + left.current_fingerprint + " --actor local-operator");
  $("#promotion-command").textContent = commands.join("\n") || "Select two editions to compare or a completed job for selection.";
  $("#promotion-copy").disabled = !commands.length;
  $("#promotion-note").textContent = job && left && left.worker_id === INTEGRATED ? "CP30 signature checks do not establish general integrated-route capability for promotion."
    : job ? "Native re-verification happens in the local CLI; recorded COMPLETE alone is insufficient."
    : left ? "Select a second edition for comparison or a completed job for evidence-gated selection."
    : "Select an edition to start.";
  const items = (current.preferred || []).map(x => {
    const item = el("article", "entry");
    const line = el("div", "line");
    line.append(el("strong", "name", x.worker_id + " / " + x.version_id), status(x.source_state));
    item.append(line, el("p", "minor", "Supported by job " + x.supporting_job_id + " · " + x.required_relation),
                el("p", "minor", "One native-reverified job; not deployment or proof of other capabilities."));
    return item;
  });
  put("#preferred-editions", items, "No preferred editions have been explicitly selected.");
  renderNextPreferred();
}
function renderNextPreferred() {
  if (!current) return;
  const selected = (current.preferred || []).filter(x => x.source_state === "MATCHES_SELECTION");
  const jobId = $("#preferred-new-job").value.trim();
  const prefix = "python -m systems.workspace.controls --data-dir runtime/data ";
  const finite = selected.find(x => x.worker_id === FINITE);
  const factory = selected.find(x => x.worker_id === FACTORY);
  const cmds = [];
  const notes = [];
  if (finite) {
    cmds.push(prefix + "prepare-preferred --worker " + FINITE + " --inputs-file runtime/data/finite-inputs.json");
    if (ID_PATTERN.test(jobId)) {
      cmds.push(prefix + "admit-preferred-finite --inputs-file runtime/data/finite-inputs.json --job-id " + jobId +
        " --confirm-admit " + jobId + " --confirm-selection " + finite.event_id + " --from-actor local-operator");
      notes.push("Finite: job admission creates READY, not an executed result.");
    } else notes.push("Finite: enter a valid new job ID to prepare an exact admission command.");
  }
  if (factory) {
    cmds.push(prefix + "prepare-preferred --worker " + FACTORY);
    notes.push("Factory: the pending machine-stage ID must come from FactorySystem before admission; no order is invented here.");
  }
  if ((current.preferred || []).some(x => x.source_state !== "MATCHES_SELECTION")) {
    notes.push("A stale or unavailable selection cannot be used to admit future work.");
  }
  $("#preferred-new-command").textContent = cmds.join("\n") || "No current verified-source selection available.";
  $("#preferred-new-note").textContent = notes.join(" ") || "Select an edition with a completed, reverified supporting job first.";
  $("#preferred-new-copy").disabled = !cmds.length;
}
$("#preferred-new-job").addEventListener("input", renderNextPreferred);
$("#preferred-new-copy").addEventListener("click", async () => {
  const value = $("#preferred-new-command").textContent;
  if (!value.startsWith("python -m systems.workspace.controls ")) return;
  try { await navigator.clipboard.writeText(value);
    $("#preferred-new-note").textContent = "Copied for local review. No new job was admitted or executed.";
  } catch (_error) {
    $("#preferred-new-note").textContent = "Clipboard unavailable; select the text manually.";
  }
});
$("#compare-left").addEventListener("change", renderPromotion);
$("#compare-right").addEventListener("change", renderPromotion);
$("#promote-job").addEventListener("change", renderPromotion);
$("#promotion-copy").addEventListener("click", async () => {
  const value = $("#promotion-command").textContent;
  if (!value.startsWith("python -m systems.workspace.controls ")) return;
  try { await navigator.clipboard.writeText(value);
        $("#promotion-note").textContent = "Copied for local review. No edition was selected or executed.";
  } catch (_error) { $("#promotion-note").textContent = "Copy unavailable; select the commands manually."; }
});

// Research is a source-owned READ-ONLY projection. No research file is a job.
let researchShown = 80;
function researchLink(path, label, line) {
  const safe = /^[a-zA-Z0-9._/-]{1,260}$/.test(path) && !path.includes("..");
  const item = el(safe ? "a" : "span", "code", label || path);
  if (safe) {
    item.href = "https://github.com/huntingthereferent/autobots-assemble/blob/main/" + path.split("/").map(encodeURIComponent).join("/") + (Number.isInteger(line) && line > 0 ? "#L" + line : "");
    item.target = "_blank";
    item.rel = "noopener noreferrer";
  }
  return item;
}
function renderResearch() {
  if (!current || !current.research) return;
  const research = current.research;
  if (research.schema !== "workstation-research-continuity/v1") {
    $("#research-record-list").replaceChildren(el("p","empty","Unknown research source version"));
    return;
  }
  const totals = research.totals;
  for (const [key, value] of Object.entries({
      sources:totals.source_files, records:totals.structured_records,
      moves:totals.explicit_move_states, walls:totals.explicit_wall_entries})) {
    $("#research-" + key).textContent = String(value);
  }
  const select = $("#research-section"), selected=select.value;
  select.replaceChildren(option("", "All research systems"),
    ...research.sections.map(x=>option(x.name, x.name+" ("+x.source_count+")")));
  select.value = research.sections.some(x=>x.name===selected) ? selected : "";
  const active=select.value, mode=$("#research-view").value;
  let entries=[];
  if (mode==="all_moves_walls") {
    // Display only originally recorded evidence. Titles/labels are not new events.
    entries=[
      ...research.documented_marks.filter(x=>!active||x.section===active),
      ...research.source_records.filter(x=>!active||x.section===active)
        .flatMap(x=>[
          ...(["MOVE","MOVE_WITH_WALL"].includes(x.state) ? [{...x,source_marker:"STRUCTURED_MOVEMENT"}] : []),
          ...x.walls.map((statement,index)=>({...x,source_marker:"STRUCTURED_WALL",statement,index}))
        ])
    ].sort((a,b)=>a.path.localeCompare(b.path)||((a.line||0)-(b.line||0)));
  } else if (mode==="inventory") {
    entries=research.sections.filter(x=>!active||x.name===active)
      .flatMap(x=>x.paths.map(path=>({path,section:x.name})));
  } else if (mode==="documented_walls" || mode==="documented_moves") {
    const kind = mode==="documented_walls" ? "DOCUMENTED_WALL" : "DOCUMENTED_MOVEMENT";
    entries=research.documented_marks.filter(x=>(!active||x.section===active) && x.kind===kind);
  } else if (mode==="walls") {
    entries=research.source_records.filter(x=>!active||x.section===active)
      .flatMap(x=>x.walls.map((statement,i)=>({...x,statement,index:i})));
  } else {
    entries=research.source_records.filter(x=>!active||x.section===active);
  }
  const shown=entries.slice(0,researchShown);
  const nodes=shown.map(row=>{
    const card=el("article","entry research-entry");
    if (mode==="inventory") {
      card.append(researchLink(row.path),el("p","meta",row.section+" · indexed source only"));
      return card;
    }
    if (mode==="documented_walls" || mode==="documented_moves" ||
        (mode==="all_moves_walls" && row.heading)) {
      card.append(el("strong","name",row.heading),
        el("p","meta",row.section+" · documented source heading, not native verification"),
        researchLink(row.path,row.path+" · line "+row.line,row.line));
      return card;
    }
    const head=el("div","line");
    head.append(el("strong","name",row.title),status(row.state));
    card.append(head,el("p","meta",row.kind+" · "+row.section),researchLink(row.path));
    if (mode==="walls" || (mode==="all_moves_walls" && row.source_marker==="STRUCTURED_WALL"))
      card.append(el("p","research-wall",row.statement));
    else {
      if (row.walls.length) card.append(el("p","minor",row.walls.length+" source-recorded unresolved conditions"));
      if (row.boundary) card.append(el("p","minor","Boundary: "+row.boundary));
      if (row.next) card.append(el("p","minor","Next recorded movement: "+row.next));
      card.append(el("p","minor",row.scope));
      if (row.walls.length) card.append(detail("Read original walls",row.walls));
    }
    return card;
  });
  if (entries.length>researchShown) {
    const more=el("button","research-more","Show more source records ("+(entries.length-researchShown)+" remaining)");
    more.type="button";
    more.addEventListener("click",()=>{researchShown+=80;renderResearch();});
    nodes.push(more);
  }
  put("#research-record-list",nodes,"No records of this kind in the selected source. Not the same as no research.");
  $("#research-label").textContent=research.sections.length+" original source areas";
  $("#research-note").textContent=shown.length+" of "+entries.length+" source entries · "+mode;
}
$("#research-section").addEventListener("change",()=>{researchShown=80;renderResearch();});
$("#research-view").addEventListener("change",()=>{researchShown=80;renderResearch();});

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
