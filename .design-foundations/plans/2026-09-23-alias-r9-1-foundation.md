# Design plan: ALIAS R9.1 "Signal Intelligence" foundation

- **Date:** 2026-09-23
- **Track:** Standard
- **Entry stage:** Discover. Neither DESIGN.md nor JOURNEY.md existed when this plan was written.
- **Seed:** `.design-foundations/research/2026-09-23-alias-r9-signal-intelligence.md`
- **Product truth:** `PRODUCT.md`
- **Audit baseline:** `.impeccable/critique/2026-09-23T05-53-39Z__frontend-src.md`, which scored 20/40
- **Status:** ready

## Context
The user confirmed this problem statement on 2026-09-23.

**Problem.** ALIAS already has three working screens. What it lacks is a design system. R9.1 creates the "Signal Intelligence" foundation so that the evidence chain reads at a glance:

observed fact → deterministic finding → correlated risk → AI interpretation

A SOC analyst should see what happened, why it is suspicious, and what to do next. A judge should understand the same within 60 seconds of the live demo.

The foundation covers:
- tokens
- the type scale
- the surface language
- how severity is shown
- motion rules
- specs for the shared components

It is applied to the existing screens without redesigning any layout.

**Success.** The design is done when:
- every text and background pairing passes WCAG AA, including muted text
- tokens cover all shared roles, and the mock contains no hard-coded hex values
- the four evidence stages are visually distinct, and severity can be read without relying on color
- a design review of the rendered mock finds no Critical issues

The code-level checks are acceptance criteria for the R9.1 code commit, not for this plan (see D3). They are: no hard-coded colors on any screen, and every existing behavior still works.

## Constraints
The user pinned these, so they are user law:
- Dark theme only.
- Geist for text; Geist Mono for machine data (IPs, IDs, hashes, rule IDs).
- The indigo AI accent (hue about 275) is reserved for AI-interpretation UI.
- Severity uses LOW, MODERATE, HIGH and CRITICAL, always with a non-color cue.
- Motion is used only when it carries meaning. Nothing loops.
- The display target is a laptop screen, so the contrast floor is WCAG AA.

These are banned: neon, glow, big gradients, glassmorphism, constant pulsing, particles, and KPI-card template grids.

The information architecture is fixed: `/dashboard`, `/investigations` and `/investigations/:eventId`, with the Scenario Console inside the Overview.

The stack is fixed: React 19, Vite, Tailwind 4 through CSS `@theme`, shadcn/Radix, Lucide, and framer-motion. No new UI, animation, chart or state libraries.

These contracts are frozen: backend, REST, the WebSocket, scenario behavior, and the risk and severity thresholds.

Never display fabricated data.

## Chosen Approach
Record the current journey first (JOURNEY.md), because the design cannot specify screens the journey has not described. Then lock the visual direction and its tokens (DESIGN.md) through design-for-ai's DNA pipeline:
1. The `dealer.mjs` script deals values for the axes the user has not pinned.
2. The `palette.mjs` script generates color tokens that pass contrast by construction.
3. Five candidates are critiqued.
4. The user picks one.

Finally, write the component specs and the wording changes. Phases 3 and 4 are independent of each other — neither consumes the other's output — but `build` executes one phase at a time, so they run sequentially, not literally in parallel.

Translating the specs into the React app happens after `build`, as a separate implementation step. It is not a phase of this plan.

## Rejected Approaches
- **Hand-editing the current `index.css` tokens.** This skips the DNA gate and leaves the contrast floor unverified, which is the root cause of the 2.9–3.4:1 muted-text failures.
- **Starting at the design phases without JOURNEY.md.** This breaks gate 1. The existing screens are known, so recording them costs little and gives R9.2 onward its specs.
- **Including data-viz screen work (contribution bar, travel arc).** That work belongs to R9.2. Here data-viz only guides the risk meter and the severity glyph.

---

### Phase 1: As-built journey
**Stage:** Discover
**Model:** sonnet
**Doctrine:** journey, usability
**Gate:** Standard

**Goal:** Record the analyst's jobs, the journey through the product, the screen map, the flows, and a spec for each of the three screens, exactly as they work today.

**Scope:**
- IN:
  - A JTBD job story, using Moesta's Switch interview school only.
  - A journey covering Notice, Understand and Decide, with the emotional curve (the critique found dips at first paint and at the end state).
  - The screen map, following Rosenfeld and Morville's four IA systems.
  - Flows: open an investigation from the stream, the globe, History or the Scenario Console; run, complete or fail a scenario; reset; go back to where you came from.
  - Page specs for all three screens: purpose, entry points, blocks, the four states, primary CTA, and exit.
  - Each spec also records the information priorities from the R9 brief.
