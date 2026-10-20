"use strict";
// No eval, no injected markup, no localStorage, no third-party requests.
// The real monotonic A/B presence driver and finite graph live in Python.
(() => {
  let session = null;
  let busy = false;
  const byId = id => document.getElementById(id);
  const consent = byId("consent");
  const experience = byId("experience");
  const status = byId("status");
  const input = byId("message");
  const along = byId("along");
  const side = byId("side");
  const erase = byId("erase");
  const trail = byId("trail");

  async function call(path, method = "GET", data = undefined) {
    const headers = {};
    if (session) headers["X-AB-Session"] = session;
    const options = {method, headers, credentials: "omit",
                     cache: "no-store", redirect: "error"};
    if (data !== undefined) {
      headers["Content-Type"] = "application/json";
      options.body = JSON.stringify(data);
    }
    const response = await fetch(path, options);
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "The branch was refused");
    return result;
  }

  function text(id, value) {
    byId(id).textContent = String(value);
  }

  function appendRecord(branch) {
    const li = document.createElement("li");
    const entered = document.createElement("div");
    entered.className = "entered";
    entered.textContent = "You submitted: " + branch.message;
    const shown = document.createElement("div");
    shown.className = "shown";
    shown.textContent = branch.branch_node + " / " + branch.form + " — " + branch.branch_words;
    li.append(entered, shown);
    trail.prepend(li);
  }

  async function observe() {
    if (!session || busy) return;
    try {
      const state = await call("/api/state");
      text("node", state.node);
      text("swing", (state.orientation > 0 ? "POSITIVE" : "NEGATIVE") +
                   " SWING  /  PRESENCE " + state.presence);
      text("along-node", state.along);
      text("side-node", state.side);
      byId("pulse").className = state.orientation > 0 ? "positive" : "negative";
    } catch (error) {
      status.textContent = error.message;
    }
  }

  async function enter() {
    if (busy || session) return;
    busy = true;
    try {
      const result = await call("/api/consent", "POST", {accepted: true});
      session = result.session;
      consent.classList.add("hidden");
      experience.classList.remove("hidden");
      status.textContent = "Session active · text stays on this local process";
      input.focus();
    } catch (error) {
      byId("agree").textContent = "Unable to enter: " + error.message;
    } finally {
      busy = false;
    }
    await observe();
  }

  async function submit(exitChoice) {
    if (!session || busy) return;
    const message = input.value;
    if (!message.trim()) return;
    busy = true;
    along.disabled = side.disabled = erase.disabled = true;
    try {
      const result = await call("/api/submit", "POST",
                                {message, exit_choice: exitChoice});
      const branch = result.branch;
      text("words", branch.branch_words);
      text("node", branch.branch_node);
      text("along-node", branch.exits[0]);
      text("side-node", branch.exits[1]);
      status.textContent = "Branch " + branch.branch_number + " · " +
                           branch.direction + " · presence " + branch.presence_movement;
      appendRecord(branch);
      input.value = "";
      input.focus();
    } catch (error) {
      status.textContent = error.message;
    } finally {
      busy = false;
      along.disabled = side.disabled = erase.disabled = false;
    }
    await observe();
  }

  async function eraseSession() {
    if (!session || busy) return;
    busy = true;
    try {
      await call("/api/erase", "POST", {});
      session = null;
      trail.replaceChildren();
      input.value = "";
      experience.classList.add("hidden");
      consent.classList.remove("hidden");
      byId("agree").textContent = "I agree · enter the fiction";
    } catch (error) {
      status.textContent = error.message;
    } finally {
      busy = false;
    }
  }

  byId("agree").addEventListener("click", enter);
  byId("message-form").addEventListener("submit", event => {
    event.preventDefault();
    void submit("along");
  });
  side.addEventListener("click", () => { void submit("side"); });
  erase.addEventListener("click", () => { void eraseSession(); });
  // Poll read-only observation; polling neither advances nor directs
  // the independently clocked native bipolar motion.
  window.setInterval(() => { void observe(); }, 650);
})();
