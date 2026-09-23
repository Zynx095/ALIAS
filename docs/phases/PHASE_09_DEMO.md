# Phase 9: Demo Scenarios

## Phase Metadata
- **Phase ID:** 9
- **Phase Name:** Demo Scenarios
- **Status:** NOT STARTED
- **Started:** —
- **Completed:** —
- **Prerequisites:** Phase 6, Phase 8

---

## 1. Objective & Intended Responsibility
Phase 9 constructs reproducible, scripted attack and anomaly scenarios designed to demonstrate the end-to-end detection and AI investigation capabilities of ALIAS for stakeholders and evaluations.

### Scope of Responsibility:
1. **Scenario 1: Impossible Travel Attack:**
   - User `alice.smith@example.com` logs in successfully from New York, USA.
   - 15 minutes later, an authentication occurs from Moscow, Russia.
   - Demonstrates: Haversine distance detection, impossible velocity alert (>3,000 km/h), high risk score, and real-time map vector display.
2. **Scenario 2: Distributed Credential Stuffing / Password Spray:**
   - 100 failed authentication events across 20 user accounts originating from a rotating proxy pool within 2 minutes, culminating in 1 successful login.
   - Demonstrates: Brute force detector, time-window correlation, critical severity escalation, and prompt generation of an AI investigation report.
3. **Scenario 3: Executive Account Off-Hours Privilege Abuse:**
   - Chief Financial Officer credentials used at 3:15 AM from an unknown mobile device and atypical ISP to access sensitive resources.
   - Demonstrates: Temporal anomaly detection, device fingerprint novelty, and AI-assisted mitigation recommendation.
4. **Scenario Execution CLI:**
   - Implement `scripts/run_demo.py` allowing one-click automated execution of scenarios with real-time CLI status and live dashboard updates.

---

## 2. Key Deliverables
- `scripts/run_demo.py` demo runner utility.
- Pre-scripted scenario datasets.
- Demonstration guide with expected outcomes and verification points.