- OUT: Any change to the screen map, new routes, or layout redesign.

**Constraints:** Record the screens as built. Code is the source of truth. Flag any gap between the docs and the code instead of fixing it here.

**Edge cases:**
- The journey map could turn into theater. To prevent that, name an owner (the ALIAS team) and state the evidence base (the audit and the demo runbook).
- The flow from a scenario to the Investigation screen has no automatic navigation today. Record that as it is.

**Produces:** JOURNEY.md, with the sections Job, Journey, IA, Flows and Page specs.
**Depends on:** the research doc | **Unlocks:** Phases 2–5

**Done when:**
- [ ] DW-1.1: JOURNEY.md `## Page specs` has three complete page entries, each with purpose, entry, blocks, states (loading, empty, error, success), CTA and exit.
- [ ] DW-1.2: Flows cover every path from the Overview into an investigation, plus the scenario run → complete → open → reset cycle, including the failed state.
- [ ] DW-1.3: The design-review agent's synthesis reports no Critical findings, and every Major finding is resolved or explicitly accepted.

---

### Phase 2: Signal Intelligence direction and tokens
**Stage:** Design
**Model:** fable
**Doctrine:** design-dna, archetypes, foundations, color, fonts, ai-tells, motion
**Gate:** Full

**Goal:** Lock DESIGN.md: the DNA (one of five critiqued candidates), the color tokens generated by `palette.mjs`, the type scale, and the motion budget.

**Scope:**
- IN: Archetype derivation (Sage first, then Ruler or Caregiver), grounding, the five candidates, the critique, convergence, the token block, the type scale, spacing, radius, depth, motion, and the "Never" list.
- OUT: Component specs (Phase 3), wording (Phase 4), and code.

**Constraints:** The research doc's taste signals, copied verbatim:
- `register=dark-only`
- `family-direction="Signal Intelligence"`: restrained, precise, instrument-like. Not neon.
- `severity-scale=LOW/MODERATE/HIGH/CRITICAL`. Severity color carries meaning only and is always paired with a non-color cue.
- `ai-accent=reserved`: exactly one accent hue, used only for AI-interpretation UI. It must never be used for focus rings, navigation or generic chrome.
- `motion=purposeful-only`: covers arrival, causality and state change. No looping animation.
- `font=Geist` for text and `mono=Geist Mono` for machine data.
- `ai-hue=indigo(275)`. This is **not** passed to the dealer (see D4). The AI accent gets its own prefixed ramp.
- `display=laptop` (WCAG AA floor).
- Family: `--pin family=data-dense-professional` (D1, decided 2026-09-23).

**Edge cases:**

*Token mechanics.* `palette.mjs` puts every token of a run under one namespace, so a second run would otherwise overwrite the first. All runs use `--project alias --date 2026-09-23` for the dealer, so the deal is reproducible; the ledger (`used-dna.json`) is written to `.design-foundations/used-dna.json`, not the repo root.
- **Chrome run.** Run the dealt seed with `--scheme dark`. The dealt hue only tints the neutrals, because `palette.mjs` caps neutral chroma at 0.018. Chrome, navigation and `--focus` resolve to high-step neutrals. `--accent-*` is unused or aliased to neutrals, so there is no saturated chrome accent (D5).
- **AI run.** `palette.mjs --seed 275 --chroma balanced --scheme dark --prefix ai`, matching the Signal Intelligence direction's chroma character.
- **Severity runs.** `--chroma balanced --scheme dark`, `--prefix sev-low` (seed 160), `sev-moderate` (75), `sev-high` (45) and `sev-critical` (25).
- **What to keep from the prefixed runs.**
  - AI: keep `--ai-accent-11` as the AI indicator/solid role (≥7:1, verified). Keep `--ai-accent-9` only as a fill behind on-solid text (on-solid on step 9 measures 6.19:1) — never as a standalone indicator, icon, or text color, since step 9 alone falls to 2.2–3.0:1 against the surfaces. Discard steps 1–8, 10, and 12 unless a later phase needs them.
  - Severity: keep steps 3 (subtle background), 9 (solid/indicator) and 11 (text) and on-solid.
  - Discard every run's neutral ramp, its functional colors (error/success/warning/info), and its semantic aliases (for example `--ai-surface`, `--sev-low-background`) — none of these act as surfaces.
