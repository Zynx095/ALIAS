# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

**Primary: a SOC analyst triaging suspicious logins.** Their job has three steps: notice that something is happening, work out why a specific login is suspicious, and decide what to do about it. The product is designed around this analyst's workflow.

**Secondary: hackathon judges.** Judges see the product through a live demo of that same analyst workflow, driven from the Scenario Console. What they see must be the real workflow, not a separate marketing layer.

## Product Purpose

ALIAS (AI-assisted Login Anomaly Investigation System) analyzes authentication events and finds suspicious login behavior using several signals: IP and geolocation, device fingerprint, timing, failed-attempt bursts, and network type (VPN/TOR/proxy). It correlates those signals into one risk score and produces a readable investigation report with recommended actions.

Success means the analyst can go from "an alert fired" to "I understand the evidence and what to do next" without leaving the product. It also means a judge understands the value within the first minute of the demo.

## Positioning

**A deterministic pipeline detects; the AI only interprets.**

```
OBSERVED FACT → DETERMINISTIC FINDING → CORRELATED RISK → AI INTERPRETATION
```

Every finding traces back to a behavioral baseline model and a deterministic anomaly or correlation rule. The AI layer turns that evidence into a readable dossier. It never detects anything itself, never confirms a compromise, and never makes up a verdict or confidence score that the backend doesn't produce. Multi-signal correlation (several individually weak anomalies adding up to one account-takeover picture) is the climax of the demo.

## Operating Context

- Analysts work across three surfaces:
  - **Overview:** what is happening now (KPIs, live event stream, globe, Scenario Console)
  - **Investigation:** why this event is suspicious. Evidence arrives in stages: event → anomalies → risk → AI report.
  - **History:** past investigations
- Real-time updates arrive over WebSocket (`RISK_ASSESSMENT`, `ANOMALY_DETECTED`, `INVESTIGATION_REPORT`).
- The demo runs locally (FastAPI on :8000, Vite on :5173) through five deterministic scenarios: Normal Login, New Device, Impossible Travel, Authentication Burst, and Multi-Signal Compromise. Script: `docs/demo/runbook.md`.
- An optional Tauri v2 desktop wrapper exists. Its design language is still web.

## Capabilities and Constraints

- **Backend** (complete, 61/61 tests passing): FastAPI, SQLAlchemy, SQLite, and Pydantic v2. It has six behavioral baseline models (temporal, device, location, network, auth, access pattern), an anomaly engine, correlation and risk scoring, and an investigation engine.
- **AI provider:** Gemini or OpenAI, with an automatic deterministic mock fallback. The demo must work with no API key.
- **Frontend:** React 19, Vite, Tailwind CSS 4, shadcn/Radix, Lucide, framer-motion, and react-globe.gl. Navigation is a small History-API hook rather than a router library. Severity mapping has one source of truth in `frontend/src/lib/severity.js`.
- **Severity vocabulary:** LOW / MODERATE / HIGH / CRITICAL. Risk scores run from 0 to 100.
- **UI must match the real data:** it only shows fields that exist in the backend schemas. For example, the investigation report has `severity` and `summary`, not `verdict` or `confidence`. There are no fabricated rows or placeholder charts.
- **Open:** the hackathon problem statement and judging criteria haven't been recorded yet. The user is providing them.

## Brand Commitments

- **Name:** ALIAS, which stands for AI-assisted Login Anomaly Investigation System. "ShadowGuard" is the pre-rebrand name and only survives in the repo and folder names.
- **Voice:** forensic and evidence-first. Copy never overstates what the system knows. The AI's text is always labeled as interpretation.

## Evidence on Hand

- Five deterministic demo scenarios with verified outputs. For example, New Device consistently scores 15/100 LOW, and Multi-Signal Compromise scores 90+ CRITICAL. Script: `docs/demo/runbook.md`.
- Feature documentation: `docs/features/`
- Phase history: `docs/phases/`, `CHANGELOG.md`
- Sample presentation: `PPT SAMPLE.pptx`
- There are no real customers, deployments, testimonials, benchmarks, or production detection metrics. Don't invent any.

## Product Principles

1. **Evidence before interpretation.** Every AI statement must sit next to the deterministic findings it interprets, and must visibly come after them.
2. **Never overclaim.** No invented verdicts, confidence scores, compromise confirmations, or fake data, in either the UI or the copy.
3. **Correlation is the story.** One weak signal is noise. Several correlated signals make a case. Surfaces should make that build-up readable.
4. **The demo is the real workflow.** Judges watch an analyst's actual path through the product. Honest system states (running, completed, no anomalies) beat staged ones.
5. **Always demoable.** Every external dependency (the LLM, the WebSocket) has a working fallback or a clear state, so the flow never collapses mid-demo.
