# ANTIGRAVITY HANDOFF — ALIAS

IMPORTANT: Before making any change, inspect the actual repository files. This document
describes the state as of 2026-09-23, end of a Claude Code session. The repo is the source
of truth for exact filenames, APIs, and implementation details — verify before acting on
anything below.

============================================================
1. WHAT ALIAS IS
============================================================

ALIAS = AI-assisted Login Anomaly Investigation System.

A deterministic security pipeline (behavioral baseline → anomaly detection → multi-signal
correlation → risk scoring) feeds an AI investigation layer that interprets — never
independently detects — the evidence. The core product philosophy, enforced throughout the
UI and backend:

```
OBSERVED FACT  →  DETERMINISTIC FINDING  →  CORRELATED RISK  →  AI INTERPRETATION
```

The AI must never be allowed to imply it detected something, confirmed compromise, or
invented a verdict/confidence score that doesn't exist in the backend schema.

============================================================
2. CURRENT STATUS
============================================================

- **Backend**: Complete, stable, validated. 61/61 pytest tests passing (3 repeated runs
  confirmed deterministic, no cross-test isolation issues). NOT modified in any of the work
  described below — every phase below was explicitly frontend-only.
- **Frontend**: Mid UI/UX refresh, phases R0 through R8.1 complete. R9 (full visual overhaul)
  and R10 (responsive/accessibility pass) have **not** started.
- **Git**: HEAD is `889bfe0 feat: complete ALIAS MVP`. All work described below is
  **uncommitted** — nothing since R6/R7/R8/R8.1 has been committed. Run `git status` first.
- **Known pre-existing issue, not fixed**: `npx vitest run` fails with
  `ReferenceError: expect is not defined` — a `vite.config.js` `test.globals` config gap
  (unrelated to any of the work below, deliberately left untouched each time it was
  encountered, per explicit instruction each phase).
- **Known pre-existing, unexplained change**: `scripts/trigger_synthetic_login.py` shows a
  one-line modification (an emoji removed from a print statement) that no agent working on
  this repo made intentionally. Left untouched every time it was seen. Investigate before
  assuming it's safe to ignore or revert.

============================================================
3. WHAT WAS DONE (R0 → R8.1) — IN ORDER
============================================================

**R0 — Correctness fix.** `InvestigationDetail.jsx` was rendering `report.verdict` and
`report.confidence`, fields that don't exist on the real backend schema
(`InvestigationReportResponse` only has `severity`/`summary`). Fixed to use real fields.
Also fixed `correlation_factors[].factor` → `.name` (another real-field mismatch), and
removed a `Math.random()`-driven fake chart in the old Dashboard.

**R2 — Design tokens.** Consolidated `frontend/src/index.css` into one token system
("Signal Intelligence" direction): `--bg-primary/secondary`, `--surface`,
`--surface-elevated`, `--border`, text hierarchy, 4 severity colors (emerald/amber/
orange/red — LOW/MODERATE/HIGH/CRITICAL), one dedicated `--accent-ai` (indigo) reserved
exclusively for AI-interpretation UI. Removed unused legacy `.glass-panel`/`.neon-text`/
`.scanline` purple-neon utilities that predated this refresh.

**R3 — Component foundation.** Created `frontend/src/lib/severity.js` as the single
source of truth for severity→color mapping (was previously duplicated 3 times). Created
`frontend/src/components/ui/severity-badge.jsx` (`SeverityBadge`, `SeverityDot`,
`SeverityLegend`), built on the previously-unused shadcn `Badge` primitive.

**R4 — Shell + Dashboard.** Reworked `MainLayout.jsx` (sidebar/topbar, removed global
`font-mono`, removed a fake permanently-green "API status" indicator that had no real
health check behind it) and the dashboard grid hierarchy (KPIs → weighted 12-col grid:
LiveStream 6 / Globe 4 / Scenario Console 2).

**R5 — CyberGlobe.** Stopped default auto-rotation, made sizing responsive (was hardcoded
400×300px), added a severity legend, added selected-point highlighting + compact context
panel. (Some of this was later simplified in R7 — see below.)

**R6 — Information architecture.** This is the big one. Replaced the single-page
`Dashboard.jsx` (which crammed overview + investigation into one screen) with three real
surfaces, orchestrated by `App.jsx`:
- **Overview** (`pages/Overview.jsx`) — "what's happening now" — KPIs, LiveStream,
  CyberGlobe, ScenarioConsole.