- **Selector.** `--scheme dark` writes to `[data-theme="dark"]`. The product is dark-only, so map these tokens to `:root` / `@theme`.
- **Exit code 2.** `palette.mjs` exits with code 2 when a pair fails contrast. Read stdout anyway; a nonzero exit on a step this plan doesn't keep (e.g. a discarded semantic alias) is expected and not a rejection trigger — only reject a token that DW-2.2/DW-2.3 actually require.

*Hue collisions.*
- **Hue proximity (C1).** Every five-hand deal lands at least one hand near 275, so a reroll loop never ends. Do not re-deal for hue. At critique, flag any hand within 60° of 275 as "conflicts with ai-accent=reserved". If the user still picks it, do a converge-time hue swap to at least 60° from 275, re-run `palette.mjs`, and re-present once.
- **Error vs CRITICAL (m1).** The functional `--error-*` color shares hue 25 with CRITICAL. System states therefore use no functional color: error, failed, completed and disconnected are shown as neutral text plus a Lucide icon. The functional colors are excluded from the alias set.

*Tells.*
- **AI-accent tell.** `ai-tells.md` lists the "purple-indigo-violet triplet" (High severity). The accent must therefore:
  - come from the `--ai-*` ramp, never from Tailwind indigo classes
  - never appear in a gradient or a heading
  - be used only on AI UI
  - be recorded in the Never list
- **Dark-default tell.** Justify the dark theme from the SOC operating context, and ban glow.

*Severity and family.*
- **Red vs green.** LOW and CRITICAL can't be told apart by color alone, so a redundant glyph is mandatory.
- **Poorly fitting families.** The dealer may deal a family that fits badly. Flag it at critique on content pressure. Never hand-edit a dealt hand.
- **Dealer signature conflicts.** The dealer's signature deck includes moves like `accent-scarcity` ("the accent color appears only on the current nav item and the primary CTA"), which would put the AI-reserved indigo on navigation or a primary action — a direct violation of `ai-accent=reserved` and D5. At critique, flag any dealt signature that would place a saturated accent (indigo or otherwise) on chrome, navigation, or a non-AI/non-severity surface. Never hand-edit the signature; instead offer a converge-time signature swap (design-dna Converge swaps) to a signature that doesn't touch those surfaces, and re-present once with a fresh critique line.

*User pause (M4).* The build agent cannot prompt the user. After the critique, it returns UPDATE_PLAN with all five critiqued candidates. The orchestrator asks the user to pick, synthesize or swap. The agent is then re-dispatched to converge. The "Lock this in?" gate is asked the same way.

**Produces:** DESIGN.md, locked, containing: the token block, the contrast matrix, the type scale, spacing, radius and depth, motion, and the Never list.
**Depends on:** Phase 1 | **Unlocks:** Phases 3, 4 and 5

**Done when:**
- [ ] DW-2.1: DESIGN.md is locked: the token block is present and the user confirmed it through the "Lock this in?" gate (asked through the orchestrator).
- [ ] DW-2.2: DESIGN.md has a contrast matrix, verified by computed WCAG ratio (not the `palette.mjs` report). It covers two text levels — primary and supporting/muted, distinguished by typography (size, weight, spacing) rather than a third low-contrast color step, since the available neutral steps at ≥4.5:1 (9, 10, 11, 12) don't yield a visually distinct third tier — plus the four severity text steps and AI text, each on every surface (canvas, panel, inset, hover, active). Every pair is at least 4.5:1.
- [ ] DW-2.3: Every non-text token reaches at least 3:1 against the surfaces it sits on: the four severity solid (step-9) indicators, the AI indicator (`--ai-accent-11`, not step 9), and boundary borders. "Boundary" means input, form and interactive-control outlines only, mapped to `--neutral-9`; decorative dividers/separators are exempt from this check (WCAG 1.4.11 scopes the non-text requirement to UI components and graphical objects, not decoration). `--neutral-9`'s ≥3:1 margin against the chrome surfaces depends on the chrome seed staying at least 60° from 275 (C1, DW-2.7) — at 275 itself, neutral-9 drops to 2.93:1, which is exactly why that hue is reserved for `--ai-*` and excluded from chrome.
- [ ] DW-2.4: All semantic aliases resolve: background, three surface levels, two text levels, border, focus, `--ai-*` (accent-11 indicator, accent-9 fill-only), and the four `--sev-*` levels (step-3 background, step-9 indicator, step-11 text).
- [ ] DW-2.5: The type scale (`--text-xs` to `--text-4xl`) is present, including a mono role for machine data.
- [ ] DW-2.6: The design-review agent's synthesis finds no Critical findings. Every Major finding is resolved or explicitly accepted. The tells scan is clean or has a stated justification for each hit.
- [ ] DW-2.7: `--focus`, `--accent-*` and every chrome alias resolve to neutral steps. Only `--ai-*` aliases resolve to the hue-275 ramp. The chosen seed hue is at least 60° from 275.

