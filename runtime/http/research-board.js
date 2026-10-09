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
  ["review", "answered", "partial", "open"].forEach(lane => {
    el("research-" + lane + "-list").replaceChildren();
    el("research-" + lane + "-count").textContent = "0";
  });
  const counts = {review:0,answered:0,partial:0,open:0};
  (data.questions || []).forEach(q => {
    const lane = lanes[q.status];
    if (!lane) return;
    el("research-" + lane + "-list").appendChild(questionCard(q));
    counts[lane] += 1;
  });
  for (const [lane,count] of Object.entries(counts)) {
    el("research-" + lane + "-count").textContent = String(count);
  }
}

async function loadBoard(checkpoint = "") {
  const error = el("research-error");
  error.hidden = true;
  try {
    const path = "/api/research-board" + (checkpoint ? "?checkpoint=" + encodeURIComponent(checkpoint) : "");
    const response = await fetch(path, {cache:"no-store"});
    const data = await response.json();
    if (!response.ok || data.available === false) throw new Error(data.error || data.reason || "Board source unavailable");
    renderBoard(data);
  } catch (err) {
    error.textContent = err.message || String(err);
    error.hidden = false;
    // Never retain stale cards from an older checkpoint after an error.
    ["review","answered","partial","open"].forEach(lane => {
      el("research-" + lane + "-list").replaceChildren();
      el("research-" + lane + "-count").textContent = "0";
    });
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
const requested = new URLSearchParams(window.location.search).get("checkpoint") || "";
loadBoard(requested);