- **Investigation** (`pages/InvestigationWorkspace.jsx`) — "why is this suspicious" — owns
  all four evidence-stage fetches (event/anomalies/risk/report) as independent progressive
  state machines, renders `InvestigationHeader` + `InvestigationDetail`.
- **History** (`pages/InvestigationHistory.jsx`) — real data from `GET /api/investigations`,
  no fabricated rows, no invented pagination.

Navigation: `hooks/useViewState.js` — a small, dependency-free URL-sync hook using the
native History API (`pushState`/`popstate`). **Not** a routing library — deliberately, per
explicit instruction to avoid adding React Router. Paths: `/dashboard`, `/investigations`,
`/investigations/:eventId`. Back-navigation is origin-aware: Overview→Investigation→Back
returns to Overview; History→Investigation→Back returns to History (tracked via an
in-memory `from` hint on the view-state object, not URL-encoded).

Also fixed a second real schema bug found during this pass: `InvestigationDetail.jsx` was
rendering `EVT-{event.event_id}`, but the real REST schema (`LoginEventDetail`) uses `id`,
not `event_id` (the WebSocket payload shape is genuinely different and does use
`event_id` — confirmed by reading both contracts, not assumed).

**R7 — Dead code cleanup.** Deleted (all confirmed zero live references via repo-wide grep
before deletion): `ThreatMap.jsx`, `InvestigationPanel.jsx`, `LoginEventFeed.jsx`,
`LoginTimeline.jsx`, `RiskOverview.jsx`, the entire `frontend/src/ShadowGuard/` legacy
scaffold (pre-rebrand orphan, 21 files), the old `pages/Dashboard.jsx`, a duplicate
`hooks/useWebSocket.js` (AlertContext already has its own, the hook was never imported
anywhere), `utils/constants.js` (zero importers). Removed the `recharts` npm dependency
(confirmed zero usage after R4's chart removal). Simplified `CyberGlobe.jsx` back down by
removing the R5 `selectedEventId`/highlight/context-panel logic once R6 made it
unreachable (nothing calls `CyberGlobe` with that prop anymore, since selecting a point now
navigates to the Investigation surface instead of showing inline context).

**R8 — Scenario Console hardening.** Found and fixed a real bug: `ScenarioConsole.jsx`
marked a scenario run "Completed" the instant `POST /api/scenarios/{id}/run` returned
HTTP 200 — but that endpoint always synchronously returns `status:"Running"` while the
actual pipeline continues via FastAPI `BackgroundTasks`. Traced the real backend broadcast
contract directly from `backend/app/api/events.py` (not assumed): `RISK_ASSESSMENT`
broadcasts unconditionally for every event; `ANOMALY_DETECTED` only when anomalies exist
(must never be waited on — some scenarios, e.g. Normal Login, legitimately produce none);
`INVESTIGATION_REPORT` only when `risk_score > 0`. Rewrote completion detection to watch
`AlertContext`'s real WebSocket pipeline state against that exact gate. Added
"Open Investigation" on completion, a genuine two-click Reset confirmation, and a
`clearStream()` on `AlertContext` so Reset actually clears the frontend's own accumulated
view (previously the backend was wiped but the UI kept showing already-deleted events).
Verified all 5 canonical scenarios against a **live running backend** with a real
WebSocket client (not just static review) — see the CHANGELOG `[R8]` entry for exact
observed lifecycles/risk scores.

**R8.1 — Targeted debug pass** (Impossible Travel reportedly hanging in the real
frontend). Could not reproduce the hang through the most realistic non-browser test
available: replayed the real captured multi-event WebSocket sequence through the exact
`AlertContext`/`ScenarioConsole` reducer logic in isolation (Node, not React) — confirmed
completion-detection resolves `true` at exactly the right moment. Found one real,
provable-by-construction gap during the audit (unproven to be the actual cause, but real):
`AlertContext`'s reconnect logic (`setTimeout(connect, 3000)` on WS close) has no message
backlog/replay — anything broadcast during a disconnect window is lost forever, and
nothing re-checks state afterward. Added a resync effect to `ScenarioConsole.jsx`: on
WebSocket reconnect, any run still "running" gets resynced via the same REST endpoints
`InvestigationWorkspace` already uses (`fetchEventRisk`/`fetchInvestigation`) — real
backend data, not a timer, not a guessed failure state. **Explicitly did not claim this
"fixes" the reported hang** — no browser access to confirm the original symptom is gone.

============================================================
4. CURRENT FRONTEND ARCHITECTURE (as it actually is now)
============================================================

```
frontend/src/
  App.jsx                          — top-level surface switch + navigation (useViewState)
  hooks/
    useViewState.js                — URL-sync, no routing library
  context/
    AlertContext.jsx               — single WebSocket connection, pipelineState/eventStream
  pages/
    Overview.jsx                   — "what's happening now"
    InvestigationWorkspace.jsx     — owns all evidence-stage fetching, progressive states
    InvestigationHistory.jsx       — GET /api/investigations, real data only
  layouts/
    MainLayout.jsx                 — sidebar, topbar, connection status
  components/
    CyberGlobe.jsx                 — responsive, no auto-rotate, severity-colored points
    soc/
      LiveStream.jsx
      ScenarioConsole.jsx          — real WebSocket-gated completion (see R8/R8.1)
      InvestigationHeader.jsx      — identity/back/risk header
      InvestigationDetail.jsx      — pure presentational, 4 evidence sections
      EvidenceSection.jsx          — shared loading/error/empty/success wrapper
    ui/
      severity-badge.jsx           — SeverityBadge / SeverityDot / SeverityLegend
      badge.jsx, button.jsx, card.jsx, table.jsx, tabs.jsx, ... (shadcn primitives —
        NOW actually used, were previously dead weight)
  lib/
    severity.js                    — SINGLE source of truth for severity colors
    utils.js                       — cn() helper
  services/
    api.js                         — all backend calls, incl. WebSocket factory
  index.css                        — the token system (see below)
```

Do **not** recreate `pages/Dashboard.jsx`, `hooks/useWebSocket.js`,
`utils/constants.js`, or the `ShadowGuard/` scaffold — all deliberately deleted, confirmed
dead. Do not re-introduce a second severity color mapping anywhere — `lib/severity.js` is
the only one, by design.

============================================================
5. DESIGN TOKENS (do not redesign without reading this)
============================================================

Direction name: **"Signal Intelligence."** Dark-only SOC console, no light/dark toggle.
Defined once in `:root` in `frontend/src/index.css` (not gated behind a `.dark` class,
since nothing ever toggles one).

- `--bg-primary`, `--bg-secondary`, `--surface`, `--surface-elevated`, `--border`
- `--text-primary`, `--text-secondary`, `--text-muted`
- Severity: `--severity-low` (emerald), `--severity-moderate` (amber),
  `--severity-high` (orange), `--severity-critical` (red) — meaning-bearing ONLY,
  never decorative.
- `--accent-ai` (indigo) — reserved exclusively for AI-interpretation UI. Must not leak
  into unrelated components (buttons, nav, generic highlights).
- Motion tokens: `--motion-fast/base/slow`.

These are also exposed as Tailwind utility classes via the `@theme inline` block (e.g.
`bg-surface`, `text-accent-ai`, `border-border`) — most components use these utilities
directly rather than raw CSS variables.

Legacy CSS that was deliberately removed and must **not** be reintroduced:
`.glass-panel`, `.glass-panel-hover`, `.neon-text`, `.scanline`, purple radial-gradient
`body` backgrounds, global `font-mono`.

============================================================
6. RULES THAT GOVERNED THIS ENTIRE REFRESH (keep following them)
============================================================

1. **Frontend-only, every phase.** Never touch backend algorithms, database models, API
   contracts, WebSocket message contracts, anomaly detection, baseline logic, correlation,
   risk scoring, or AI investigation logic without explicit authorization and a proven need.
2. **No fabricated data, ever.** No `Math.random()`, no fake metrics/percentages/trends, no
   invented confidence/verdict/attack-classification fields, no hardcoded "success" states
   standing in for real backend confirmation. If a value isn't available, show an honest
   unavailable/loading/empty state — never a placeholder pretending to be real.
3. **Evidence hierarchy is sacred.** Observed Fact / Deterministic Finding / Correlated
   Risk / AI Interpretation must remain visually and semantically distinct everywhere. The
   AI never gets credited with detecting anything — only interpreting what the
   deterministic pipeline already established.
4. **Verify schemas from source, don't assume.** Two real schema-mismatch bugs (verdict/
   confidence, event.id vs event_id) were found specifically by reading the actual backend
   Pydantic schemas and WebSocket broadcast code rather than trusting what the frontend
   already assumed.