---

### Phase 3: Foundation components
**Stage:** Design
**Model:** sonnet
**Doctrine:** design-systems, interaction, motion, usability, data-viz
**Gate:** Full

**Goal:** Turn DESIGN.md into a token machine and a set of component specs that the R9.1 code will implement.

**Scope:**
- IN:
  - Three token tiers (global, alias, component) in DTCG naming.
  - Panel at three surface levels: canvas, panel, inset.
  - Button variants: primary, secondary, ghost, and confirm-destructive.
  - SeverityBadge with a signal-bar glyph showing 1–4 bars.
  - The RiskScore meter.
  - An EvidenceStage marker for each of the four stages.
  - The focus ring.
  - The eight interaction states.
  - Standard loading, empty and error states, shown as neutral plus an icon.
  - Three motion presets: enter, reveal and value-change.
- OUT: Screen layouts, the contribution bar (R9.2), and the responsive shell.

**Constraints:** Extend the tokens; never replace them. Components consume alias tokens only.

**Edge cases:**
- **Findings.** A finding takes severity color only when the backend computed a severity for it. Today every finding is orange regardless.
- **RiskScore.** The meter encodes the score truthfully: a linear 0–100 scale with a visible baseline (Cairo).
- **Motion.** Motion never fakes progress: value-change only moves between two real values. Under reduced motion every preset becomes an instant state change.
- **Focus.** The focus ring is never the AI accent.

**Produces:** a `## Components` section in DESIGN.md, plus the token tiers.
**Depends on:** Phase 2 | **Unlocks:** Phase 5

**Done when:**
- [ ] DW-3.1: Every component spec references alias tokens only, with no hard-coded hex values.
- [ ] DW-3.2: Severity can be read without color: the glyph plus the label pass a grayscale check.
- [ ] DW-3.3: Interactive states reach at least 3:1 as non-text. The focus ring is at least 2px and reaches at least 3:1.
- [ ] DW-3.4: The design-review agent's synthesis finds no Critical findings, and every Major finding is resolved or explicitly accepted.
- [ ] DW-3.5: The four EvidenceStage markers can be told apart in grayscale by glyph or label, and only the AI stage uses `--ai-*` tokens.
- [ ] DW-3.6: Every motion preset names the state change it communicates and its reduced-motion equivalent. No preset loops.

---

### Phase 4: Interface words
**Stage:** Design
**Model:** sonnet
**Doctrine:** content-design, ai-native
**Gate:** Standard

**Goal:** Fix the copy the audit flagged, and set the voice so the AI text never overclaims.

**Scope:**
- IN:
  - The `mock-fallback` label.
  - An origin-aware "Back to …" label.
  - "Awaiting telemetry…" and "Active Tracks".
  - One name for the Overview.
  - The AI disclaimer.
  - Error copy that states the cause and the fix (Yifrah).
  - Empty-state guidance.
  - An honest label for "Anomalies Detected".
  - Three to five voice attributes.
- OUT: Any new claims or invented metadata.

**Edge cases:** AI copy cites the findings it interprets (ai-native trust calibration; principle-derived, no settled canon). Copy that implies detection or a verdict is rejected.

**Produces:** microcopy tables in the JOURNEY.md `## Page specs`.
**Depends on:** Phases 1 and 2 | **Unlocks:** Phase 5

**Done when:**
- [ ] DW-4.1: Every error and empty state in the page specs has copy that states the cause and the next step.
- [ ] DW-4.2: No copy claims that the AI detected anything or reached a verdict.
- [ ] DW-4.3: The design-review agent's synthesis finds no Critical findings, and every Major finding is resolved or explicitly accepted.

---

### Phase 5: Foundation mock
**Stage:** Design
**Model:** sonnet
**Doctrine:** interaction, usability, ai-tells, data-viz
**Gate:** Full

**Goal:** Render a styled, self-contained HTML mock that applies the locked foundation to the Investigation Workspace (the evidence chain at CRITICAL), plus a strip of shared components (every SeverityBadge level, RiskScore, the buttons, and the loading, empty and error states). The user signs it off before any React code changes.

