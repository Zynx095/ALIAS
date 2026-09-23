#!/usr/bin/env python3
"""
ALIAS — Demo Scenario Data Generator Script

Generates deterministic scenario data derived from the identity log reference schema.
Produces human-readable CSV and JSONL preview fixtures for all 6 ALIAS investigation scenarios.
"""
import os
import json
import csv
from datetime import datetime, timedelta

SCENARIO_METADATA = [
    {
        "scenario_id": "normal_login",
        "name": "Scenario 1 — Normal Login",
        "description": "Establish the baseline/control case. Known user, device, location, and routine business hours.",
        "purpose": "Demonstrate normal behavior with no meaningful deviation.",
        "source": "SCENARIO",
        "users": ["demo_sarah"],
        "event_count": 11,
        "target_event_id": "alias-demo-normal-001",
        "expected_anomalies": [],
        "expected_risk": 0.0,
        "expected_severity": "LOW",
        "expected_investigation": False,
        "dataset_reference": "Screenshot 1 (Identity Log) — Routine single-user sequence"
    },
    {
        "scenario_id": "new_device",
        "name": "Scenario 2 — New Device",
        "description": "Known user, location, and network route. Previously unseen device fingerprint.",
        "purpose": "Isolate device novelty detection while location, IP, and timing remain normal.",
        "source": "SCENARIO",
        "users": ["demo_david"],
        "event_count": 11,
        "target_event_id": "alias-demo-new-device-001",
        "expected_anomalies": ["NEW_DEVICE"],
        "expected_risk": 15.0,
        "expected_severity": "LOW",
        "expected_investigation": True,
        "dataset_reference": "Screenshot 1 (Identity Log) — Device/OS tuple change"
    },
    {
        "scenario_id": "impossible_travel",
        "name": "Scenario 3 — Impossible Travel",
        "description": "Two chronologically adjacent logins with physically impossible geographic velocity.",
        "purpose": "Trigger geographic velocity anomaly between distant locations in short elapsed time.",
        "source": "SCENARIO",
        "users": ["demo_traveler"],
        "event_count": 12,
        "target_event_id": "alias-demo-impossible-travel-002",
        "expected_anomalies": ["IMPOSSIBLE_TRAVEL"],
        "expected_risk": 40.0,
        "expected_severity": "MODERATE",
        "expected_investigation": True,
        "dataset_reference": "Screenshot 1 (Identity Log) + Screenshot 2 (Graph sequence transition)"
    },
    {
        "scenario_id": "auth_burst",
        "name": "Scenario 4 — Authentication Burst",
        "description": "Multiple failed authentication attempts immediately preceding a successful login.",
        "purpose": "Demonstrate brute-force / credential stuffing detection before access.",
        "source": "SCENARIO",
        "users": ["demo_admin"],
        "event_count": 15,
        "target_event_id": "alias-demo-auth-burst-001",
        "expected_anomalies": ["BRUTE_FORCE"],
        "expected_risk": 45.0,
        "expected_severity": "MODERATE",
        "expected_investigation": True,
        "dataset_reference": "Screenshot 3 (IdP Audit) — Challenge & failure sequence"
    },
    {
        "scenario_id": "multi_signal",
        "name": "Scenario 5 — Multi-Signal Compromise",
        "description": "Unseen device + new location + off-hours timing + TOR anonymizing proxy + auth burst.",
        "purpose": "Primary showcase demonstrating correlation across 5 independent behavioral signals.",
        "source": "SCENARIO",
        "users": ["demo_ceo"],
        "event_count": 11,
        "target_event_id": "alias-demo-multi-signal-001",
        "expected_anomalies": ["NEW_DEVICE", "IMPOSSIBLE_TRAVEL", "UNSEEN_IP", "OFF_HOURS", "ANONYMOUS_PROXY"],
        "expected_risk": 90.0,
        "expected_severity": "CRITICAL",
        "expected_investigation": True,
        "dataset_reference": "Screenshot 1 & 3 — Multi-attribute anomaly composite"
    },
    {
        "scenario_id": "unseen_network",
        "name": "Scenario 6 — Unseen Network & Proxy",
        "description": "Corporate VPN user logging in from an unannounced TOR proxy node from a new IP/subnet.",
        "purpose": "Validate network topology and anonymizing proxy routing anomaly detection.",
        "source": "SCENARIO",
        "users": ["demo_marcus"],
        "event_count": 11,
        "target_event_id": "alias-demo-unseen-network-001",
        "expected_anomalies": ["UNSEEN_IP", "ANONYMOUS_PROXY"],
        "expected_risk": 35.0,
        "expected_severity": "MODERATE",
        "expected_investigation": True,
        "dataset_reference": "Screenshot 1 & 3 — Proxy network transition"
    }
]

