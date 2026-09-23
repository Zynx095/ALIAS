import pytest
import os
import json
from scripts.demo.generate_scenarios import generate_scenario_events, SCENARIO_METADATA

def test_scenario_metadata_structure():
    assert len(SCENARIO_METADATA) == 6
    ids = [s["scenario_id"] for s in SCENARIO_METADATA]
    assert "normal_login" in ids
    assert "new_device" in ids
    assert "impossible_travel" in ids
    assert "auth_burst" in ids
    assert "multi_signal" in ids
    assert "unseen_network" in ids

    for meta in SCENARIO_METADATA:
        assert "name" in meta
        assert "description" in meta
        assert "purpose" in meta
        assert meta["source"] == "SCENARIO"
        assert meta["event_count"] > 0
        assert "target_event_id" in meta
        assert "expected_anomalies" in meta
        assert "expected_risk" in meta
        assert "expected_severity" in meta
        assert "dataset_reference" in meta

def test_generate_scenario_events_determinism():
    events = generate_scenario_events()
    assert len(events) == 71

    target_ids = [e["source_event_id"] for e in events if e["source"] == "SCENARIO"]
    assert "alias-demo-normal-001" in target_ids
    assert "alias-demo-new-device-001" in target_ids
    assert "alias-demo-impossible-travel-001" in target_ids
    assert "alias-demo-impossible-travel-002" in target_ids
    assert "alias-demo-auth-burst-001" in target_ids
    assert "alias-demo-multi-signal-001" in target_ids
    assert "alias-demo-unseen-network-001" in target_ids

def test_fixture_files_exist():
    out_dir = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "fixtures")
    assert os.path.exists(os.path.join(out_dir, "scenario_metadata.json"))
    assert os.path.exists(os.path.join(out_dir, "scenarios.jsonl"))
    assert os.path.exists(os.path.join(out_dir, "scenarios.csv"))