5. **No routing library** was added — `useViewState.js`'s native History API approach was
   judged sufficient. Revisit only if a real deep-linking/SPA-fallback need arises in
   production hosting.
6. **Completion states must be evidence-based**, not timer-based. See R8/R8.1 — this was a
   real, fixed bug class. Any future "is this done yet" UI must derive from real backend
   signals (WebSocket or REST), never `setTimeout(..., 'completed')`.
7. Each phase stopped exactly where instructed and did not silently continue into the next
   phase's scope. R9 (full visual overhaul) and R10 (responsive/accessibility) are the
   next logical phases and have not been started.

============================================================
7. HOW TO RUN THIS PROJECT
============================================================

**Backend:**
```
cd backend/app
pip install fastapi uvicorn sqlalchemy pydantic python-dotenv passlib websockets python-multipart
python -m uvicorn main:app --reload
```
Runs at `http://localhost:8000`. Health check: `GET /health`. No `requirements.txt` exists
in the repo — the package list above was reconstructed from actual imports + the installed
environment; consider generating a real `requirements.txt` before wider distribution.

**Frontend:**
```
cd frontend
npm install
npm run dev
```
Runs at `http://localhost:5173`.

`.env` (copy from `.env.example`) works with defaults for local/demo use — no API key
required, AI investigation falls back to a deterministic `mock-fallback` provider when
`LLM_PROVIDER=none`.

