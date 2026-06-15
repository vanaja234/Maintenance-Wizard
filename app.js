const state = {
  equipment: [],
  samples: [],
  selectedEquipment: "",
  query: "Main drive motor has high vibration, rising temperature, bearing noise, and lubrication pressure is low.",
  sensors: {},
  result: null,
  stale: false,
  loading: false,
  activeView: "diagnosis",
  selectedSampleIndex: "",
};

const app = document.querySelector("#app");

function riskTone(level = "waiting") {
  return {
    low: "ok",
    medium: "warn",
    high: "high",
    critical: "danger",
    waiting: "muted",
  }[level] || "muted";
}

function html(strings, ...values) {
  return strings.map((part, index) => part + (values[index] ?? "")).join("");
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function currentEquipment() {
  return state.equipment.find((item) => item.id === state.selectedEquipment) || state.equipment[0];
}

function normalizeResult(result) {
  if (!result || result.error) return result;
  const risk = result.risk || { score: 0, level: "waiting", estimated_rul_hours: 0 };
  const fallbackProbability = Math.min(0.97, Math.max(0.03, (Number(risk.score || 0) + 10) / 125));
  return {
    ...result,
    prediction: result.prediction || {
      rul_hours: risk.estimated_rul_hours || 0,
      failure_probability: fallbackProbability,
      failure_window: risk.level === "critical" ? "next shift to 24 hours" : risk.level === "high" ? "24 to 72 hours" : risk.level === "medium" ? "3 to 7 days" : "no immediate failure window",
      degradation_trend: risk.level === "critical" ? "rapid degradation" : risk.level === "high" ? "accelerating degradation" : risk.level === "medium" ? "watchlist" : "stable",
      model_used: "Explainable hybrid scoring model",
      production_upgrade: "Upgrade with Isolation Forest/LSTM Autoencoder and XGBoost/Survival RUL models when plant history is available.",
      features: ["equipment criticality", "sensor deviation severity", "diagnosis confidence"],
    },
    business_impact: result.business_impact || {
      estimated_downtime_hours_avoided: risk.level === "critical" ? 24 : risk.level === "high" ? 14 : risk.level === "medium" ? 6 : 0,
      response_time_reduction_pct: risk.level === "critical" ? 70 : risk.level === "high" ? 55 : risk.level === "medium" ? 35 : 15,
      spare_actions_required: result.recommendations?.procurement_strategy?.length || 0,
      value_statement: "Earlier fault triage and spare-aware maintenance planning reduce downtime and decision delay.",
    },
  };
}

function optionList(rows, selected, labeler) {
  return rows
    .map((row, index) => {
      const value = row.id ?? index;
      const label = labeler(row, index);
      return `<option value="${escapeHtml(value)}" ${String(value) === String(selected) ? "selected" : ""}>${escapeHtml(label)}</option>`;
    })
    .join("");
}

function list(items, fallback) {
  const rows = items && items.length ? items : [fallback];
  return rows.map((item) => `<li>${escapeHtml(item)}</li>`).join("");
}

function metric(label, value, tone = "") {
  return html`
    <div class="metric-card ${tone}">
      <span>${label}</span>
      <strong>${value}</strong>
    </div>
  `;
}

function renderShell() {
  const result = state.result;
  const risk = result?.risk?.level || "waiting";
  const score = result?.risk?.score ?? 0;
  const eq = currentEquipment();
  const prediction = result?.prediction;
  const impact = result?.business_impact;

  app.innerHTML = html`
    <main class="app-shell">
      <aside class="rail">
        <div class="brand">
          <div class="brand-mark">MW</div>
          <div>
            <strong>Maintenance Wizard</strong>
            <span>Agentic AI for Steel Ops</span>
          </div>
        </div>
        <button class="nav-btn ${state.activeView === "diagnosis" ? "active" : ""}" data-view="diagnosis">Diagnosis</button>
        <button class="nav-btn ${state.activeView === "agents" ? "active" : ""}" data-view="agents">Agent Workflow</button>
        <button class="nav-btn ${state.activeView === "prediction" ? "active" : ""}" data-view="prediction">Prediction</button>
        <button class="nav-btn ${state.activeView === "report" ? "active" : ""}" data-view="report">Report</button>
        <div class="rail-card">
          <span>Hackathon fit</span>
          <strong>RAG + Agents + RUL + Alerts</strong>
          <p>Designed around Tata Steel's maintenance wizard problem statement.</p>
        </div>
      </aside>

      <section class="main">
        <header class="hero">
          <div>
            <p class="eyebrow">Tata Steel AI Hackathon 2026 | Round 2</p>
            <h1>Agentic Maintenance Intelligence Dashboard</h1>
            <p class="hero-copy">A decision-support prototype for faster diagnosis, root cause analysis, predictive maintenance, spare planning, and traceable supervisor reporting.</p>
          </div>
          <div class="live-chip"><span></span>Local prototype running</div>
        </header>

        <section class="kpi-grid">
          ${metric("Equipment covered", state.equipment.length || "-", "teal")}
          ${metric("Sample scenarios", state.samples.length || "-", "blue")}
          ${metric("Agent workflow", "7 agents", "violet")}
          ${metric("Current risk", risk.toUpperCase(), riskTone(risk))}
        </section>

        <section class="workspace-grid">
          ${renderInputPanel(eq)}
          ${renderDecisionPanel(result, risk, score)}
        </section>

        ${renderView(result, prediction, impact)}
      </section>
    </main>
  `;

  bindEvents();
}

function renderInputPanel(eq) {
  const sensorFields = Object.keys(eq?.normal_ranges || {})
    .map((signal) => {
      const [low, high] = eq.normal_ranges[signal];
      return html`
        <label class="sensor-field">
          <span>${signal}</span>
          <input data-sensor="${signal}" type="number" step="0.1" value="${state.sensors[signal] ?? ""}" />
          <small>Normal ${low} - ${high}</small>
        </label>
      `;
    })
    .join("");

  return html`
    <section class="panel input-panel">
      <div class="panel-head">
        <div>
          <span class="panel-kicker">Engineer input</span>
          <h2>Fault Context</h2>
        </div>
        <select id="sampleSelect">
          <option value="">Load sample</option>
          ${optionList(state.samples, state.selectedSampleIndex, (sample) => sample.title)}
        </select>
      </div>

      <label class="field">
        <span>Equipment</span>
        <select id="equipmentSelect">
          ${optionList(state.equipment, state.selectedEquipment, (item) => `${item.id} - ${item.name}`)}
        </select>
      </label>

      <label class="field">
        <span>Engineer query / alert</span>
        <textarea id="queryInput">${escapeHtml(state.query)}</textarea>
      </label>

      <div class="sensor-grid">${sensorFields}</div>

      <div class="button-row">
        <button id="runBtn" class="primary-btn" ${state.loading ? "disabled" : ""}>
          ${state.loading ? "Agents running..." : "Run Agent Analysis"}
        </button>
        <button id="normalBtn" class="ghost-btn" type="button">Load Normal</button>
      </div>
    </section>
  `;
}

function renderDecisionPanel(result, risk, score) {
  const staleText = state.stale
    ? "Inputs changed. Re-run analysis for fresh risk, RUL, and recommendations."
    : result
      ? "Decision summary is current for visible inputs."
      : "Run analysis to generate an explainable decision.";
  const fault = result?.diagnosis?.probable_fault || "Waiting for analysis";
  const urgency = result?.risk?.urgency || "Select equipment, confirm sensor values, and run the agent workflow.";
  const failureProbability = result?.prediction?.failure_probability;
  return html`
    <section class="panel decision-panel">
      <div class="panel-head">
        <div>
          <span class="panel-kicker">Decision summary</span>
          <h2>${escapeHtml(fault)}</h2>
        </div>
        <span class="risk-pill ${riskTone(risk)}">${state.stale ? "RE-RUN" : risk.toUpperCase()}</span>
      </div>

      <div class="decision-metrics">
        ${metric("Risk score", result?.risk?.score ?? "-", riskTone(risk))}
        ${metric("RUL estimate", result ? `${result.risk.estimated_rul_hours}h` : "-", "blue")}
        ${metric("Confidence", result ? `${Math.round(result.diagnosis.confidence * 100)}%` : "-", "violet")}
      </div>

      <div class="risk-track"><span class="${riskTone(risk)}" style="width:${score}%"></span></div>
      <p class="urgency">${escapeHtml(urgency)}</p>
      <p class="state-note ${state.stale ? "stale" : result ? "fresh" : ""}">${escapeHtml(staleText)}</p>

      <div class="impact-strip">
        <div><span>Failure probability</span><strong>${failureProbability !== undefined ? Math.round(failureProbability * 100) + "%" : "-"}</strong></div>
        <div><span>Downtime avoided</span><strong>${result?.business_impact ? result.business_impact.estimated_downtime_hours_avoided + "h" : "-"}</strong></div>
        <div><span>Spare actions</span><strong>${result?.business_impact ? result.business_impact.spare_actions_required : "-"}</strong></div>
      </div>
    </section>
  `;
}

function renderView(result, prediction, impact) {
  if (state.activeView === "agents") return renderAgents(result);
  if (state.activeView === "prediction") return renderPrediction(result, prediction, impact);
  if (state.activeView === "report") return renderReport(result);
  return renderDiagnosis(result);
}

function renderDiagnosis(result) {
  return html`
    <section class="cards-grid">
      ${detailCard("Root Causes", list(result?.diagnosis?.root_causes, "No root causes yet."), true)}
      ${detailCard("Immediate Actions", list(result?.recommendations?.immediate_actions, "No actions yet."), true)}
      ${detailCard("Detected Abnormalities", list((result?.anomalies || []).map((a) => `${a.signal}: ${a.value} is ${a.direction} vs ${a.normal_range.join(" - ")}`), "No abnormality detected."), true)}
      ${detailCard("Traceable Evidence", list((result?.retrieved_evidence || []).map((doc) => `${doc.id} | ${doc.type} | ${doc.title}`), "No evidence retrieved yet."))}
      ${detailCard("Procurement Strategy", list((result?.recommendations?.procurement_strategy || []).map((item) => `${item.part}: stock ${item.stock}, lead ${item.lead_time_days} days - ${item.strategy}`), "No procurement escalation required."))}
      ${detailCard("Monitoring Plan", list(result?.recommendations?.monitoring_plan, "No monitoring plan yet."))}
    </section>
  `;
}

function renderAgents(result) {
  const workflow = result?.agent_workflow || [
    "Retrieval Agent", "Anomaly Detection Agent", "Diagnosis Agent", "Risk Assessment Agent",
    "Predictive Maintenance Agent", "Maintenance Planner Agent", "Spare Parts Agent"
  ].map((agent) => ({ agent, status: "waiting", output: "Run analysis to execute this agent." }));

  return html`
    <section class="timeline-panel panel">
      <div class="panel-head">
        <div>
          <span class="panel-kicker">LangGraph-style orchestration</span>
          <h2>Multi-Agent Execution Trace</h2>
        </div>
        <span class="workflow-chip">Sequential + conditional branches</span>
      </div>
      <div class="agent-timeline">
        ${workflow.map((step, index) => html`
          <div class="agent-step">
            <span class="step-index">${String(index + 1).padStart(2, "0")}</span>
            <div>
              <strong>${escapeHtml(step.agent)}</strong>
              <p>${escapeHtml(step.output)}</p>
            </div>
          </div>
        `).join("")}
      </div>
    </section>
  `;
}

function renderPrediction(result, prediction, impact) {
  return html`
    <section class="prediction-grid">
      <div class="panel model-card">
        <span class="panel-kicker">Predictive maintenance</span>
        <h2>${prediction?.degradation_trend || "Awaiting analysis"}</h2>
        <p>${prediction?.model_used || "Run analysis to see anomaly detection, RUL, and failure prediction details."}</p>
        <div class="model-metrics">
          ${metric("Failure window", prediction?.failure_window || "-", "blue")}
          ${metric("Failure probability", prediction ? Math.round(prediction.failure_probability * 100) + "%" : "-", "warn")}
          ${metric("RUL", prediction ? `${prediction.rul_hours}h` : "-", "teal")}
        </div>
      </div>
      <div class="panel model-card">
        <span class="panel-kicker">Production model path</span>
        <h2>How this becomes plant-grade</h2>
        <p>${prediction?.production_upgrade || "Use plant historian data to train equipment-specific anomaly and RUL models."}</p>
        <ul>${list(prediction?.features, "Run analysis to see model features.")}</ul>
      </div>
      <div class="panel model-card wide">
        <span class="panel-kicker">Business value</span>
        <h2>Measurable impact</h2>
        <p>${impact?.value_statement || "Run analysis to estimate downtime avoidance and response improvement."}</p>
        <div class="model-metrics">
          ${metric("Downtime avoided", impact ? `${impact.estimated_downtime_hours_avoided}h` : "-", "teal")}
          ${metric("Response gain", impact ? `${impact.response_time_reduction_pct}%` : "-", "blue")}
          ${metric("Spare actions", impact?.spare_actions_required ?? "-", "violet")}
        </div>
      </div>
    </section>
  `;
}

function renderReport(result) {
  return html`
    <section class="panel report-panel">
      <div class="panel-head">
        <div>
          <span class="panel-kicker">Supervisor-ready output</span>
          <h2>Generated Maintenance Report</h2>
        </div>
        <div class="button-row compact">
          <button id="helpfulBtn" class="ghost-btn" type="button">Helpful</button>
          <button id="correctBtn" class="ghost-btn" type="button">Needs correction</button>
        </div>
      </div>
      <pre>${escapeHtml(result?.report || "Run analysis to generate a structured maintenance decision report.")}</pre>
    </section>
  `;
}

function detailCard(title, body, open = false) {
  return html`
    <details class="panel detail-card" ${open ? "open" : ""}>
      <summary>${title}</summary>
      <ul>${body}</ul>
    </details>
  `;
}

function markStale() {
  if (!state.result) return;
  state.stale = true;
  renderShell();
}

function bindEvents() {
  document.querySelectorAll(".nav-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      state.activeView = btn.dataset.view;
      renderShell();
    });
  });

  document.querySelector("#equipmentSelect")?.addEventListener("change", (event) => {
    state.selectedEquipment = event.target.value;
    state.selectedSampleIndex = "";
    state.sensors = {};
    markStale();
    renderShell();
  });

  document.querySelector("#sampleSelect")?.addEventListener("change", (event) => {
    if (event.target.value === "") return;
    const sample = state.samples[Number(event.target.value)];
    state.selectedSampleIndex = event.target.value;
    state.selectedEquipment = sample.equipment_id;
    state.query = sample.query;
    state.sensors = { ...sample.sensors };
    markStale();
    renderShell();
  });

  document.querySelector("#queryInput")?.addEventListener("input", (event) => {
    state.query = event.target.value;
    markStale();
  });

  document.querySelectorAll("[data-sensor]").forEach((input) => {
    input.addEventListener("input", (event) => {
      const signal = event.target.dataset.sensor;
      if (event.target.value === "") delete state.sensors[signal];
      else state.sensors[signal] = Number(event.target.value);
      markStale();
    });
  });

  document.querySelector("#normalBtn")?.addEventListener("click", () => {
    const normal = state.samples.find((sample) => sample.title.includes("Normal"));
    if (!normal) return;
    state.selectedSampleIndex = String(state.samples.indexOf(normal));
    state.selectedEquipment = normal.equipment_id;
    state.query = normal.query;
    state.sensors = { ...normal.sensors };
    markStale();
    renderShell();
  });

  document.querySelector("#runBtn")?.addEventListener("click", runAnalysis);
  document.querySelector("#helpfulBtn")?.addEventListener("click", () => sendFeedback("helpful"));
  document.querySelector("#correctBtn")?.addEventListener("click", () => sendFeedback("needs_correction"));
}

