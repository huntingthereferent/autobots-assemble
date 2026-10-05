import { calculateHealth, fallbackInsight } from "./logic.mjs";

const form = document.querySelector("#health-form");
const steps = [...document.querySelectorAll(".step")];
const progress = document.querySelector("#progress");
const dashboard = document.querySelector("#dashboard");
const formPanel = document.querySelector("#form-panel");
const backButton = document.querySelector("#back");
const nextButton = document.querySelector("#next");
const resetButton = document.querySelector("#reset");
const insightText = document.querySelector("#insight-text");
const insightSource = document.querySelector("#insight-source");

let currentStep = 0;

function money(value) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);
}

function decimalMoney(value) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
}

function showStep(index) {
  currentStep = index;
  steps.forEach((step, i) => step.hidden = i !== currentStep);
  progress.textContent = `Step ${currentStep + 1} of ${steps.length}`;
  backButton.hidden = currentStep === 0;
  nextButton.textContent = currentStep === steps.length - 1 ? "See my business health" : "Continue";
}

function validateCurrentStep() {
  const inputs = [...steps[currentStep].querySelectorAll("input")];
  for (const input of inputs) {
    if (!input.reportValidity()) return false;
  }
  return true;
}

function formData() {
  const data = new FormData(form);
  return Object.fromEntries(data.entries());
}

function setText(id, value) {
  document.querySelector(id).textContent = value;
}

function renderDashboard(result) {
  const statusLabel = result.status === "green"
    ? "Healthy"
    : result.status === "yellow"
      ? "Close"
      : "Needs attention";

  const status = document.querySelector("#status");
  status.dataset.status = result.status;
  setText("#status-label", statusLabel);
  setText("#profit", money(result.monthlyProfit));
  setText("#revenue", money(result.revenue));
  setText("#break-even", `${result.breakEvenUnits} units / month`);
  setText("#contribution", decimalMoney(result.contributionPerUnit));

  if (result.unitsToBreakEven === 0) {
    setText("#headline-number", "You are above monthly break-even");
    setText("#headline-detail", `Current monthly profit: ${money(result.monthlyProfit)}.`);
  } else {
    setText("#headline-number", `Sell ${result.unitsToBreakEven} more unit${result.unitsToBreakEven === 1 ? "" : "s"}`);
    setText("#headline-detail", "at the current price and cost to reach monthly break-even.");
  }

  setText("#payback",
    result.paybackMonths === null
      ? "Not yet"
      : result.paybackMonths < 0.1
        ? "< 1 month"
        : `${result.paybackMonths.toFixed(1)} months`
  );

  insightText.textContent = fallbackInsight(result);
  insightSource.textContent = "Local rule-based insight";
  loadAiInsight(result);

  formPanel.hidden = true;
  dashboard.hidden = false;
  window.scrollTo({ top: 0, behavior: "smooth" });
}

async function loadAiInsight(result) {
  try {
    const response = await fetch("/api/insight", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(result),
    });

    if (!response.ok) return;
    const payload = await response.json();
    if (payload.insight) {
      insightText.textContent = payload.insight;
      insightSource.textContent = payload.source === "openai"
        ? "AI suggestion"
        : "Local suggestion";
    }
  } catch {
    // The deterministic suggestion remains visible if the API is unavailable.
  }
}

nextButton.addEventListener("click", () => {
  if (!validateCurrentStep()) return;

  if (currentStep < steps.length - 1) {
    showStep(currentStep + 1);
    return;
  }

  try {
    renderDashboard(calculateHealth(formData()));
  } catch (error) {
    const message = document.querySelector("#form-error");
    message.textContent = error.message;
    message.hidden = false;
  }
});

backButton.addEventListener("click", () => {
  document.querySelector("#form-error").hidden = true;
  if (currentStep > 0) showStep(currentStep - 1);
});

resetButton.addEventListener("click", () => {
  form.reset();
  dashboard.hidden = true;
  formPanel.hidden = false;
  document.querySelector("#form-error").hidden = true;
  showStep(0);
  window.scrollTo({ top: 0, behavior: "smooth" });
});

showStep(0);