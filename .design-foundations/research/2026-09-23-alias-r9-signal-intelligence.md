# ALIAS R9: design brief, "Signal Intelligence"

This brief covers the premium UI/UX overhaul of ALIAS, an existing React/Vite security-investigation product that already works end to end. The goal is a coherent design foundation (R9.1) that later surface redesigns (R9.2 onward) build on.

- **Date:** 2026-09-23
- **Status:** draft
- **Product truth:** `PRODUCT.md`
- **Source brief:** the R9 master prompt from the user
- **Audit evidence:** `.impeccable/critique/2026-09-23T05-53-39Z__frontend-src.md` (scored 20/40)

## Open questions
All resolved on 2026-09-23:
1. **Typography:** pinned to **Geist** for text, with **Geist Mono** for machine data such as IPs, event IDs, hashes and rule IDs.
2. **Display:** the demo will be shown on a **laptop screen**, so the standard WCAG AA contrast floor is enough; no projector compensation is needed.
3. **AI accent:** pinned to **indigo, hue about 275**, and reserved for AI-interpretation UI only.

## What
ALIAS analyzes login events. A deterministic pipeline (behavioral baseline → anomaly detection → multi-signal correlation → risk score) produces findings. An AI layer then only *interprets* those findings; it never detects anything on its own.

The product statement is: **"ALIAS doesn't just flag a suspicious login — it investigates why it is suspicious."**

The interface must make the evidence hierarchy visible:

OBSERVED FACT → DETERMINISTIC FINDING → CORRELATED RISK → AI INTERPRETATION

## Who
- **Primary user: a SOC analyst** who is focused, working at a desktop, and triaging suspicious logins.
- **Secondary audience: hackathon judges** who watch a live demo of that analyst's workflow, typically for about 60 seconds of attention. The Scenario Console runs the demo.

## Jobs to be done
The analyst hires ALIAS for three jobs:
1. Notice that something is happening (the Overview).
2. Understand why a specific login is suspicious and what evidence supports that (the Investigation Workspace).
3. Decide what to do next (the recommended actions, and the History queue).

Before ALIAS, analysts got flat "suspicious login" alerts with no reasoning attached.

## Surfaces
These are fixed and must be preserved:
- `/dashboard`: Overview / Command Center
- `/investigations`: History
- `/investigations/:eventId`: Investigation Workspace

The Scenario Console is a controlled demo surface inside the Overview.

## Device and constraints
- **Device:** desktop and laptop first. Tablet and narrow screens must degrade by prioritizing information, not by shrinking everything.
- **Stack:** React 19, Vite, Tailwind 4 (tokens defined through CSS `@theme`), shadcn/Radix, Lucide icons, and framer-motion (the only animation library). No Next.js, no new state library, and no second UI, animation, or chart library.
- **Theme:** dark-only. The current app has no light theme.
- **Contracts are frozen:** backend, REST, WebSocket protocol and payloads, scenario semantics, and risk and severity thresholds must not change.
- **Honest data only:** never fabricate progress, risk, counts, completion states, or metadata.
- **Accessibility:** WCAG AA contrast, keyboard access, visible focus, severity never conveyed by color alone, and `prefers-reduced-motion` respected.
- **Audio:** allowed only after the visual foundation is stable. It must be subtle and optional.

## Feel
These words describe a mood, not a look: intelligence, investigation, trust, precision, evidence, real-time awareness, and **controlled urgency**. The reference point is a professional SOC platform crossed with a modern AI investigation workspace, high-end data visualization, and subtle security instrumentation.

Sophistication should come from information architecture, evidence hierarchy, data visualization, typography, motion, precision, and restraint.

### Anti-references
These are explicitly banned: generic cyberpunk, gamer UI, excessive neon, crypto-dashboard styling, sci-fi movie interfaces, random glassmorphism, big gradients, glow effects, constant pulsing, particle effects, template KPI-card grids, and "AI slop".

## Taste signals (dealer pins)
- `register=dark-only`
- `family-direction="Signal Intelligence"`: restrained, precise, instrument-like. Not neon.
- `severity-scale=LOW/MODERATE/HIGH/CRITICAL`. Severity color carries meaning only and is always paired with a non-color cue.
- `ai-accent=reserved`: exactly one accent hue, used only for AI-interpretation UI. It must never be used for focus rings, navigation, or generic chrome.
- `motion=purposeful-only`: covers arrival, causality, and state change. No looping animation.
- `font=Geist` for text and `mono=Geist Mono` for machine data
- `ai-hue=indigo(275)`
- `display=laptop` (WCAG AA floor)

## Evidence from the audit (current state)
- **Token bug:** `--color-text-primary` and `--color-bg-primary` are missing from `@theme`, so every heading renders in the secondary gray.
- **Muted text fails contrast:** `--text-muted` measures about 2.9 to 3.4:1 on every surface, below the AA minimum.
- **Severity is defined twice**, as Tailwind palette classes and as unused CSS tokens. It is also used decoratively.
- **LiveStream bypasses the token system** entirely, using hard-coded zinc colors and `#0a0a0a`.
- **The focus ring uses the AI accent**, which breaks the reservation rule.
- **Mouse-only entry:** the Overview → Investigation path cannot be done by keyboard (P0).
- **Reload wipes the Overview:** it only knows what arrived over the WebSocket (P1).
- **The correlation climax is not visualized:** the backend sends `risk_factors[].contribution` and `supporting_anomaly_ids`, and the UI does not render them (P1).
- **Layout:** the Scenario Console gets 2 of 12 columns, and the fixed sidebar breaks narrow screens (P1).

## Phasing agreed so far
- **R9.1: foundation.** Tokens, type, surfaces, severity treatment, motion principles, and primitives. It also includes the P0 keyboard-access fix and the P1 fix that loads existing data from REST into AlertContext on reload (the WebSocket itself is unchanged).
- **R9.2: the Investigation climax.** A contribution bar, links between correlation factors and the findings they rest on, and AI text that cites the findings it interprets.
- **Later:** the Overview command center and responsive shell, then the History queue, polish, and audio.
