from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid

from schemas.ingestion import RawLoginEvent
from services.ingestion_service import IngestionService
from services.baseline_preparation_service import BaselinePreparationService

class ScenarioService:
    @staticmethod
    def get_available_scenarios() -> List[Dict[str, Any]]:
        return [
            {
                "scenario_id": "normal_login",
                "scenario_name": "Scenario 1 — Normal Login",
                "description": "Establish the baseline/control case. Known user, device, location, and routine business hours.",
                "expected_signals": [],
                "expected_anomalies": [],
                "expected_risk_range": "LOW",
                "expected_investigation": False,
                "events_generated": 11 # 10 history + 1 test
            },
            {
                "scenario_id": "new_device",
                "scenario_name": "Scenario 2 — New Device",
                "description": "Known user, location, and network route. Previously unseen device fingerprint.",
                "expected_signals": ["DEVICE"],
                "expected_anomalies": ["NEW_DEVICE"],
                "expected_risk_range": "LOW",
                "expected_investigation": True,
                "events_generated": 11
            },
            {
                "scenario_id": "impossible_travel",
                "scenario_name": "Scenario 3 — Impossible Travel",
                "description": "Two chronologically adjacent logins with physically impossible geographic velocity.",
                "expected_signals": ["LOCATION"],
                "expected_anomalies": ["IMPOSSIBLE_TRAVEL"],
                "expected_risk_range": "MODERATE",
                "expected_investigation": True,
                "events_generated": 12 # 10 history + 2 tests
            },
            {
                "scenario_id": "auth_burst",
                "scenario_name": "Scenario 4 — Authentication Burst",
                "description": "Multiple failed authentication attempts immediately preceding a successful login.",
                "expected_signals": ["AUTHENTICATION"],
                "expected_anomalies": ["BRUTE_FORCE"],
                "expected_risk_range": "MODERATE",
                "expected_investigation": True,
                "events_generated": 15 # 10 history + 4 fails + 1 success
            },
            {
                "scenario_id": "multi_signal",
                "scenario_name": "Scenario 5 — Multi-Signal Compromise",
                "description": "Unseen device + new location + off-hours timing + TOR anonymizing proxy + auth burst.",
                "expected_signals": ["DEVICE", "LOCATION", "NETWORK", "TEMPORAL", "AUTHENTICATION"],
                "expected_anomalies": ["NEW_DEVICE", "IMPOSSIBLE_TRAVEL", "UNSEEN_IP", "OFF_HOURS"],
                "expected_risk_range": "CRITICAL",
                "expected_investigation": True,
                "events_generated": 11
            },
            {
                "scenario_id": "unseen_network",
                "scenario_name": "Scenario 6 — Unseen Network & Proxy",
                "description": "Corporate VPN user logging in from an unannounced TOR proxy node from a new IP/subnet.",
                "expected_signals": ["NETWORK", "ACCESS_PATTERN"],
                "expected_anomalies": ["UNSEEN_IP", "ANONYMOUS_PROXY"],
                "expected_risk_range": "MODERATE",
                "expected_investigation": True,
                "events_generated": 11
            }
        ]

    @staticmethod
    def _create_history(db: Session, user_id: str, count: int, template: dict) -> None:
        """Inject historical events quietly to build baseline."""
        now = datetime.utcnow()
        for i in range(count, 0, -1):
            past_time = now - timedelta(days=i)
            evt = RawLoginEvent(user_id=user_id, **template)
            evt.timestamp = past_time
            evt.source = "DEMO_HISTORY"
            evt.source_event_id = f"alias-demo-hist-{user_id}-{i:03d}"
            IngestionService.ingest_single(db, evt)
            
        # Rebuild baseline after history
        BaselinePreparationService.prepare_baseline(db, user_id, days=30)

    @staticmethod
    def prepare_scenario(db: Session, scenario_id: str) -> Tuple[str, List[RawLoginEvent]]:
        """Returns (user_id, [test_events_to_execute])."""
        now = datetime.utcnow()
        
        if scenario_id == "normal_login":
            user_id = "demo_sarah"
            tmpl = {
                "ip_address": "104.28.1.1",
                "location": "London, UK",
                "latitude": 51.5074,
                "longitude": -0.1278,
                "device_fingerprint": "sarah-macbook-pro",
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "auth_status": "SUCCESS",
                "failed_attempts": 0,
                "access_pattern": "DIRECT"
            }
            ScenarioService._create_history(db, user_id, 10, tmpl)
            
            # 1 Test Event (normal)
            test_evt = RawLoginEvent(user_id=user_id, **tmpl)
            test_evt.source = "SCENARIO"
            test_evt.timestamp = now
            test_evt.source_event_id = f"alias-demo-normal-001"
            return user_id, [test_evt]
            
        elif scenario_id == "new_device":
            user_id = "demo_david"
            tmpl = {
                "ip_address": "12.34.56.78",
                "location": "New York, US",
                "latitude": 40.7128,
                "longitude": -74.0060,
                "device_fingerprint": "david-windows-10",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0",
                "auth_status": "SUCCESS",
                "failed_attempts": 0,
                "access_pattern": "DIRECT"
            }
            ScenarioService._create_history(db, user_id, 10, tmpl)
            
            # Test Event: Same IP/Location, new device
            test_evt = RawLoginEvent(user_id=user_id, **tmpl)
            test_evt.source = "SCENARIO"
            test_evt.timestamp = now
            test_evt.device_fingerprint = "david-linux-unknown"
            test_evt.user_agent = "curl/7.68.0"
            test_evt.source_event_id = f"alias-demo-new-device-001"
            return user_id, [test_evt]
            
        elif scenario_id == "impossible_travel":
            user_id = "demo_traveler"
            tmpl = {
                "ip_address": "115.114.1.1",
                "location": "Bengaluru, IN",
                "latitude": 12.9716,
                "longitude": 77.5946,
                "device_fingerprint": "traveler-phone",
                "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)",
                "auth_status": "SUCCESS",
                "failed_attempts": 0,
                "access_pattern": "DIRECT"
            }
            ScenarioService._create_history(db, user_id, 10, tmpl)
            
            # Event 1: Bengaluru at Now - 20 mins
            evt1 = RawLoginEvent(user_id=user_id, **tmpl)
            evt1.source = "SCENARIO"
            evt1.timestamp = now - timedelta(minutes=20)
            evt1.source_event_id = f"alias-demo-impossible-travel-001"
            
            # Event 2: London at Now
            evt2 = RawLoginEvent(user_id=user_id, **tmpl)
            evt2.source = "SCENARIO"
            evt2.timestamp = now
            evt2.ip_address = "104.28.1.2"
            evt2.location = "London, UK"
            evt2.latitude = 51.5074
            evt2.longitude = -0.1278
            evt2.source_event_id = f"alias-demo-impossible-travel-002"
            return user_id, [evt1, evt2]
            
        elif scenario_id == "auth_burst":
            user_id = "demo_admin"
            tmpl = {
                "ip_address": "8.8.8.8",
                "location": "Mountain View, US",
                "latitude": 37.3861,
                "longitude": -122.0839,
                "device_fingerprint": "admin-workstation",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "auth_status": "SUCCESS",
                "failed_attempts": 0,
                "access_pattern": "VPN"
            }
            ScenarioService._create_history(db, user_id, 10, tmpl)
            
            evts = []
            for i in range(4):
                evt = RawLoginEvent(user_id=user_id, **tmpl)
                evt.source = "SCENARIO"
                evt.timestamp = now - timedelta(minutes=5 - i)
                evt.auth_status = "FAILURE"
                evt.failed_attempts = i + 1
                evt.source_event_id = f"alias-demo-auth-burst-fail-{i+1:03d}"
                evts.append(evt)
                
            success_evt = RawLoginEvent(user_id=user_id, **tmpl)
            success_evt.source = "SCENARIO"
            success_evt.timestamp = now
            success_evt.auth_status = "SUCCESS"
            success_evt.failed_attempts = 5
            success_evt.source_event_id = f"alias-demo-auth-burst-001"
            evts.append(success_evt)
            return user_id, evts
            
        elif scenario_id == "multi_signal":
            user_id = "demo_ceo"
            tmpl = {
                "ip_address": "9.9.9.9",
                "location": "Paris, FR",
                "latitude": 48.8566,
                "longitude": 2.3522,
                "device_fingerprint": "ceo-laptop",
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0)",
                "auth_status": "SUCCESS",
                "failed_attempts": 0,
                "access_pattern": "DIRECT"
            }
            
            ScenarioService._create_history(db, user_id, 10, tmpl)
            
            # Update history timestamps to be 10:00 AM UTC
            from models.database import LoginEvent, UserBaseline
            for evt in db.query(LoginEvent).filter(LoginEvent.user_id == user_id).all():
                evt.timestamp = evt.timestamp.replace(hour=10)
            db.commit()
            BaselinePreparationService.prepare_baseline(db, user_id, days=30)
            
            # The attack event: 3 AM UTC
            attack_time = now.replace(hour=3)
            if attack_time > now:
                attack_time = attack_time - timedelta(days=1)
                
            test_evt = RawLoginEvent(user_id=user_id, **tmpl)
            test_evt.source = "SCENARIO"
            test_evt.timestamp = attack_time
            test_evt.ip_address = "45.33.22.11"
            test_evt.location = "Moscow, RU"
            test_evt.latitude = 55.7558
            test_evt.longitude = 37.6173
            test_evt.device_fingerprint = "attacker-linux-box"
            test_evt.user_agent = "curl/7.81.0"
            test_evt.auth_status = "SUCCESS"
            test_evt.failed_attempts = 3
            test_evt.access_pattern = "TOR"
            test_evt.source_event_id = f"alias-demo-multi-signal-001"
            
            return user_id, [test_evt]

        elif scenario_id == "unseen_network":
            user_id = "demo_marcus"
            tmpl = {
                "ip_address": "198.51.100.45",
                "location": "Chicago, US",
                "latitude": 41.8781,
                "longitude": -87.6298,
                "device_fingerprint": "marcus-laptop",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/121.0.0.0",
                "auth_status": "SUCCESS",
                "failed_attempts": 0,
                "access_pattern": "VPN"
            }
            ScenarioService._create_history(db, user_id, 10, tmpl)

            test_evt = RawLoginEvent(user_id=user_id, **tmpl)
            test_evt.source = "SCENARIO"
            test_evt.timestamp = now
            test_evt.ip_address = "185.220.101.5"
            test_evt.location = "Frankfurt, DE"
            test_evt.latitude = 50.1109
            test_evt.longitude = 8.6821
            test_evt.access_pattern = "TOR"
            test_evt.source_event_id = f"alias-demo-unseen-network-001"
            return user_id, [test_evt]
            
        else:
            raise ValueError(f"Unknown scenario ID: {scenario_id}")
