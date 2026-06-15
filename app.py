from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
STATIC_DIR = BASE_DIR / "static"
KB_PATH = DATA_DIR / "knowledge_base.json"
FEEDBACK_PATH = DATA_DIR / "feedback_log.jsonl"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-zA-Z0-9_]+", text.lower()))


class KnowledgeBase:
    def __init__(self, path: Path = KB_PATH) -> None:
        raw = load_json(path)
        self.equipment = {item["id"]: item for item in raw["equipment"]}
        self.documents = raw["documents"]
        self.rules = raw["rules"]

    def list_equipment(self) -> list[dict[str, Any]]:
        return list(self.equipment.values())

    def get_equipment(self, equipment_id: str) -> dict[str, Any]:
        if equipment_id not in self.equipment:
            raise ValueError(f"Unknown equipment_id: {equipment_id}")
        return self.equipment[equipment_id]

    def retrieve(self, equipment_id: str, query: str, limit: int = 4) -> list[dict[str, Any]]:
        q_tokens = tokenize(query)
        ranked: list[tuple[float, dict[str, Any]]] = []
        for doc in self.documents:
            if doc["equipment_id"] != equipment_id:
                continue
            d_tokens = tokenize(f'{doc["title"]} {doc["type"]} {doc["content"]}')
            overlap = len(q_tokens & d_tokens)
            score = overlap + (1.5 if doc["type"] in {"SOP", "Failure Report"} else 0)
            ranked.append((score, doc))
        ranked.sort(key=lambda row: row[0], reverse=True)
        return [doc for score, doc in ranked[:limit] if score > 0]


