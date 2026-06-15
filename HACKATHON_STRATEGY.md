# Tata Steel AI Hackathon 2026 Round 2: Agentic AI Challenge Strategy

## 1. Business Understanding

Tata Steel is trying to solve a high-value industrial maintenance problem: critical equipment in steel manufacturing plants fails or degrades in complex, interconnected ways, while maintenance engineers must make fast decisions using fragmented information. A steel plant is not a simple machine environment. Rolling mills, blast furnace fans, hydraulic pumps, caster segments, conveyors, drives, bearings, motors, cooling systems, lubrication systems, and process-control systems interact continuously. A single abnormal vibration trend, temperature excursion, hydraulic pressure drop, or lubrication issue can cascade into production loss, quality defects, safety risk, and expensive unplanned shutdown.

The current pain point is not only failure prediction. It is the complete decision loop around maintenance: engineers receive alarms, check logs, search manuals, consult SOPs, review prior failure reports, inspect spares, estimate urgency, speak with supervisors, and then create a maintenance action. This process is manual, time-consuming, dependent on senior experience, and inconsistent across shifts. Junior engineers may miss historical patterns. Senior engineers may know the right action but lose time collecting evidence. Procurement teams may discover too late that a critical spare has long lead time. Supervisors may lack a structured report explaining why shutdown is needed.

In steel manufacturing, the business value is measurable. A good solution should reduce unplanned downtime, reduce mean time to diagnose, reduce mean time to repair, improve diagnostic consistency, avoid catastrophic failures, improve spare availability, and support the shift from reactive to predictive maintenance. The strongest prototype should express business impact in practical terms such as estimated downtime hours avoided, faster response time, critical spare alerts, risk classification, and supervisor-ready decision summaries.

## 2. Hidden Expectations

Explicit requirements include multi-source maintenance inputs, natural-language interaction, LLM/SLM reasoning, knowledge integration, explainable recommendations, abnormality detection, failure prediction, feedback loop, real-time alerting, structured reports, and source code/demo deliverables.

Implicit expectations are more important for winning. Tata Steel likely expects participants to understand industrial constraints: safety approval, production criticality, spare lead time, procurement delay, shutdown planning, supervisor escalation, and traceability. Judges will not be impressed by a generic chatbot that says "replace the bearing." They will look for a workflow that looks usable by real plant teams. The system should ask: Is the equipment critical? Is the signal abnormal? Is this a known failure pattern? What does the SOP say? Is the spare available? How urgent is intervention? What should the engineer do now? What should the supervisor approve? What should procurement reserve?

Average teams will build a chatbot over documents. Strong teams will build a maintenance assistant with RAG, risk scoring, and reports. Winning teams will show an agentic workflow with specialized agents, explainable outputs, simulated real-time alerts, prediction/RUL logic, feedback learning, and a dashboard that clearly communicates business value.

Innovative elements judges may reward include a LangGraph-style agent workflow, confidence and evidence traceability, dynamic abnormality scoring, RUL estimates, spare-aware maintenance prioritization, role-based alerts, digital logbook generation, feedback-driven rule/model improvement, and plant-level bottleneck prioritization.

## 3. Agentic AI Analysis

This is an Agentic AI challenge because Tata Steel is not asking for only prediction or only chat. They want an intelligent maintenance decision-support system that can plan, reason, retrieve evidence, call tools, evaluate risk, generate actions, and improve from feedback. An agentic system has goals, memory, tools, workflow state, and the ability to coordinate multiple reasoning steps.

Expected agentic capabilities include:

- Tool use: retrieve manuals/SOPs/logs, inspect sensor summaries, check spare stock, generate reports.
- Multi-step reasoning: diagnose fault, infer root cause, classify risk, plan actions.
- Autonomy: decide which agents to run based on input type and risk.
- Explainability: cite evidence and state why a recommendation was made.
- Feedback learning: store engineer correction/outcome for future recommendations.
- Conditional escalation: notify supervisor or procurement when critical risk or spare lead-time issue exists.

