"use strict";

const el = (id) => document.getElementById(id);
const lanes = {
  REVIEW: "review",
  ANSWERED: "answered",
  PARTIAL: "partial",
  UNKNOWN: "partial",
  OPEN: "open",
};
let knownCheckpoints = [];
let boardRequestSerial = 0;

function textNode(tag, value, className = "") {
  const node = document.createElement(tag);
  node.textContent = value;
  if (className) node.className = className;
  return node;
}

function addLink(holder, label, url) {
  if (!url) return;
  try {
    const checked = new URL(url);
    if (checked.protocol !== "https:") return;
  } catch (_) { return; }
  const link = textNode("a", label);
  link.href = url;
  link.rel = "noopener noreferrer";
  link.target = "_blank";
  holder.appendChild(link);
}

function questionCard(q) {
  const card = document.createElement("article");
  card.className = "research-question";
  card.appendChild(textNode("span", q.id, "research-question-id"));
  card.appendChild(textNode("h3", q.question));
  card.appendChild(textNode("span", q.status, "state"));
  const parts = [
    ["Answer", q.answer], ["Scope", q.scope], ["Remaining boundary", q.boundary],
  ];
  parts.forEach(function([label, value]) {
    if (!value) return;
    const para = document.createElement("p");
    para.appendChild(textNode("strong", label + ": ", "detail-label"));
    para.appendChild(document.createTextNode(value));
    card.appendChild(para);
  });
  const ancestry = [];
  if ((q.derived_from || []).length) ancestry.push("From " + q.derived_from.join(", "));
  if ((q.next_question_ids || []).length) ancestry.push("Leads to " + q.next_question_ids.join(", "));
  if (ancestry.length) card.appendChild(textNode("p", ancestry.join(" · "), "research-lineage"));
  const references = document.createElement("div");
  references.className = "research-refs";
  addLink(references, "Original question ↗", q.origin);
  (q.witnesses || []).forEach(w => addLink(references, w.label + " ↗", w.url));
  if (references.childElementCount) card.appendChild(references);
  return card;
}

// Each status lane is a vertically moving, seamless repeat of its actual
// research questions. The second cycle is decorative only: never an extra
// question, focus stop, announcement, or research record.
const laneNames = ["review", "answered", "partial", "open"];
let laneObservers = [];
let motionPaused = false;
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

function syncMotionButton() {
  const button = el("research-motion-toggle");
  button.disabled = reducedMotion.matches;
  button.setAttribute("aria-pressed", String(motionPaused));
  button.textContent = reducedMotion.matches
    ? "Scrolling off (system setting)"
    : (motionPaused ? "Resume scrolling" : "Pause scrolling");
  el("research-columns").classList.toggle("is-motion-paused", motionPaused);
  document.querySelector(".research-board-page").classList.toggle("is-motion-paused", motionPaused);
}

function clearLanes() {
  laneObservers.forEach(observer => observer.disconnect());
  laneObservers = [];
  laneNames.forEach(lane => {
    const track = el("research-" + lane + "-list");
    track.classList.remove("is-looping");
    track.replaceChildren();
    track.style.removeProperty("--research-loop-duration");
    el("research-" + lane + "-count").textContent = "0";
  });
}

function renderVerticalList(lane, questions) {
  const track = el("research-" + lane + "-list");
  const count = questions.length;
  el("research-" + lane + "-count").textContent = String(count);

  if (!count) {
    track.appendChild(textNode("p", "No questions in this state for the selected checkpoint.", "research-empty"));
    return;
  }

  const original = document.createElement("div");
  original.className = "research-question-cycle";
  questions.forEach(q => original.appendChild(questionCard(q)));
  track.appendChild(original);

  // Same cards, repeated only for smooth motion. The duplicate cannot
  // receive keyboard focus and does not change the source record or totals.
  const repeated = original.cloneNode(true);
  repeated.setAttribute("aria-hidden", "true");
  repeated.setAttribute("inert", "");
  repeated.inert = true;
  repeated.querySelectorAll("a, button, [tabindex]").forEach(node => {
    node.setAttribute("tabindex", "-1");
  });
  track.appendChild(repeated);

  const updateDuration = () => {
    const distance = original.getBoundingClientRect().height;
    if (distance > 0) {
      // Consistent slow upward movement, independent of list length.
      track.style.setProperty("--research-loop-duration",
        Math.max(24, Math.round(distance / 23)) + "s");
    }
  };
  updateDuration();
  if (typeof ResizeObserver !== "undefined") {
    const observer = new ResizeObserver(updateDuration);
    observer.observe(original);
    laneObservers.push(observer);
  }
  track.classList.add("is-looping");
}

function renderBoard(data) {
  const choice = el("research-checkpoint");
  knownCheckpoints = data.checkpoints || [];
  choice.replaceChildren(...knownCheckpoints.map(x => {
    const option = document.createElement("option");
    option.value = x.id;
    option.textContent = x.label;
    return option;
  }));
  choice.value = data.checkpoint?.id || "";
  el("research-note").textContent = data.checkpoint?.note || "";
  el("research-freeze-date").textContent = data.checkpoint?.frozen_date || "";
  clearLanes();
  const byLane = {review:[],answered:[],partial:[],open:[]};
  (data.questions || []).forEach(q => {
    const lane = lanes[q.status];
    if (lane) byLane[lane].push(q);
  });
  laneNames.forEach(lane => renderVerticalList(lane, byLane[lane]));
}

async function loadBoard(checkpoint = "") {
  const serial = ++boardRequestSerial;
  const error = el("research-error");
  error.hidden = true;
  try {
    const path = "/api/research-board" + (checkpoint ? "?checkpoint=" + encodeURIComponent(checkpoint) : "");
    const response = await fetch(path, {cache:"no-store"});
    const data = await response.json();
    if (serial !== boardRequestSerial) return;
    if (!response.ok || data.available === false) throw new Error(data.error || data.reason || "Board source unavailable");
    renderBoard(data);
  } catch (err) {
    if (serial !== boardRequestSerial) return;
    error.textContent = err.message || String(err);
    error.hidden = false;
    // Never retain stale cards from an older checkpoint after an error.
    clearLanes();
  }
}

el("research-checkpoint").addEventListener("change", function(event) {
  const selected = event.target.value;
  if (!knownCheckpoints.some(x => x.id === selected)) return;
  const url = new URL(window.location);
  url.searchParams.set("checkpoint", selected);
  history.replaceState(null, "", url.pathname + url.search);
  loadBoard(selected);
});
el("research-motion-toggle").addEventListener("click", function() {
  motionPaused = !motionPaused;
  syncMotionButton();
});
if (reducedMotion.addEventListener) {
  reducedMotion.addEventListener("change", syncMotionButton);
}
syncMotionButton();
const requested = new URLSearchParams(window.location.search).get("checkpoint") || "";
loadBoard(requested);