class MaintenanceWizard:
    def __init__(self, kb: KnowledgeBase) -> None:
        self.kb = kb

    def analyze(self, equipment_id: str, query: str, sensors: dict[str, Any]) -> dict[str, Any]:
        equipment = self.kb.get_equipment(equipment_id)
        evidence = self.kb.retrieve(equipment_id, query)
        anomalies = self._detect_anomalies(equipment, sensors)
        diagnosis = self._diagnose(equipment, query, sensors, anomalies)
        risk = self._risk(equipment, anomalies, diagnosis)
        prediction = self._prediction(equipment, anomalies, diagnosis, risk)
        recommendations = self._recommend(equipment, diagnosis, risk)
        business_impact = self._business_impact(equipment, risk, recommendations)
        agent_workflow = self._agent_workflow(evidence, anomalies, diagnosis, risk, prediction, recommendations)
        report = self._report(equipment, query, sensors, evidence, anomalies, diagnosis, risk, recommendations)
        return {
            "timestamp": dt.datetime.now().isoformat(timespec="seconds"),
            "equipment": {
                "id": equipment["id"],
                "name": equipment["name"],
                "area": equipment["area"],
                "criticality": equipment["criticality"],
            },
            "query": query,
            "sensors": sensors,
            "retrieved_evidence": evidence,
            "anomalies": anomalies,
            "diagnosis": diagnosis,
            "risk": risk,
            "prediction": prediction,
            "recommendations": recommendations,
            "business_impact": business_impact,
            "agent_workflow": agent_workflow,
            "report": report,
        }

    def _detect_anomalies(self, equipment: dict[str, Any], sensors: dict[str, Any]) -> list[dict[str, Any]]:
        anomalies: list[dict[str, Any]] = []
        ranges = equipment.get("normal_ranges", {})
        for signal, value in sensors.items():
            if value in ("", None) or signal not in ranges:
                continue
            try:
                value_num = float(value)
            except (TypeError, ValueError):
                continue
            low, high = ranges[signal]
            if value_num < low:
                severity = min(1.0, (low - value_num) / max(abs(low), 1))
                anomalies.append(
                    {
                        "signal": signal,
                        "value": value_num,
                        "normal_range": [low, high],
                        "direction": "below normal",
                        "severity": round(severity, 2),
                    }
                )
            elif value_num > high:
                severity = min(1.0, (value_num - high) / max(abs(high), 1))
                anomalies.append(
                    {
                        "signal": signal,
                        "value": value_num,
                        "normal_range": [low, high],
                        "direction": "above normal",
                        "severity": round(severity, 2),
                    }
                )
        anomalies.sort(key=lambda item: item["severity"], reverse=True)
        return anomalies

    def _diagnose(
        self, equipment: dict[str, Any], query: str, sensors: dict[str, Any], anomalies: list[dict[str, Any]]
    ) -> dict[str, Any]:
        q_tokens = tokenize(query)
        anomaly_signals = {item["signal"] for item in anomalies}
        if not anomalies and q_tokens & {"normal", "routine", "healthy", "health", "ok", "stable"}:
            return {
                "probable_fault": "Normal operating condition",
                "confidence": 0.9,
                "root_causes": ["No abnormal sensor condition detected"],
                "reasoning": [
                    "All supplied sensor values are within equipment-specific normal ranges.",
                    "Engineer query indicates routine or normal health check.",
                ],
            }
        scored: list[tuple[float, dict[str, Any]]] = []
        for rule in self.kb.rules:
            keyword_hits = len(q_tokens & set(rule["keywords"]))
            signal_hits = len(anomaly_signals & set(rule["signals"]))
            equipment_bonus = 1.4 if any(token in q_tokens for token in tokenize(equipment["name"])) else 0
            score = keyword_hits * 1.2 + signal_hits * 1.7 + equipment_bonus
            if score:
                scored.append((score, rule))
        scored.sort(key=lambda row: row[0], reverse=True)
        best_rule = scored[0][1] if scored else self.kb.rules[0]
        confidence = min(0.95, 0.35 + (scored[0][0] if scored else 1) / 12)
        likely_causes = best_rule["root_causes"][:]
        if "lubrication_pressure_bar" in anomaly_signals:
            likely_causes.insert(0, "insufficient lubrication pressure")
        if "oil_particle_count" in anomaly_signals:
            likely_causes.insert(0, "oil contamination accelerating component wear")
        likely_causes = list(dict.fromkeys(likely_causes))
        return {
            "probable_fault": best_rule["fault"],
            "confidence": round(confidence, 2),
            "root_causes": likely_causes[:4],
            "reasoning": [
                f"Matched {best_rule['fault']} rule from keywords/signals.",
                f"Detected abnormal signals: {', '.join(anomaly_signals) if anomaly_signals else 'none'}."
            ],
        }

    def _risk(
        self, equipment: dict[str, Any], anomalies: list[dict[str, Any]], diagnosis: dict[str, Any]
    ) -> dict[str, Any]:
        criticality = float(equipment["criticality"])
        anomaly_score = sum(item["severity"] for item in anomalies)
        max_anomaly = max((item["severity"] for item in anomalies), default=0)
        confidence = float(diagnosis["confidence"])
        score = (criticality * 5) + min(38, anomaly_score * 24) + (max_anomaly * 22)
        if anomalies:
            score += confidence * 10
        else:
            score += confidence * 3
        emergency_signals = {
            item["signal"]
            for item in anomalies
            if item["severity"] >= 0.75
            or item["signal"] in {"lubrication_pressure_bar", "pressure_bar"} and item["direction"] == "below normal" and item["severity"] >= 0.25
        }
        if emergency_signals and criticality >= 4:
            score += 12
        score = min(100, round(score))
        if score >= 82:
            level = "critical"
            urgency = "Immediate intervention. Reduce load or stop equipment if trend worsens."
        elif score >= 62:
            level = "high"
            urgency = "Act within 24 hours and plan controlled shutdown if condition persists."
        elif score >= 40:
            level = "medium"
            urgency = "Inspect in next planned maintenance window and monitor trend."
        else:
            level = "low"
            urgency = "Continue monitoring and log observations."
        estimated_rul_hours = max(6, int(360 * math.exp(-score / 45)))
        return {
            "score": score,
            "level": level,
            "urgency": urgency,
            "estimated_rul_hours": estimated_rul_hours,
            "basis": "Risk combines equipment criticality, abnormal sensor severity, emergency conditions, and diagnostic confidence.",
        }

    def _prediction(
        self,
        equipment: dict[str, Any],
        anomalies: list[dict[str, Any]],
        diagnosis: dict[str, Any],
        risk: dict[str, Any],
    ) -> dict[str, Any]:
        anomaly_score = sum(item["severity"] for item in anomalies)
        max_anomaly = max((item["severity"] for item in anomalies), default=0)
        failure_probability = min(
            0.97,
            0.05
            + (risk["score"] / 145)
            + (anomaly_score * 0.13)
            + (float(equipment["criticality"]) * 0.015),
        )
        if risk["level"] == "critical":
            window = "next shift to 24 hours"
        elif risk["level"] == "high":
            window = "24 to 72 hours"
        elif risk["level"] == "medium":
            window = "3 to 7 days"
        else:
            window = "no immediate failure window"
        model_features = [
            "equipment criticality",
            "sensor deviation severity",
            "maximum abnormal signal",
            "diagnosis confidence",
            "spare lead time exposure",
        ]
        trend = "stable"
        if max_anomaly >= 0.75:
            trend = "rapid degradation"
        elif max_anomaly >= 0.25:
            trend = "early degradation"
        elif anomalies:
            trend = "watchlist"
        return {
            "rul_hours": risk["estimated_rul_hours"],
            "failure_probability": round(failure_probability, 2),
            "failure_window": window,
            "degradation_trend": trend,
            "model_used": "Explainable hybrid scoring model: threshold anomaly detector + rules + RUL risk curve",
            "production_upgrade": "Replace with Isolation Forest/LSTM Autoencoder for anomalies and XGBoost/Survival model for RUL when plant history is available.",
            "features": model_features,
        }

    def _recommend(
        self, equipment: dict[str, Any], diagnosis: dict[str, Any], risk: dict[str, Any]
    ) -> dict[str, Any]:
        if diagnosis["probable_fault"] == "Normal operating condition":
            return {
                "immediate_actions": [
                    "Continue normal operation.",
                    "Log the health check result in the digital maintenance record.",
                    "Keep routine shift-wise monitoring active.",
                ],
                "planned_actions": [
                    "Review trend again during the next planned maintenance window.",
                    "No spare reservation required unless trend changes.",
                    "Capture engineer confirmation as feedback for future recommendations.",
                ],
                "procurement_strategy": [],
                "monitoring_plan": [
                    "Continue monitoring all listed signals within normal limits.",
                    "Re-run analysis if temperature, vibration, pressure, or current crosses warning limits.",
                ],
            }
        rule = next(
            (item for item in self.kb.rules if item["fault"] == diagnosis["probable_fault"]),
            self.kb.rules[0],
        )
        spares = equipment.get("spares", [])
        procurement = []
        for spare in spares:
            if spare["stock"] <= 0 or risk["level"] in {"high", "critical"}:
                procurement.append(
                    {
                        "part": spare["part"],
                        "stock": spare["stock"],
                        "lead_time_days": spare["lead_time_days"],
                        "strategy": "Issue reservation now" if spare["stock"] > 0 else "Raise urgent purchase request",
                    }
                )
        return {
            "immediate_actions": rule["actions"][:3],
            "planned_actions": [
                "Create maintenance work order with attached diagnostic report.",
                "Assign supervisor review for high or critical risks.",
                "Capture outcome after inspection to improve future recommendations.",
            ],
            "procurement_strategy": procurement,
            "monitoring_plan": [
                "Trend abnormal sensor values every shift until normalized.",
                "Escalate if risk level increases or estimated RUL falls below one shift.",
            ],
        }

    def _business_impact(
        self, equipment: dict[str, Any], risk: dict[str, Any], recommendations: dict[str, Any]
    ) -> dict[str, Any]:
        criticality = int(equipment["criticality"])
        downtime_hours_avoided = {
            "low": 0,
            "medium": 2 + criticality,
            "high": 6 + (criticality * 2),
            "critical": 12 + (criticality * 3),
        }[risk["level"]]
        response_time_reduction_pct = {
            "low": 15,
            "medium": 35,
            "high": 55,
            "critical": 70,
        }[risk["level"]]
        spare_risk = len(recommendations["procurement_strategy"])
        return {
            "estimated_downtime_hours_avoided": downtime_hours_avoided,
            "response_time_reduction_pct": response_time_reduction_pct,
            "spare_actions_required": spare_risk,
            "value_statement": "Earlier fault triage, explainable action planning, and spare visibility reduce unplanned downtime and maintenance decision delay.",
        }

    def _agent_workflow(
        self,
        evidence: list[dict[str, Any]],
        anomalies: list[dict[str, Any]],
        diagnosis: dict[str, Any],
        risk: dict[str, Any],
        prediction: dict[str, Any],
        recommendations: dict[str, Any],
    ) -> list[dict[str, Any]]:
        return [
            {
                "agent": "Retrieval Agent",
                "status": "complete",
                "output": f"Retrieved {len(evidence)} traceable maintenance records.",
            },
            {
                "agent": "Anomaly Detection Agent",
                "status": "complete",
                "output": f"Detected {len(anomalies)} abnormal signal(s).",
            },
            {
                "agent": "Diagnosis Agent",
                "status": "complete",
                "output": f"{diagnosis['probable_fault']} at {diagnosis['confidence'] * 100:.0f}% confidence.",
            },
            {
                "agent": "Risk Assessment Agent",
                "status": "complete",
                "output": f"{risk['level'].upper()} risk with score {risk['score']}.",
            },
            {
                "agent": "Predictive Maintenance Agent",
                "status": "complete",
                "output": f"RUL {prediction['rul_hours']}h; failure probability {prediction['failure_probability'] * 100:.0f}%.",
            },
            {
                "agent": "Maintenance Planner Agent",
                "status": "complete",
                "output": f"Generated {len(recommendations['immediate_actions'])} immediate action(s).",
            },
            {
                "agent": "Spare Parts Agent",
                "status": "complete",
                "output": f"Flagged {len(recommendations['procurement_strategy'])} spare/procurement action(s).",
            },
        ]

    def _report(
        self,
        equipment: dict[str, Any],
        query: str,
        sensors: dict[str, Any],
        evidence: list[dict[str, Any]],
        anomalies: list[dict[str, Any]],
        diagnosis: dict[str, Any],
        risk: dict[str, Any],
        recommendations: dict[str, Any],
    ) -> str:
        evidence_lines = [
            f"- {doc['id']} ({doc['type']}): {doc['title']}" for doc in evidence
        ] or ["- No matching document found; recommendation based on rules and sensor limits."]
        anomaly_lines = [
            f"- {a['signal']}={a['value']} is {a['direction']} {a['normal_range']}."
            for a in anomalies
        ] or ["- No numeric abnormality detected from supplied sensor values."]
        action_lines = [f"- {item}" for item in recommendations["immediate_actions"]]
        return "\n".join(
            [
                f"Maintenance Decision Report - {equipment['name']}",
                f"Area: {equipment['area']} | Equipment ID: {equipment['id']}",
                f"Engineer Query: {query}",
                "",
                "Sensor Snapshot:",
                json.dumps(sensors, indent=2),
                "",
                "Detected Abnormalities:",
                *anomaly_lines,
                "",
                f"Probable Diagnosis: {diagnosis['probable_fault']} ({diagnosis['confidence'] * 100:.0f}% confidence)",
                f"Likely Root Causes: {', '.join(diagnosis['root_causes'])}",
                f"Risk: {risk['level'].upper()} | Score: {risk['score']} | Estimated RUL: {risk['estimated_rul_hours']} hours",
                f"Urgency: {risk['urgency']}",
                "",
                "Immediate Maintenance Actions:",
                *action_lines,
                "",
                "Traceable Evidence:",
                *evidence_lines,
            ]
        )


