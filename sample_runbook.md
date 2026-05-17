# Sample Reliability Runbook

## Sendable Summary

This sample shows how incident response and contract confidence can be tied together. The runbook is intentionally compact: a hiring manager can skim the structure quickly, while an engineer can still see the operational reasoning and follow-up guardrails.

Incidents analyzed: 2
Shared signals: `5xx_rate_3pct` (1), `dependency_timeout` (1), `latency_spike` (1), `queue_lag` (1), `retry_storm` (1), `schema_mismatch` (1)

## First 10 Minutes

1. Confirm user impact through latency, error-rate, and dependency dashboards.
2. Freeze non-essential deploys for every affected service.
3. Assign incident commander, comms owner, and dependency owner.
4. Capture current contract failures before restarting services or replaying traffic.

## Incident-Specific Guidance

### INC-2401 — `auth-api`

Severity: SEV2
Symptom: p95 latency above 1200ms
Signals: latency_spike, 5xx_rate_3pct, dependency_timeout
Suspected dependency: `session-store`
Boundary failure: token refresh response missing expires_at for 2.4% of calls

Mitigation

1. Reduce retry pressure with exponential backoff and rate limits on the affected callers.
2. Enable a temporary fallback for missing `expires_at` values while downstream consumers are protected.
3. Keep the incident open until error rate and latency remain below threshold for 30 minutes.

Follow-up

- Annotate dependency timeout spikes on the service dashboard to speed up triage.
- Add a contract test that fails when token refresh responses omit `expires_at`.
- Review whether retry behavior amplified the incident and document the new guardrail.

### INC-2402 — `billing-events`

Severity: SEV3
Symptom: consumer lag above threshold
Signals: queue_lag, schema_mismatch, retry_storm
Suspected dependency: `event-router`
Boundary failure: amount field changed from number to string in one producer

Mitigation

1. Reduce retry pressure with exponential backoff and rate limits on the affected callers.
2. Pin consumers to the last known-good schema and block incompatible producer deploys.
3. Keep the incident open until error rate and latency remain below threshold for 30 minutes.

Follow-up

- Add alert tuning for queue lag so operators see backlog growth before customer impact widens.
- Add schema compatibility checks in CI for producer and consumer event payloads.
- Review whether retry behavior amplified the incident and document the new guardrail.
