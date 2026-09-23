# Phase 8: SOC Dashboard

## Phase Metadata
- **Phase ID:** 8
- **Phase Name:** SOC Dashboard
- **Status:** NOT STARTED
- **Started:** —
- **Completed:** —
- **Prerequisites:** Phase 7 (API & WebSocket Integration)

---

## 1. Objective & Intended Responsibility
Phase 8 transforms the frontend into a responsive, high-performance Security Operations Center (SOC) dashboard using React 19, Vite, and Tailwind CSS 4.

### Scope of Responsibility:
1. **Live Alert Stream:**
   - Real-time event ticker subscribed to the WebSocket gateway.
   - Severity badges, instant audio alerts for critical threats, and filtering controls.
2. **Interactive Threat Map:**
   - 2D / 3D Geospatial visualization of active authentication attempts.
   - Visual vector paths indicating impossible travel routes (e.g., origin point to destination point with velocity indicator).
3. **User Profile & Baseline Inspector:**
   - Detailed user view contrasting current login metrics with baseline histograms (active hours, frequent locations, known devices).
4. **AI Investigation Dossier UI:**
   - Visual display of AI-generated incident reports with MITRE ATT&CK tags, chronological evidence chain, and one-click remediation actions (e.g., "Force Session Revocation", "Mark Benign").
5. **System Health & Metrics:**
   - Ingestion throughput gauges, error rates, and active WebSocket connection count.

---

## 2. Key Deliverables
- Modernized SOC frontend application running on Vite + Tailwind CSS 4.
- Real-time WebSocket hook with automated reconnect logic.
- Geospatial map integration with impossible travel path rendering.
- AI report viewing and mitigation response interface.