Specialized agents should handle retrieval, abnormality detection, diagnosis, root cause analysis, risk assessment, predictive maintenance, spare planning, maintenance planning, report generation, alerting, and feedback learning.

## 4. Complete System Architecture

```text
                     +-------------------------------+
                     | Maintenance Engineer Dashboard |
                     | Chat + Forms + Alerts + Report |
                     +---------------+---------------+
                                     |
                                     v
                     +-------------------------------+
                     | Backend API / Gateway          |
                     | Auth, sessions, audit logs     |
                     +---------------+---------------+
                                     |
                                     v
                     +-------------------------------+
                     | Multi-Agent Orchestrator       |
                     | LangGraph / CrewAI workflow    |
                     +---+-----+-----+-----+-----+----+
                         |     |     |     |     |
        +----------------+     |     |     |     +----------------+
        v                      v     v     v                      v
+---------------+   +--------------+ +--------------+   +----------------+
| Retrieval     |   | Anomaly      | | Diagnosis    |   | Spare Parts    |
| Agent         |   | Agent        | | RCA Agent    |   | Agent          |
+-------+-------+   +------+-------+ +------+-------+   +-------+--------+
        |                  |                |                   |
        v                  v                v                   v
+---------------+   +--------------+ +--------------+   +----------------+
| Vector DB     |   | ML Models    | | LLM/SLM      |   | ERP/CMMS/SAP   |
| SOP/manuals   |   | RUL/anomaly  | | reasoning    |   | spare stock    |
+---------------+   +--------------+ +--------------+   +----------------+
                         |                |
                         v                v
                   +-----------------------------+
                   | Risk + Maintenance Planner  |
                   +-------------+---------------+
                                 |
                                 v
                   +-----------------------------+
                   | Report + Alerting + Logbook |
                   +-------------+---------------+
                                 |
                                 v
                   +-----------------------------+
                   | Feedback Learning Store     |
                   +-----------------------------+
```

Frontend should be a plant-style dashboard, not a marketing page. It should contain equipment selector, engineer query, sensor values, risk summary, agent trace, abnormality cards, RUL prediction, spare recommendations, evidence citations, and maintenance report. Backend should expose APIs for analysis, document upload, alert ingestion, feedback, and report generation. Database stores equipment master, maintenance logs, alerts, feedback, reports, users, and work orders. Vector database stores chunked manuals, SOPs, and failure reports. LLM layer handles contextual reasoning and natural language output. ML prediction layer handles anomaly detection and RUL. Alerting system sends role-specific notifications. Feedback system stores engineer corrections and final outcomes.

## 5. Multi-Agent Design

Retrieval Agent:
Purpose: search manuals, SOPs, logs, failure reports.
Inputs: equipment ID, query, abnormal signals.
Outputs: ranked evidence with source IDs.
Tools: vector database, keyword search, metadata filter.

Anomaly Detection Agent:
Purpose: detect abnormal sensor/process conditions.
Inputs: sensor snapshot, normal ranges, historical trends.
Outputs: abnormal signals, severity, trend.
Tools: thresholds, Isolation Forest, statistical control charts.

Diagnosis Agent:
Purpose: identify probable fault.
Inputs: query, anomalies, retrieved evidence.
Outputs: probable diagnosis and confidence.
Tools: LLM/SLM, rules, failure taxonomy.

Root Cause Agent:
Purpose: identify likely root causes.
Inputs: diagnosis, historical failures, SOPs, symptoms.
Outputs: ranked root causes.
Tools: LLM reasoning, causal rules, fault tree.

Risk Assessment Agent:
Purpose: classify low/medium/high/critical risk.
Inputs: criticality, severity, diagnosis confidence, production impact.
Outputs: risk score, urgency, escalation need.
Tools: scoring model, safety rules.

Predictive Maintenance Agent:
Purpose: estimate degradation, failure probability, RUL.
Inputs: sensor trend, anomaly score, failure history.
Outputs: RUL, failure window, probability.
Tools: XGBoost, survival model, LSTM autoencoder, hybrid scoring.

Spare Parts Agent:
Purpose: evaluate spare availability and procurement lead time.
Inputs: diagnosis, required parts, stock, lead time.
Outputs: reserve/purchase recommendations.
Tools: ERP/CMMS/SAP API or mock inventory.

