"""Generate a concise runbook and contract report from incident signals."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).parent
INCIDENTS_PATH = ROOT / "incident_samples.json"
RUNBOOK_PATH = ROOT / "sample_runbook.md"
CONTRACT_PATH = ROOT / "contract_report.md"


def load_incidents() -> list[dict]:
    return json.loads(INCIDENTS_PATH.read_text(encoding="utf-8"))


def summarize_signals(incidents: list[dict]) -> str:
    signal_counts: dict[str, int] = {}
    for incident in incidents:
        for signal in incident["signals"]:
            signal_counts[signal] = signal_counts.get(signal, 0) + 1
    ranked = sorted(signal_counts.items(), key=lambda item: (-item[1], item[0]))
    return ", ".join(f"`{signal}` ({count})" for signal, count in ranked)


def mitigation_steps(incident: dict) -> list[str]:
    steps = [
        "Keep the incident open until error rate and latency remain below threshold for 30 minutes.",
    ]
    contract_failure = incident["contract_failure"].lower()
    signals = set(incident["signals"])
    if "expires_at" in contract_failure:
        steps.insert(0, "Enable a temporary fallback for missing `expires_at` values while downstream consumers are protected.")
    if "schema" in contract_failure or "schema_mismatch" in signals:
        steps.insert(0, "Pin consumers to the last known-good schema and block incompatible producer deploys.")
    if "retry_storm" in signals or "dependency_timeout" in signals:
        steps.insert(0, "Reduce retry pressure with exponential backoff and rate limits on the affected callers.")
    return [f"{index}. {step}" for index, step in enumerate(steps, start=1)]


def follow_up_actions(incident: dict) -> list[str]:
    actions = [
        "Review whether retry behavior amplified the incident and document the new guardrail.",
    ]
    contract_failure = incident["contract_failure"].lower()
    signals = set(incident["signals"])
    if "expires_at" in contract_failure:
        actions.insert(0, "Add a contract test that fails when token refresh responses omit `expires_at`.")
    if "schema" in contract_failure or "schema_mismatch" in signals:
        actions.insert(0, "Add schema compatibility checks in CI for producer and consumer event payloads.")
    if "queue_lag" in signals:
        actions.insert(0, "Add alert tuning for queue lag so operators see backlog growth before customer impact widens.")
    if "dependency_timeout" in signals:
        actions.insert(0, "Annotate dependency timeout spikes on the service dashboard to speed up triage.")
    return [f"- {action}" for action in actions]


def render_runbook(incidents: list[dict]) -> str:
    lines = [
        "# Sample Reliability Runbook",
        "",
        "## Sendable Summary",
        "",
        "This sample shows how incident response and contract confidence can be tied together. The runbook is intentionally compact: a hiring manager can skim the structure quickly, while an engineer can still see the operational reasoning and follow-up guardrails.",
        "",
        f"Incidents analyzed: {len(incidents)}",
        f"Shared signals: {summarize_signals(incidents)}",
        "",
        "## First 10 Minutes",
        "",
        "1. Confirm user impact through latency, error-rate, and dependency dashboards.",
        "2. Freeze non-essential deploys for every affected service.",
        "3. Assign incident commander, comms owner, and dependency owner.",
        "4. Capture current contract failures before restarting services or replaying traffic.",
        "",
        "## Incident-Specific Guidance",
        "",
    ]
    for incident in incidents:
        lines.extend([
            f"### {incident['incident_id']} — `{incident['service']}`",
            "",
            f"Severity: {incident['severity'].upper()}",
            f"Symptom: {incident['symptom']}",
            f"Signals: {', '.join(incident['signals'])}",
            f"Suspected dependency: `{incident['suspected_dependency']}`",
            f"Boundary failure: {incident['contract_failure']}",
            "",
            "Mitigation",
            "",
            *mitigation_steps(incident),
            "",
            "Follow-up",
            "",
            *follow_up_actions(incident),
            "",
        ])
    return "\n".join(lines)


def specific_test(incident: dict) -> str:
    failure = incident["contract_failure"].lower()
    signals = set(incident["signals"])
    if "expires_at" in failure or "token" in failure or "auth" in incident["service"].lower():
        return "contract test asserting required auth response fields are always present"
    if "schema" in failure or "schema_mismatch" in signals:
        return "schema registry compatibility check blocking incompatible producer deploys"
    if "queue_lag" in signals or "retry_storm" in signals:
        return "consumer lag alert threshold test plus retry-storm regression case"
    return "consumer contract test plus schema validation in CI"

def render_contract_report(incidents: list[dict]) -> str:
    lines = [
        "# API / Service Contract Report",
        "",
        "This companion report captures the boundary failures that should become automated checks, so the next incident is less likely to escape into downstream systems.",
        "",
        "| Incident | Service | Boundary failure | Recommended test |",
        "| --- | --- | --- | --- |",
    ]
    for incident in incidents:
        test = specific_test(incident)
        lines.append(f"| {incident['incident_id']} | {incident['service']} | {incident['contract_failure']} | {test} |")
    lines.extend([
        "",
        "## Takeaway",
        "",
        "The recurring reliability risk is not only service health; it is weak contract confidence at system boundaries. The fix is to pair incident runbooks with automated contract checks that fail before downstream teams discover drift.",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    incidents = load_incidents()
    RUNBOOK_PATH.write_text(render_runbook(incidents), encoding="utf-8")
    CONTRACT_PATH.write_text(render_contract_report(incidents), encoding="utf-8")
    print(f"Generated runbook and contract report from {len(incidents)} incidents.")


if __name__ == "__main__":
    main()