**Demo scenarios** (via the Scenario Console in the UI, or `POST /api/scenarios/{id}/run`):
`normal_login`, `new_device`, `impossible_travel`, `auth_burst`, `multi_signal`. Verified
risk/severity baseline as of R8/R8.1 (deterministic given a fresh reset):

| Scenario | Risk | Severity |
|---|---|---|
| Normal Login | 0.0 | LOW |
| New Device | 15.0 | LOW |
| Impossible Travel | 40.0 | MODERATE |
| Auth Burst | 45.0 | MODERATE |
| Multi-Signal | 90.0 | CRITICAL |

If these values ever change without a corresponding, deliberate backend edit, that's a
regression worth investigating, not silently accepting.

============================================================
8. WHAT'S NOT DONE / KNOWN GAPS FOR THE NEXT AGENT
============================================================

- **R9 not started**: the full premium visual overhaul. Current token system
  ("Signal Intelligence") is the intended foundation for it — read section 5 before
  touching anything visual.
- **R10 not started**: full responsive/accessibility pass. Some responsive foundation
  exists (grid breakpoints in Overview) but it's not comprehensive.
- **No browser automation was available** during R6–R8.1. Every claim of "verified" in the
  CHANGELOG is backend/WebSocket-level verification via real running servers and real
  captured message replays — genuinely rigorous, but **the actual rendered React UI in a
  real browser has not been visually confirmed** for any of this work. This is the single
  biggest open risk. A real click-through (ideally via browser automation, or by the user)
  of all 5 scenarios end-to-end, plus the Overview→Investigation→Back and
  History→Investigation→Back navigation flows, should happen before treating this refresh
  as demo-ready.
- **Vitest is broken** (`ReferenceError: expect is not defined`, `vite.config.js` missing
  `test.globals: true`) — pre-existing, never fixed, explicitly left alone every time.
- **`scripts/trigger_synthetic_login.py`** has an unexplained one-line change (see section
  2) — not investigated, not reverted.
- **The Impossible Travel reconnect-resync fix (R8.1) is unproven** against the actual
  reported symptom — it closes a real gap but the original hang was never reproduced to
  confirm the fix addresses it.
- Nothing described in this document has been committed to git. `git status` and
  `git diff` before doing anything further.

============================================================
9. WHERE TO FIND MORE DETAIL
============================================================

- `CHANGELOG.md` — the authoritative, phase-by-phase record (R0 through R8.1), including
  exact verification evidence (WebSocket message traces, risk scores observed live).
- `PROJECT_STATE.md` — high-level status, includes a "UI/UX Refresh Status" section
  separate from the backend's original Phase 1–10 numbering.
- `docs/demo/runbook.md` — presentation talking points per scenario, corrected during R8
  where a stale risk-score claim was found and fixed against live-verified data.