Maintenance Planner Agent:
Purpose: recommend immediate and long-term actions.
Inputs: risk, diagnosis, spares, SOPs.
Outputs: step-by-step plan.
Tools: SOP retrieval, planner rules, LLM formatting.

Report Generator Agent:
Purpose: generate supervisor-ready structured report.
Inputs: all previous outputs.
Outputs: maintenance decision report and logbook entry.
Tools: template engine, LLM summarizer.

Alerting Agent:
Purpose: notify correct roles.
Inputs: risk level, equipment area, action type.
Outputs: alerts for engineer/supervisor/procurement.
Tools: email, Teams, SMS, dashboard notification.

Feedback Agent:
Purpose: capture corrections and outcomes.
Inputs: engineer feedback, final repair outcome.
Outputs: learning records for model/rule tuning.
Tools: feedback DB, analytics.

Workflow should use LangGraph when possible. Retrieval and anomaly detection can run in parallel. Diagnosis depends on both. RCA depends on diagnosis and evidence. Risk and prediction can run after anomalies and diagnosis. Spare and maintenance planning can run in parallel after risk. Report and alerts run last. Critical risk creates conditional branches for supervisor and procurement escalation.

## 6. Feature Prioritization

Must Have:
- Working dashboard or chatbot interface.
- Equipment selection and fault input.
- Sensor values and abnormality detection.
- RAG-style evidence retrieval.
- Diagnosis and root cause explanation.
- Risk score and priority.
- Maintenance recommendations.
- Structured report.
- Clear install/run instructions.

Good To Have:
- Agent execution trace.
- RUL/failure probability estimate.
- Spare availability and procurement lead time.
- Feedback buttons.
- Sample cases for normal, medium, and critical scenarios.
- Downloadable report/logbook entry.

Advanced Features:
- Multi-turn conversation.
- Real-time simulated IoT stream.
- Role-based alerts.
- Vector DB with document upload.
- Model monitoring and confidence.
- Plant-level bottleneck prioritization.

Winning Features:
- LangGraph multi-agent workflow.
- Explainable RUL and anomaly model.
- Human-in-the-loop feedback learning.
- Supervisor/procurement views.
- Quantified business impact.
- Polished dashboard that feels plant-ready.

## 7. Predictive Maintenance

RUL prediction should estimate how long equipment can safely continue before intervention. In a hackathon, real historical degradation data may be unavailable, so use a hybrid approach: threshold anomaly severity, equipment criticality, failure-history rules, and exponential RUL decay. In production, use vibration/temperature/current/pressure trends over time and train models such as XGBoost regression, Random Forest regression, survival analysis, Weibull models, LSTM, GRU, or Transformer time-series models.

Anomaly detection should compare current signals against equipment-specific normal ranges and historical baseline. Simple prototype methods include z-score, EWMA, moving average drift, and threshold severity. Production models include Isolation Forest, One-Class SVM, Autoencoder, LSTM Autoencoder, PCA/T2 statistics, and change-point detection.

Failure prediction should estimate probability of failure in windows such as next shift, 24 hours, 72 hours, or 7 days. Suitable models include XGBoost classifier, LightGBM, logistic regression baseline, survival models, random forest, temporal CNN, LSTM, or transformer time-series models. If data is unavailable, simulate industrial data by defining normal ranges, injecting drift, spikes, noise, and failure events. Create synthetic sequences where temperature and vibration rise before bearing failure, pressure drops before hydraulic failure, or bearing noise increases before fan failure.

## 8. Knowledge System

Manuals should be processed using document ingestion: PDF/DOCX parsing, section extraction, chunking by headings, metadata tagging by equipment ID, chunk embedding, and vector indexing. SOPs should be indexed with metadata such as equipment, failure mode, action type, safety rule, and shutdown requirement. Maintenance logs should be stored as structured records with date, equipment, symptoms, root cause, action taken, spare used, downtime, and outcome.