def generate_scenario_events():
    base_time = datetime(2026, 9, 23, 10, 0, 0)
    all_events = []

    # Scenario 1
    for i in range(10, 0, -1):
        all_events.append({
            "scenario_id": "normal_login",
            "source_event_id": f"alias-demo-hist-demo_sarah-{i:03d}",
            "user_id": "demo_sarah",
            "timestamp": (base_time - timedelta(days=i)).isoformat(),
            "ip_address": "104.28.1.1",
            "location": "London, UK",
            "latitude": 51.5074,
            "longitude": -0.1278,
            "device_fingerprint": "sarah-macbook-pro",
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "auth_status": "SUCCESS",
            "failed_attempts": 0,
            "access_pattern": "DIRECT",
            "source": "DEMO_HISTORY"
        })
    all_events.append({
        "scenario_id": "normal_login",
        "source_event_id": "alias-demo-normal-001",
        "user_id": "demo_sarah",
        "timestamp": base_time.isoformat(),
        "ip_address": "104.28.1.1",
        "location": "London, UK",
        "latitude": 51.5074,
        "longitude": -0.1278,
        "device_fingerprint": "sarah-macbook-pro",
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "auth_status": "SUCCESS",
        "failed_attempts": 0,
        "access_pattern": "DIRECT",
        "source": "SCENARIO"
    })

    # Scenario 2
    for i in range(10, 0, -1):
        all_events.append({
            "scenario_id": "new_device",
            "source_event_id": f"alias-demo-hist-demo_david-{i:03d}",
            "user_id": "demo_david",
            "timestamp": (base_time - timedelta(days=i)).isoformat(),
            "ip_address": "12.34.56.78",
            "location": "New York, US",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "device_fingerprint": "david-windows-10",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0",
            "auth_status": "SUCCESS",
            "failed_attempts": 0,
            "access_pattern": "DIRECT",
            "source": "DEMO_HISTORY"
        })
    all_events.append({
        "scenario_id": "new_device",
        "source_event_id": "alias-demo-new-device-001",
        "user_id": "demo_david",
        "timestamp": base_time.isoformat(),
        "ip_address": "12.34.56.78",
        "location": "New York, US",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "device_fingerprint": "david-linux-unknown",
        "user_agent": "curl/7.68.0",
        "auth_status": "SUCCESS",
        "failed_attempts": 0,
        "access_pattern": "DIRECT",
        "source": "SCENARIO"
    })

    # Scenario 3
    for i in range(10, 0, -1):
        all_events.append({
            "scenario_id": "impossible_travel",
            "source_event_id": f"alias-demo-hist-demo_traveler-{i:03d}",
            "user_id": "demo_traveler",
            "timestamp": (base_time - timedelta(days=i)).isoformat(),
            "ip_address": "115.114.1.1",
            "location": "Bengaluru, IN",
            "latitude": 12.9716,
            "longitude": 77.5946,
            "device_fingerprint": "traveler-phone",
            "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)",
            "auth_status": "SUCCESS",
            "failed_attempts": 0,
            "access_pattern": "DIRECT",
            "source": "DEMO_HISTORY"
        })
    all_events.append({
        "scenario_id": "impossible_travel",
        "source_event_id": "alias-demo-impossible-travel-001",
        "user_id": "demo_traveler",
        "timestamp": (base_time - timedelta(minutes=20)).isoformat(),
        "ip_address": "115.114.1.1",
        "location": "Bengaluru, IN",
        "latitude": 12.9716,
        "longitude": 77.5946,
        "device_fingerprint": "traveler-phone",
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)",
        "auth_status": "SUCCESS",
        "failed_attempts": 0,
        "access_pattern": "DIRECT",
        "source": "SCENARIO"
    })
    all_events.append({
        "scenario_id": "impossible_travel",
        "source_event_id": "alias-demo-impossible-travel-002",
        "user_id": "demo_traveler",
        "timestamp": base_time.isoformat(),
        "ip_address": "104.28.1.2",
        "location": "London, UK",
        "latitude": 51.5074,
        "longitude": -0.1278,
        "device_fingerprint": "traveler-phone",
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)",
        "auth_status": "SUCCESS",
        "failed_attempts": 0,
        "access_pattern": "DIRECT",
        "source": "SCENARIO"
    })

    # Scenario 4
    for i in range(10, 0, -1):
        all_events.append({
            "scenario_id": "auth_burst",
            "source_event_id": f"alias-demo-hist-demo_admin-{i:03d}",
            "user_id": "demo_admin",
            "timestamp": (base_time - timedelta(days=i)).isoformat(),
            "ip_address": "8.8.8.8",
            "location": "Mountain View, US",
            "latitude": 37.3861,
            "longitude": -122.0839,
            "device_fingerprint": "admin-workstation",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "auth_status": "SUCCESS",
            "failed_attempts": 0,
            "access_pattern": "VPN",
            "source": "DEMO_HISTORY"
        })
    for i in range(4):
        all_events.append({
            "scenario_id": "auth_burst",
            "source_event_id": f"alias-demo-auth-burst-fail-{i+1:03d}",
            "user_id": "demo_admin",
            "timestamp": (base_time - timedelta(minutes=5 - i)).isoformat(),
            "ip_address": "8.8.8.8",
            "location": "Mountain View, US",
            "latitude": 37.3861,
            "longitude": -122.0839,
            "device_fingerprint": "admin-workstation",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "auth_status": "FAILURE",
            "failed_attempts": i + 1,
            "access_pattern": "VPN",
            "source": "SCENARIO"
        })
    all_events.append({
        "scenario_id": "auth_burst",
        "source_event_id": "alias-demo-auth-burst-001",
        "user_id": "demo_admin",
        "timestamp": base_time.isoformat(),
        "ip_address": "8.8.8.8",
        "location": "Mountain View, US",
        "latitude": 37.3861,
        "longitude": -122.0839,
        "device_fingerprint": "admin-workstation",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "auth_status": "SUCCESS",
        "failed_attempts": 5,
        "access_pattern": "VPN",
        "source": "SCENARIO"
    })

    # Scenario 5
    for i in range(10, 0, -1):
        all_events.append({
            "scenario_id": "multi_signal",
            "source_event_id": f"alias-demo-hist-demo_ceo-{i:03d}",
            "user_id": "demo_ceo",
            "timestamp": (base_time - timedelta(days=i)).replace(hour=10).isoformat(),
            "ip_address": "9.9.9.9",
            "location": "Paris, FR",
            "latitude": 48.8566,
            "longitude": 2.3522,
            "device_fingerprint": "ceo-laptop",
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0)",
            "auth_status": "SUCCESS",
            "failed_attempts": 0,
            "access_pattern": "DIRECT",
            "source": "DEMO_HISTORY"
        })
    all_events.append({
        "scenario_id": "multi_signal",
        "source_event_id": "alias-demo-multi-signal-001",
        "user_id": "demo_ceo",
        "timestamp": base_time.replace(hour=3).isoformat(),
        "ip_address": "45.33.22.11",
        "location": "Moscow, RU",
        "latitude": 55.7558,
        "longitude": 37.6173,
        "device_fingerprint": "attacker-linux-box",
        "user_agent": "curl/7.81.0",
        "auth_status": "SUCCESS",
        "failed_attempts": 3,
        "access_pattern": "TOR",
        "source": "SCENARIO"
    })

    # Scenario 6
    for i in range(10, 0, -1):
        all_events.append({
            "scenario_id": "unseen_network",
            "source_event_id": f"alias-demo-hist-demo_marcus-{i:03d}",
            "user_id": "demo_marcus",
            "timestamp": (base_time - timedelta(days=i)).isoformat(),
            "ip_address": "198.51.100.45",
            "location": "Chicago, US",
            "latitude": 41.8781,
            "longitude": -87.6298,
            "device_fingerprint": "marcus-laptop",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/121.0.0.0",
            "auth_status": "SUCCESS",
            "failed_attempts": 0,
            "access_pattern": "VPN",
            "source": "DEMO_HISTORY"
        })
    all_events.append({
        "scenario_id": "unseen_network",
        "source_event_id": "alias-demo-unseen-network-001",
        "user_id": "demo_marcus",
        "timestamp": base_time.isoformat(),
        "ip_address": "185.220.101.5",
        "location": "Frankfurt, DE",
        "latitude": 50.1109,
        "longitude": 8.6821,
        "device_fingerprint": "marcus-laptop",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/121.0.0.0",
        "auth_status": "SUCCESS",
        "failed_attempts": 0,
        "access_pattern": "TOR",
        "source": "SCENARIO"
    })

    return all_events

def main():
    out_dir = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "fixtures")
    os.makedirs(out_dir, exist_ok=True)

    meta_path = os.path.join(out_dir, "scenario_metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(SCENARIO_METADATA, f, indent=2)

    events = generate_scenario_events()
    jsonl_path = os.path.join(out_dir, "scenarios.jsonl")
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for evt in events:
            f.write(json.dumps(evt) + "\n")

    csv_path = os.path.join(out_dir, "scenarios.csv")
    fieldnames = list(events[0].keys())
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(events)

    print(f"[ALIAS Generator] Successfully wrote scenario fixtures:")
    print(f"  - Metadata: {meta_path}")
    print(f"  - JSONL: {jsonl_path}")
    print(f"  - CSV: {csv_path}")
    print(f"  - Total scenario events: {len(events)}")

if __name__ == "__main__":
    main()
