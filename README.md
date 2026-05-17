# Platform / Infra Reliability Kit

🌐 **Live demo:** _coming soon — deploys to Hugging Face Spaces in Wave 3 rollout_

This artifact turns incident signals into a runbook draft and a service-boundary contract report. It is designed to be reused for platform, API, infrastructure, and reliability roles where clear operational thinking matters more than a large demo.

## Run

**Interactive (Streamlit) — recommended:**
```bash
pip install -r requirements.txt
streamlit run app.py
```
Pick a sample incident or build by signal selection. Generate. Three tabs (Runbook / Contract Report / Recommended Tests) with a streaming-text effect.

**CLI batch run:**
```bash
python3 runbook_generator.py
```
Refreshes `sample_runbook.md` and `contract_report.md`.

## What It Demonstrates In 30 Seconds

- Incident signals become concrete response steps rather than abstract observability talk.
- Reliability includes service-boundary contract confidence, not just uptime metrics.
- The outputs are short enough for a hiring manager to skim and specific enough for an engineer to respect.

## Company Hooks

| Company | Angle |
| --- | --- |
| Pinterest | Platform reliability, service ownership, incident follow-through. |
| Grafana | Observability-driven diagnosis and operational signal. |
| Microsoft | API boundary confidence and developer-platform reliability. |
| Amazon | Incident response, high-scale operational discipline, customer-impact reduction. |
| 1Password | API/platform ecosystem reliability and safe contract evolution. |
| OpenVPN | Network/service reliability and clear runbook communication. |
| Wealthsimple | CI/CD and platform confidence for developer experience. |
| Bosch | QA/reliability evidence for complex systems. |

## Outreach Hook

I built a small reliability artifact that turns incident signals into actionable runbooks and failure summaries. I thought it mapped well to the platform/reliability problems described in the role.