async function runAnalysis() {
  state.loading = true;
  state.stale = false;
  renderShell();
  try {
    const response = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        equipment_id: state.selectedEquipment,
        query: state.query,
        sensors: state.sensors,
      }),
    });
    const payload = await response.json();
    if (!response.ok || payload.error) throw new Error(payload.error || "Analysis failed");
    state.result = normalizeResult(payload);
    state.stale = false;
    state.activeView = "diagnosis";
  } catch (error) {
    state.result = {
      risk: { level: "waiting", score: 0, urgency: error.message, estimated_rul_hours: 0 },
      diagnosis: { probable_fault: "Analysis error", confidence: 0, root_causes: [error.message] },
      recommendations: { immediate_actions: ["Check input values and rerun analysis."], procurement_strategy: [], monitoring_plan: [] },
      anomalies: [],
      retrieved_evidence: [],
      report: `Analysis error: ${error.message}`,
    };
  } finally {
    state.loading = false;
    renderShell();
  }
}

async function sendFeedback(rating) {
  if (!state.result) return;
  await fetch("/api/feedback", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ rating, result: state.result }),
  });
}

async function init() {
  const [equipment, samples] = await Promise.all([
    fetch("/api/equipment").then((res) => res.json()),
    fetch("/api/sample-cases").then((res) => res.json()),
  ]);
  state.equipment = equipment;
  state.samples = samples;
  state.selectedEquipment = samples[0]?.equipment_id || equipment[0]?.id;
  state.query = samples[0]?.query || state.query;
  state.sensors = { ...(samples[0]?.sensors || {}) };
  state.selectedSampleIndex = samples.length ? "0" : "";
  renderShell();
}

init();
