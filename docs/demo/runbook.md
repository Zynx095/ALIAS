# ALIAS Demo Runbook

## R8 Note (2026-09-23)
The Scenario Console's "Completed"/"Open Investigation" state now reflects the real backend pipeline (via WebSocket), not just HTTP acceptance. Expect a short "Running" period (a few seconds) after clicking Run, proportional to actual anomaly/risk/investigation processing — this is real work happening, not a delay to fake. See `CHANGELOG.md` [R8] for details.

## Setup Checklist
1. Start Backend: `cd backend && python -m uvicorn app.main:app --reload`
2. Start Frontend: `cd frontend && npm run dev`
3. Optional: Set `LLM_PROVIDER=google` in `.env` to enable real Gemini investigations.
4. Open the ALIAS SOC Dashboard at `http://localhost:5173`.

## Demo Flow

### Scenario 1: Normal Login (Baseline)
**Action:** Click "Normal Login" in the Demo Console.
**Talking Points:**
- The system ingests a normal login for Sarah.
- It compares against her behavioral baseline.
- No anomalies are generated. The Risk Engine returns a 0/LOW score.
- The SOC dashboard updates but does not flag the event as an alert.

### Scenario 2: New Device
**Action:** Click "New Device" in the Demo Console.
**Talking Points:**
- Shows ALIAS can detect deterministic signature mismatches.
- A legitimate user logs in from a device hash they've never used before.
- Risk Score: **15/100, LOW** (verified live 2026-09-23, deterministic across a reset+rerun — a single DEVICE anomaly, base weight 15, no correlation modifiers). Does not trigger a full lockdown because people buy new phones.

### Scenario 3: Impossible Travel
**Action:** Click "Impossible Travel" in the Demo Console.
**Talking Points:**
- Sarah logged in from New York, and 10 minutes later, logs in from Tokyo.
- The Location Behavior Model mathematically calculates the distance and time delta to flag it as physically impossible.
- Risk Score: High.

### Scenario 4: Authentication Burst
**Action:** Click "Authentication Burst" in the Demo Console.
**Talking Points:**
- Simulates a brute-force or credential stuffing attack.
- 5 rapid failures followed by a success.
- The Access Pattern Model detects the high failure ratio and temporal density.
- Risk Score: High.

### Scenario 5: Multi-Signal Compromise (The Climax)
**Action:** Click "Multi-Signal Compromise" in the Demo Console.
**Talking Points:**
- This is where ALIAS shines: Multi-Signal Correlation.
- The login occurs at 3:00 AM (Temporal Anomaly) from an offshore IP (Network Anomaly) on an unknown device (Device Anomaly) using a headless browser (Authentication Anomaly).
- The Correlation Engine aggregates these isolated anomalies into a single high-confidence 'Account Takeover' attack vector.
- The LLM Investigation Engine compiles the evidence into a forensic dossier.
- Risk Score: Critical (90+).
