# Agentic AI Maintenance Wizard

Working prototype for the Tata Steel Agentic AI challenge problem statement.

The system acts as an intelligent maintenance decision-support assistant for steel plant equipment. It accepts engineer queries and sensor snapshots, retrieves relevant SOP/manual/log evidence, detects abnormal conditions, diagnoses likely faults, estimates risk and remaining useful life, recommends maintenance/procurement actions, and generates a structured maintenance report.

## Why This Matches the Challenge

- Problem understanding: focuses on downtime, diagnosis delay, fragmented maintenance knowledge, and spare planning.
- Agentic AI concepts: implements a multi-agent reasoning pipeline instead of a plain chatbot.
- Technical implementation: runnable browser UI and CLI with traceable outputs.
- Scalability: data-driven knowledge base can be extended with real equipment records, vector retrieval, or LLM APIs.
- Presentation quality: includes dashboard, report, sample cases, and demo flow.
- Business impact: supports faster response, higher diagnostic consistency, predictive maintenance, and better procurement decisions.

## Agent Pipeline

1. Retrieval Agent
   - Searches SOPs, manuals, failure reports, and maintenance logs for the selected equipment.
   - Returns traceable evidence with document IDs.

2. Abnormality Detection Agent
   - Compares sensor values against equipment-specific normal ranges.
   - Produces abnormal signals and severity scores.

3. Diagnosis and RCA Agent
   - Matches symptoms, keywords, and abnormal signals to fault rules.
   - Produces probable fault, confidence, and root causes.

4. Risk and RUL Agent
   - Combines equipment criticality, anomaly severity, and diagnosis confidence.
   - Produces risk level, urgency, risk score, and estimated remaining useful life.

5. Maintenance Planning Agent
   - Recommends immediate actions, planned actions, monitoring plan, and spare strategy.
   - Uses stock and procurement lead-time information.

6. Report Agent
   - Generates a supervisor-ready maintenance decision report.

7. Feedback Agent
   - Saves engineer feedback to `data/feedback_log.jsonl`.
   - This is the hook for continuous improvement in a production version.

## Technology Stack

- Python 3
- Standard library only
- Browser UI: HTML, CSS, JavaScript
- Backend: Python `http.server`
- Data: JSON knowledge base and sample cases

No external packages are required.

## Project Structure

```text
maintenance-wizard/
  app.py
  README.md
  data/
    knowledge_base.json
    sample_cases.json
  static/
    index.html
    styles.css
    app.js
```

## Execution Steps

Open PowerShell in this folder:

```powershell
cd "C:\Users\Vanaja J\Documents\New project\maintenance-wizard"
```

Start the web prototype:

```powershell
python app.py serve --host 127.0.0.1 --port 8000
```

Open in browser:

```text
http://127.0.0.1:8000
```

Run a CLI demo:

```powershell
python app.py analyze --equipment RM-MTR-01 --query "Main drive motor has high vibration, rising temperature, bearing noise, and lubrication pressure is low." --sensors "temperature_c=91,vibration_mm_s=7.8,current_a=248,lubrication_pressure_bar=1.8"
```

Print full JSON output:

```powershell
python app.py analyze --equipment CC-PMP-02 --query "Hydraulic pump pressure is dropping and oil particle count is abnormal." --sensors "pressure_bar=128,oil_particle_count=34,temperature_c=62,vibration_mm_s=3.2" --json
```

## Demo Script

Use this story during the screen recording:

1. Select sample case: `Rolling mill motor bearing risk`.
2. Show the engineer query and sensor values.
3. Click `Run Agent Analysis`.
4. Explain the agent pipeline:
   - Retrieval Agent found SOP/manual/failure report evidence.
   - Abnormality Agent detected high temperature, high vibration, and low lubrication pressure.
   - Diagnosis Agent identified bearing wear or lubrication failure.
   - Risk Agent classified the issue as high/critical and estimated RUL.
   - Planner Agent recommended inspection, lubrication checks, bearing replacement planning, and spare reservation.
   - Report Agent generated a structured maintenance report.
5. Click `Helpful` or `Needs correction` to show the feedback loop.

## Sample Input

```json
{
  "equipment_id": "RM-MTR-01",
  "query": "Main drive motor has high vibration, rising temperature, bearing noise, and lubrication pressure is low.",
  "sensors": {
    "temperature_c": 91,
    "vibration_mm_s": 7.8,
    "current_a": 248,
    "lubrication_pressure_bar": 1.8
  }
}
```

## Sample Output

- Probable fault: Bearing wear or lubrication failure
- Root causes: insufficient lubrication pressure, bearing wear, coupling misalignment, blocked cooling airflow
- Risk: high/critical depending on sensor severity
- Urgency: immediate intervention or action within 24 hours
- Actions:
  - Inspect bearing housing temperature and acoustic noise.
  - Check lubrication pressure, grease/oil flow, and contamination.
  - Verify coupling alignment and foundation looseness.
- Evidence:
  - SOP-RM-MTR-01
  - MAN-RM-MTR-01
  - FR-2025-118

## Assumptions and Limitations

- Sample data is synthetic because real plant manuals, logs, and sensor streams are not provided.
- Diagnosis uses deterministic rules to keep the prototype runnable without external APIs.
- A production system should replace simple keyword retrieval with vector search/RAG.
- A production system can integrate an LLM or SLM for richer reasoning and multi-turn conversation.
- RUL is an explainable estimate based on risk score, not a trained predictive model.
- Real deployment would require plant historian integration, CMMS/SAP integration, authentication, audit trails, and safety approval workflow.

## Production Extension Plan

- Add RAG using embeddings over manuals, SOPs, and failure reports.
- Connect to historian/IoT streams for live abnormality detection.
- Add a trained anomaly model for each critical equipment class.
- Add CMMS/SAP work-order creation and spare reservation.
- Add role-based alerts for engineer, supervisor, procurement, and operations head.
- Use feedback records to tune rules, retrieval ranking, and model prompts.