**Scope:**
- IN: One Investigation screen using real data taken from the Multi-Signal Compromise scenario, and the component strip.
- OUT: Overview and History layouts, which are recorded in JOURNEY.md only.

**Edge cases:**
- The mock uses the tokens only, with no hex values.
- The data shown is real scenario output, never invented.

**Produces:** `mocks/investigation-foundation.html`, a screenshot, and review findings.
**Depends on:** Phases 1–4 | **Unlocks:** the R9.1 code commit (D3)

**Done when:**
- [ ] DW-5.1: The mock renders as a self-contained `.html` file with no missing dependencies.
- [ ] DW-5.2: The mock contains no hard-coded hex values.
- [ ] DW-5.3: On the rendered pixels, severity and the four evidence stages can be told apart in grayscale.
- [ ] DW-5.4: The design-review agent's synthesis finds no Critical findings, and every Major finding is resolved or explicitly accepted.

---

## Verification plan
Every done-when item above (DW-1.1 to DW-5.4) is checked by inspecting its artifact, and each phase also goes through the review agent's dual-blind synthesis. Dirty cases and their expected outcomes:
- **DESIGN.md is missing when Phase 3, 4 or 5 starts:** block, and point back to Phase 2.
- **A contrast-matrix pair falls below AA:** reject the token and move its ramp step. Never hand-edit a hex value.
- **A prefixed run leaks aliases** (for example `--ai-surface` used as a surface): DW-2.4 fails.
- **The chosen seed hue is within 60° of 275:** do a converge-time hue swap, re-present, and keep DW-2.7 open until the swap is done.
- **The AI accent appears on chrome, focus, or a gradient:** Major finding.
- **Severity is readable by color only:** Critical finding (Kadavy chapter 8).
- **An error state uses the CRITICAL hue:** Major finding (m1).
- **A page spec is missing its loading, empty or error state:** DW-1.1 fails.
- **Copy implies an AI verdict:** Critical finding (violates PRODUCT.md's "never overclaim" principle).

**Verification level:** artifact plus heuristic review per phase, with the final trust report from `build`.

## Assumptions
- The five demo scenarios and the backend payloads stay stable through R9.
- The design system has a single owner (the ALIAS team), with lightweight governance appropriate to a hackathon.

## Decision Log
- **D1, family pin (closed 2026-09-23).** Pinned to `--pin family=data-dense-professional`. This family's rule — saturated accents reserved for DATA, not chrome — matches the plan's severity-only/AI-only colour rule directly. All five candidates share this family and diverge on discipline, signature, and (within the ≥60°-from-275 constraint) hue.
- **D2.** Geist is a user pin and rides the TYPE line as a constraint. The dealer does not deal it.
- **D3.** Code implementation sits outside `build`. It is the R9.1 code commit, which re-reads DESIGN.md first. It is accepted when all of the following hold:
  - `npm run build` passes.
  - No screen has a hard-coded color.
  - Scenarios 1–5 run, and their completion arrives over the WebSocket.
  - Reset Demo works.
  - Navigation works.
  - Stream cards open from the keyboard.
  - A reload keeps the Overview's data.
  - The backend, REST and WebSocket contracts are unchanged.
- **D4 (from CHECK 1).** The hue pin was taken off the dealer, because the dealer's `hue` sets the palette seed.
- **D5 (from CHECK 2).** Chrome has no saturated accent. The dealt hue only tints the neutrals. Saturated color exists only for severity (data) and AI interpretation.
- **D6 (from CHECK 2).** A styled mock is built inside `build` (Phase 5), because running the pre-build `/design-for-ai:mock` with no DESIGN.md would only produce a greyscale wireframe of screens whose structure is already fixed.
- **D7 (from CHECK 3), accepted tooling deviations.** The build/trust-report checks that `palette.mjs`'s default functional colors (error/success/warning/info) are present, that both light and dark schemes pass, and that every `palette.mjs` invocation exits 0 are generic tool defaults that conflict with approved product doctrine. ALIAS explicitly:
  - uses the four backend severity levels instead of generic error/success/warning semantic colors (system states like "failed" or "disconnected" are neutral + icon, not a functional color — see the Error vs CRITICAL edge case in Phase 2);
  - is dark-only by product requirement, so no light-scheme pass is expected or produced;
  - may see a nonzero exit from a `palette.mjs` run on a step this plan discards (e.g. a semantic alias never wired into the token set) — this is expected per the Exit code 2 edge case in Phase 2, not a build failure.
  These are accepted deviations from generic tooling assumptions, not defects; `build`'s trust report should record them as accepted rather than failed.
