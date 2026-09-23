# ALIAS Testing Documentation

ALIAS features a comprehensive test suite across three main levels:
- `tests/unit/`: Testing individual logic circuits (e.g. baseline comparisons, anomaly threshold detection, deterministic risk scoring).
- `tests/api/`: Testing the HTTP endpoints using FastAPI `TestClient`, checking idempotency, HTTP verbs, error structures, and response schemas.

## Running Tests

To run the full suite:
```bash
set PYTHONPATH=backend\app
pytest tests -v
```

## Canonical Integration Test
As of Phase 7, a comprehensive full-pipeline test resides in `tests/api/test_canonical_pipeline.py`.
This test simulates the end-to-end journey of an event:
1. Ingestion of raw telemetry
2. Idempotency checks
3. Extraction and Baseline alignment
4. Anomaly classification
5. Risk engine composite scoring
6. AI Investigation Report Generation

It validates that every single module connects safely via the synchronous/asynchronous data paths without breaking or producing inconsistent data structures.
