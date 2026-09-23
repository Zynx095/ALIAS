# ALIAS — Phase 9: Demo Scenarios & Attack Simulation

## Overview
Phase 9 establishes a deterministic scenario framework (ScenarioRunner) that natively runs through the production ingestion pipeline, allowing end-to-end demonstrations of the ALIAS system without manual input or external attack generation.

## Key Principles
1. **Production Pipeline:** Every scenario enters through the exact same POST /api/events/login ingestion path used by real logins.
2. **Determinism:** Synthetic baseline history (10 events) is generated prior to the test event to reliably trigger comparison models.
3. **No Short-circuiting:** Anomalies, risk scores, and investigations are generated *organically* by the pipeline based on the data, not hardcoded.
4. **LLM Restraint:** The LLM does not hallucinate attacks; it only explains the evidence produced by the deterministic security pipeline.

## Implementation Details
- **Backend Service:** ScenarioService handles baseline creation and triggering the specific payload.
- **WebSocket Broadcast:** The test event executes within a BackgroundTasks block, immediately populating the SOC dashboard in real-time.
- **Frontend Console:** A side-panel ScenarioConsole.jsx lists the scenarios with quick-run buttons.
- **Presentation Mode:** Triggering a demo sets the environment into "Demo Mode", highlighted by a warning banner in the MainLayout.

## Available Scenarios
1. **Normal Login:** Establishes the baseline/control case. No meaningful anomaly.
2. **New Device:** Single dimensional anomaly. A known user logs in from an unseen device footprint.
3. **Impossible Travel:** A login from a new country within minutes of a local login.
4. **Authentication Burst:** Multiple rapid, failed login attempts followed by a success.
5. **Multi-Signal Compromise:** A critical severity event simulating an offshore IP, unseen device, unusual hour, and irregular access pattern.

## Runbooks
Detailed scripts and talking points for each scenario are located in docs/demo/.