# ALIAS — Reference-Based Demo Scenario System

## 1. Overview & Positioning

The ALIAS Demo Scenario System provides clean, deterministic, reproducible security telemetry derived from reference identity log structures (see Section 2). 

### Key Principles:
* **Simulated Telemetry:** Demo data is synthetic and engineered to exercise specific threat patterns. It is **not** raw production incident data.
* **Deterministic Pipeline Execution:** Scenario events pass directly through ALIAS's production ingestion pipeline (`RawLoginEvent` $\rightarrow$ Baseline Comparison $\rightarrow$ Anomaly Detection $\rightarrow$ Multi-Signal Correlation $\rightarrow$ Deterministic Risk Scoring $\rightarrow$ AI Forensic Narration).
* **Zero Hard-Coded Outcomes:** Risk scores, severities, anomaly classifications, and AI summaries are calculated dynamically by the backend engines.
* **Reproducible & Idempotent:** Event IDs (`alias-demo-*`) and baseline generators ensure identical evaluation results across test runs.

---

## 2. Reference Dataset Schema Mapping

The demo data schema directly aligns with identity and authentication log fields observed in enterprise security exports (e.g., identity log tabular dumps and SSO audit streams):

| Source Reference Field | ALIAS `RawLoginEvent` Field | Description / Transformation |
| :--- | :--- | :--- |
| `actor_email` / `User ID` / `user_hash` | `user_id` | Mapped to user identifier (e.g., `sarah.connors@acme.corp`, `demo_david`). |
| `IP Address` / `ip_address` | `ip_address` | IPv4/IPv6 client address. Subnets (`/24`) derived by backend normalization. |
| `Country` + `City` / `ip_country` + `ip_city` | `location` | Human-readable location string (`"{City}, {Country}"`). |
| Geographic Coordinates | `latitude`, `longitude` | Coordinates matching the resolved location for velocity calculations. |
| `User Agent` + `OS` + `Browser` | `user_agent` | Full client browser user agent string. |
| `Device Type` + Device MD5 / Fingerprint | `device_fingerprint` | Client hardware/browser fingerprint (e.g., `sarah-macbook-pro`). |
| `Login Time` / `event_time` | `timestamp` | ISO 8601 UTC timestamp. Hour/day/weekend derived by backend. |
| `Login Successful` / `event_name` | `auth_status` | `"SUCCESS"` or `"FAILURE"`. |
| Sequential failure counter | `failed_attempts` | Number of preceding failed authentication attempts in the window. |
| `login_type` / Routing channel | `access_pattern` | Traffic route: `"DIRECT"`, `"VPN"`, `"TOR"`, `"PROXY"`. |
| Log Index / Row ID | `source_event_id` | Deterministic tracking ID (e.g., `alias-demo-normal-001`). |
| System Origin | `source` | Set strictly to `"SCENARIO"`. |

---

## 3. Scenario Catalog

### **Scenario 1 — Normal Login (Control Case)**
* **ID:** `normal_login`
* **Target Event:** `alias-demo-normal-001`
* **User:** `demo_sarah` (`sarah.connors@acme.corp`)
* **Purpose:** Validate control behavior where user activity aligns completely with established business-hour baseline.
* **Baseline:** 10 days of business-hour logins from London, UK (`104.28.1.1`), device `sarah-macbook-pro`.
* **Test Event:** Login from London, UK using `sarah-macbook-pro` from `104.28.1.1`.
* **Expected Result:** Anomalies: `[]` | Risk: `0.0` | Severity: `LOW` | AI Investigation: None triggered.

---

### **Scenario 2 — New Device Anomaly**
* **ID:** `new_device`
* **Target Event:** `alias-demo-new-device-001`
* **User:** `demo_david` (`david.miller@acme.corp`)
* **Purpose:** Isolate device fingerprint novelty while location, IP, and access timing remain completely normal.
* **Baseline:** 10 days of logins from New York, US (`12.34.56.78`), device `david-windows-10`.
* **Test Event:** Login from New York, US (`12.34.56.78`), but with new device `david-linux-unknown` (`curl/7.68.0`).
* **Expected Result:** Anomalies: `["NEW_DEVICE"]` | Risk: `15.0` | Severity: `LOW` | AI Investigation: Explains isolated device novelty.

---