KB = KnowledgeBase()
WIZARD = MaintenanceWizard(KB)


def parse_sensors(raw: str | None) -> dict[str, float]:
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        cleaned = raw.strip().strip("{}")
        parsed = {}
        for item in cleaned.split(","):
            if not item.strip():
                continue
            if ":" in item:
                key, value = item.split(":", 1)
            elif "=" in item:
                key, value = item.split("=", 1)
            else:
                raise ValueError(f"Cannot parse sensor item: {item}")
            parsed[key.strip().strip("\"'")] = value.strip().strip("\"'")
    return {key: float(value) for key, value in parsed.items() if value not in ("", None)}


def write_json(handler: BaseHTTPRequestHandler, status: int, payload: Any) -> None:
    body = json.dumps(payload, indent=2).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class WizardHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/equipment":
            write_json(self, 200, KB.list_equipment())
            return
        if parsed.path == "/api/sample-cases":
            write_json(self, 200, load_json(DATA_DIR / "sample_cases.json"))
            return
        if parsed.path in {"/", "/index.html"}:
            self._serve_static("index.html", "text/html; charset=utf-8")
            return
        if parsed.path.startswith("/static/"):
            self._serve_static(parsed.path.removeprefix("/static/"))
            return
        write_json(self, 404, {"error": "Not found"})

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
            if self.path == "/api/analyze":
                result = WIZARD.analyze(
                    equipment_id=payload["equipment_id"],
                    query=payload.get("query", ""),
                    sensors=payload.get("sensors", {}),
                )
                write_json(self, 200, result)
                return
            if self.path == "/api/feedback":
                record = {
                    "timestamp": dt.datetime.now().isoformat(timespec="seconds"),
                    "feedback": payload,
                }
                with FEEDBACK_PATH.open("a", encoding="utf-8") as fp:
                    fp.write(json.dumps(record) + "\n")
                write_json(self, 200, {"status": "saved"})
                return
            write_json(self, 404, {"error": "Not found"})
        except Exception as exc:
            write_json(self, 400, {"error": str(exc)})

    def log_message(self, fmt: str, *args: Any) -> None:
        return

    def _serve_static(self, filename: str, content_type: str | None = None) -> None:
        path = STATIC_DIR / filename
        if not path.exists() or not path.is_file():
            write_json(self, 404, {"error": "Static file not found"})
            return
        content_type = content_type or (
            "text/css; charset=utf-8" if path.suffix == ".css" else "application/javascript; charset=utf-8"
        )
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run_server(host: str, port: int) -> None:
    server = ThreadingHTTPServer((host, port), WizardHandler)
    print(f"Maintenance Wizard running at http://{host}:{port}")
    print("Press Ctrl+C to stop.")
    server.serve_forever()


def run_cli(args: argparse.Namespace) -> None:
    sensors = parse_sensors(args.sensors)
    result = WIZARD.analyze(args.equipment, args.query, sensors)
    print(result["report"])
    if args.json:
        print("\nFull JSON:")
        print(json.dumps(result, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Agentic AI Maintenance Wizard prototype")
    sub = parser.add_subparsers(dest="command")
    serve = sub.add_parser("serve", help="Start browser-based prototype")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", default=8000, type=int)
    analyze = sub.add_parser("analyze", help="Run a CLI diagnosis")
    analyze.add_argument("--equipment", required=True, help="Equipment ID, e.g. RM-MTR-01")
    analyze.add_argument("--query", required=True, help="Engineer fault description")
    analyze.add_argument("--sensors", default="{}", help='JSON object, e.g. "{\"temperature_c\":91}"')
    analyze.add_argument("--json", action="store_true", help="Print full JSON output")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "serve":
        run_server(args.host, args.port)
    elif args.command == "analyze":
        run_cli(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