RAG should filter by equipment ID first, then retrieve semantically relevant SOP/manual/log chunks. The answer should cite document IDs and explain how evidence supports each recommendation. Explainable recommendations should combine retrieved text, sensor abnormalities, historical failure patterns, and rule/model outputs. Avoid black-box recommendations.

## 9. Judging Criteria Analysis

Innovation:
Low: basic chatbot.
Medium: RAG assistant with risk score.
High: multi-agent workflow with RUL, spares, alerts, feedback, and business impact.

Technical Complexity:
Low: static UI and hardcoded answers.
Medium: API, document search, rule engine.
High: orchestrated agents, vector retrieval, ML prediction, role-specific outputs.

Agentic AI Usage:
Low: single LLM prompt.
Medium: several prompt stages.
High: specialized agents with tools, state, conditional routing, and trace.

Scalability:
Low: one equipment only.
Medium: JSON/mock DB with multiple equipment.
High: database schema, vector DB, equipment metadata, extensible model layer.

Business Impact:
Low: vague benefits.
Medium: downtime/reliability claims.
High: quantified downtime avoided, response improvement, spare-risk reduction.

User Experience:
Low: raw chatbot.
Medium: form + output.
High: plant dashboard with alerts, risk meter, evidence, actions, report.

Presentation:
Low: unclear demo.
Medium: explain flow.
High: scenario-based demo from alert to report and supervisor/procurement value.

## 10. 5-7 Day Winning Roadmap

Day 1: finalize scope, data schema, sample equipment, sample SOPs, failure logs, normal ranges, demo scenarios.

Day 2: build backend analysis API, abnormality detection, diagnosis rules, risk scoring, report template.

Day 3: build RAG layer or mock retrieval, document chunks, evidence citations, root cause mapping.

Day 4: build dashboard UI with input, risk summary, agent workflow, evidence, actions, report.

Day 5: add RUL/failure probability, spare planning, feedback loop, business impact metrics.

Day 6: polish UI, add simulated alert scenarios, test normal/medium/critical cases, create screen recording.

Day 7: prepare presentation: problem, architecture, demo, innovation, impact, limitations, production roadmap.

Avoid overbuilding login, complex deployment, too many equipment types, or training deep models without data. A clean, explainable, working prototype beats a broken complex system.

## 11. Gap Analysis

Simple Chatbot:
Fast but weak. It can answer questions but does not demonstrate agentic workflow, prediction, structured decision-making, or business impact.

RAG-Based Maintenance Assistant:
Better. It can cite SOPs/manuals and answer engineer queries. Still incomplete if it lacks sensor analysis, risk scoring, RUL, spare planning, and feedback.

Full Agentic Multi-Agent Maintenance Wizard:
Best fit. It satisfies the stated and hidden requirements: multi-source reasoning, tool use, diagnosis, RCA, prediction, risk, planning, report generation, alerting, and feedback.

## 12. Final Recommendation

The best realistic hackathon prototype is a full Agentic Multi-Agent Maintenance Wizard with a polished dashboard, mock industrial knowledge base, explainable hybrid prediction model, and strong architecture story.

Recommended stack:
- Frontend: React + Tailwind if packages are available; otherwise dependency-free SPA with Tailwind-style CSS.
- Backend: Python FastAPI in production; current prototype uses standard Python HTTP server for zero-dependency demo.
- Orchestrator: LangGraph for stateful multi-agent workflow.
- LLM: GPT-4.1/GPT-4o, Claude, Gemini, or local SLM depending on policy.
- Vector DB: Chroma, FAISS, Qdrant, or pgvector.
- Database: PostgreSQL for equipment/logs/feedback/reports.
- ML: scikit-learn/XGBoost for anomaly/RUL baseline; PyTorch for LSTM autoencoder later.
- Alerting: Teams/email/SMS mock integration.
- Reporting: template-based report plus optional PDF export.

Dashboard should show equipment health, risk, RUL, failure probability, agent trace, evidence, actions, spare strategy, monitoring plan, business impact, and report. Demo should show three cases: normal health check, medium degradation, and critical failure risk. This proves the system understands both “no issue” and “urgent issue,” which is essential for credibility.