### **Scenario 3 — Impossible Travel**
* **ID:** `impossible_travel`
* **Target Events:** `alias-demo-impossible-travel-001`, `alias-demo-impossible-travel-002`
* **User:** `demo_traveler` (`alex.rivera@acme.corp`)
* **Purpose:** Demonstrate geographic velocity anomaly between distant logins in short elapsed time.
* **Baseline:** 10 days of logins from Bengaluru, IN (`115.114.1.1`).
* **Test Sequence:**
  1. `T - 20m`: Login from Bengaluru, IN (`115.114.1.1`).
  2. `T`: Login from London, UK (`104.28.1.2`).
* **Expected Result:** Anomalies: `["IMPOSSIBLE_TRAVEL"]` | Risk: `40.0` | Severity: `MODERATE` | AI Investigation: Outlines physical impossibility of velocity (~23,000 km/h).

---

### **Scenario 4 — Authentication Burst**
* **ID:** `auth_burst`
* **Target Event:** `alias-demo-auth-burst-001`
* **User:** `demo_admin` (`admin.ops@acme.corp`)
* **Purpose:** Detect rapid credential stuffing or brute-force failure attempts preceding access.
* **Baseline:** 10 successful logins from Mountain View, US (`8.8.8.8`).
* **Test Sequence:** 4 consecutive `FAILURE` events within 5 minutes followed by 1 `SUCCESS` (`failed_attempts=5`).
* **Expected Result:** Anomalies: `["BRUTE_FORCE"]` | Risk: `45.0` | Severity: `MODERATE` | AI Investigation: Identifies failed auth sequence preceding successful entry.

---

### **Scenario 5 — Multi-Signal Compromise (Showcase Scenario)**
* **ID:** `multi_signal`
* **Target Event:** `alias-demo-multi-signal-001`
* **User:** `demo_ceo` (`elena.rostova@acme.corp`)
* **Purpose:** Primary showcase correlating 5 independent behavioral signals into a high-risk finding.
* **Baseline:** 10 daytime (10:00 UTC) logins from Paris, FR (`9.9.9.9`), device `ceo-laptop`.
* **Test Event:**
  * Off-hours: 03:00 UTC
  * Location: Moscow, RU (`45.33.22.11`)
  * Device: Unseen `attacker-linux-box` (`curl/7.81.0`)
  * Route: `"TOR"` proxy
  * Auth: `failed_attempts=3`
* **Expected Result:** Anomalies: `["NEW_DEVICE"]`, `["IMPOSSIBLE_TRAVEL"]`, `["UNSEEN_IP"]`, `["OFF_HOURS"]`, `["ANONYMOUS_PROXY"]` | Risk: `90.0` | Severity: `CRITICAL` | AI Investigation: Comprehensive forensic breakdown.

---

### **Scenario 6 — Unseen Network & Proxy**
* **ID:** `unseen_network`
* **Target Event:** `alias-demo-unseen-network-001`
* **User:** `demo_marcus` (`marcus.vance@acme.corp`)
* **Purpose:** Validate network topology and anonymizing proxy routing anomaly detection independently of device fingerprinting.
* **Baseline:** 10 logins via corporate VPN (`198.51.100.45`, Chicago, US).
* **Test Event:** Login from an unannounced TOR exit node in Frankfurt, DE (`185.220.101.5`, `access_pattern="TOR"`) using known user device `marcus-laptop`.
* **Expected Result:** Anomalies: `["UNSEEN_IP"]`, `["ANONYMOUS_PROXY"]` | Risk: `35.0` | Severity: `MODERATE` | AI Investigation: Analyzes proxy route risk and subnet deviation.

---

## 4. Execution & Fixture Generation

### **1. Regenerating Preview Fixtures**
To generate clean CSV and JSONL preview fixtures in `docs/fixtures/`:

```bash
python scripts/demo/generate_scenarios.py
```

### **2. Running Scenarios via API**
Execute any scenario against a running ALIAS backend instance:

```bash
# Trigger Scenario 5 (Multi-Signal Compromise)
curl -X POST http://localhost:8000/api/scenarios/multi_signal/run

# Reset Demo Environment
curl -X POST http://localhost:8000/api/scenarios/reset
```

### **3. Running Scenarios via Frontend SOC Console**
Open the ALIAS SOC Dashboard Overview surface and select any scenario card in the **Demo Scenarios** console panel.
