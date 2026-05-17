"""Streamlit app for the Incident Runbook Toolkit.

Given a multi-select of incident signals, generates a runbook draft + contract report +
recommended tests, with a streaming-text effect that makes the generation feel AI-driven
(while remaining fully deterministic).
"""

from __future__ import annotations

import time
from pathlib import Path

import streamlit as st

from runbook_generator import (
    follow_up_actions,
    load_incidents,
    mitigation_steps,
    render_contract_report,
    render_runbook,
    specific_test,
    summarize_signals,
)

ROOT = Path(__file__).parent

st.set_page_config(
    page_title="Incident Runbook Toolkit — Isaac Maya",
    page_icon="🚨",
    layout="wide",
)

st.title("🚨 Incident Runbook Toolkit")
st.markdown(
    "**Turn incident signals into a runbook draft in under 10 seconds.**  \n"
    "_Built to demonstrate: SRE · Incident Commander · Platform Engineer_"
)

with st.expander("📖 Why this exists", expanded=True):
    st.markdown(
        """
Post-incident, the runbook gets written on Friday afternoon when energy is lowest. **This toolkit
produces a defensible first draft from signals alone** — so human energy goes into reviewing,
not starting from a blank page.

Runbook generation is deterministic (no LLM hallucinations), but the streaming output is intentional:
the format matches what an on-call engineer would actually skim — first 10 minutes, incident-specific
guidance, mitigation steps, follow-up actions, and contract-test recommendations.
"""
    )

with st.expander("🎯 What you're looking at"):
    st.markdown(
        """
- ✅ Signal-driven runbook generation — deterministic, audit-friendly
- ✅ Service-boundary contract report (who-owns-what when this fires)
- ✅ Incident-specific test recommendations to prevent recurrence
- ✅ First-10-minutes section that matches actual on-call workflow
- ✅ Streaming-text generation effect (feels AI-driven; doesn't hallucinate)
"""
    )

incidents = load_incidents()
incident_by_id = {i["incident_id"]: i for i in incidents}
all_signals = sorted({s for i in incidents for s in i["signals"]})

st.divider()
st.header("🧪 Try it")

mode = st.radio(
    "Pick a workflow",
    options=["Use a sample incident", "Build by signal selection"],
    horizontal=True,
)

if mode == "Use a sample incident":
    pick = st.selectbox("Pick an incident", options=list(incident_by_id.keys()),
                         format_func=lambda i: f"{i} — {incident_by_id[i]['service']} ({incident_by_id[i]['symptom']})")
    selected_incidents = [incident_by_id[pick]]
else:
    chosen = st.multiselect("Pick the signals firing right now", options=all_signals,
                              default=["dependency_timeout"])
    if chosen:
        candidates = [i for i in incidents if set(i["signals"]) & set(chosen)]
        selected_incidents = candidates or [incidents[0]]
        st.caption(f"Matched {len(selected_incidents)} sample incident(s) based on overlapping signals.")
    else:
        selected_incidents = []
        st.warning("Pick at least one signal to generate.")

speed = st.slider("Stream speed (delay per chunk, seconds)", 0.0, 0.5, 0.05, 0.05)

if selected_incidents and st.button("✨ Generate", type="primary", use_container_width=True):
    runbook_text = render_runbook(selected_incidents)
    contract_text = render_contract_report(selected_incidents)
    test_lines = [
        f"- **{i['incident_id']}** (`{i['service']}`) → {specific_test(i)}"
        for i in selected_incidents
    ]

    tab1, tab2, tab3 = st.tabs(["📋 Runbook", "📜 Contract Report", "🧪 Recommended Tests"])

    def stream_into(placeholder, text: str, chunk_size: int = 20):
        """Word-batch streaming effect — faster than per-character, less janky."""
        words = text.split(" ")
        rendered = []
        for i in range(0, len(words), chunk_size):
            rendered.extend(words[i : i + chunk_size])
            placeholder.markdown(" ".join(rendered))
            if speed > 0:
                time.sleep(speed)

    with tab1:
        p = st.empty()
        stream_into(p, runbook_text)
    with tab2:
        p = st.empty()
        stream_into(p, contract_text)
    with tab3:
        st.subheader("Tests to add — prevent recurrence")
        for line in test_lines:
            st.markdown(line)
        st.caption("Each test is derived from the incident's contract failure or signal pattern, not from a fixed checklist.")

st.divider()
with st.expander("🧪 How to test it (guided tour)", expanded=True):
    st.markdown(
        """
**Step 1 — Run with the default sample.** Pick `INC-2401` (auth-api latency spike). Generate. Read the
First 10 Minutes section — that's the boilerplate every incident gets. Read the Incident-Specific
Guidance — that part adapts to *this* incident's signals.

**Step 2 — Switch to signal mode.** Select `queue_lag` + `schema_mismatch`. Watch the matched incident
shift to `INC-2402` (billing-events). The recommended test changes — schema registry compatibility
check appears.

**Step 3 — Mix signals across incidents.** Select `dependency_timeout` + `schema_mismatch`. Both
incidents match. Generate. Runbook now contains both — and the contract report shows two boundary
failures with separate recommended tests.

**Step 4 — Tune stream speed.** Set to 0s for instant output, or 0.3s for a "watching it write" feel.
This is cosmetic, but the streaming effect lets you talk through the runbook with a stakeholder live.

**Step 5 — Read the contract report.** This is the second-order artifact. The runbook handles *this*
incident; the contract report makes *the next one* less likely.
"""
    )

with st.expander("💼 What this proves about me"):
    st.markdown(
        """
**For SRE roles:** I treat runbooks as software, not documents. Signal-driven generation means the
runbook stays current as the system evolves — no stale wikis.

**For Incident Commander roles:** I produce drafts the team can improve, not solo prose. The first 10
minutes section is intentionally generic; the incident-specific section adapts to the actual signals.

**For Platform Engineer roles:** Contract reports surface ownership gaps before they become next
week's incident. Every recommended test is derived from a real boundary failure in the sample data.

---

**Isaac Maya** — QA · Agentic AI · Data Quality  \n
📧 theisaacmaya@icloud.com · 💼 [LinkedIn](https://linkedin.com/in/isaac-maya) · 🔗 [Source](https://github.com/isaac-maya/incident-runbook-toolkit) · 📝 [Essays](https://isaac-maya.github.io/essays/)
"""
    )
