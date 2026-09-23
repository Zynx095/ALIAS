import sys
import os
import requests
import uuid
import time

API_URL = "http://localhost:8000/api/events/login"

def trigger():
    print("Triggering synthetic login for ALIAS E2E Demonstration...")
    
    run_id = str(uuid.uuid4())[:8]
    payload = {
        "user_id": f"synthetic_attacker_{run_id}",
        "ip_address": "192.168.1.100",  # Triggers network anomaly if baseline empty
        "location": "Moscow, RU",      # Triggers location anomaly
        "latitude": 55.7558,
        "longitude": 37.6173,
        "device_fingerprint": "kali-linux-unknown-browser",
        "user_agent": "curl/7.68.0",   # Triggers device anomaly
        "auth_status": "SUCCESS",
        "failed_attempts": 5,          # Triggers brute force anomaly
        "access_pattern": "VPN",
        "source_event_id": f"src_demo_{run_id}",
        "source": "E2E_DEMO"
    }

    print(f"📡 Sending payload to {API_URL}")
    try:
        response = requests.post(API_URL, json=payload, timeout=5)
        response.raise_for_status()
        data = response.json()
        print(f"✅ Success! Ingested as Event ID: {data.get('event_id')}")
        print("👀 Check your SOC Dashboard. You should see:")
        print("  1. LOGIN_EVENT arrive")
        print("  2. BEHAVIORAL_COMPARISON evaluate")
        print("  3. ANOMALY_DETECTED trigger")
        print("  4. RISK_ASSESSMENT escalate")
        print("  5. INVESTIGATION_REPORT generate")
    except Exception as e:
        print(f"❌ Failed to trigger login: {e}")
        print("Is the backend running on port 8000?")

if __name__ == "__main__":
    trigger()
