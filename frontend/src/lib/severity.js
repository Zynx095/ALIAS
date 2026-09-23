import { CircleDot, TriangleAlert, OctagonAlert, Siren, HelpCircle } from "lucide-react";

/**
 * Single source of truth for ALIAS severity color semantics.
 * Locked in Ivory Signal design direction.
 * Severity colors carry meaning only — never used decoratively.
 * Non-color redundancy: Every severity mark carries a Lucide glyph + signal bars + uppercase label.
 * Vocabulary matches backend: LOW, MODERATE, HIGH, CRITICAL.
 */

export const SEVERITY_LEVELS = ["LOW", "MODERATE", "HIGH", "CRITICAL"];

const SEVERITY_MAP = {
  LOW: {
    label: "LOW",
    bars: 1,
    icon: CircleDot,
    text: "text-sev-low-text",
    bg: "bg-sev-low-bg",
    border: "border-sev-low-indicator/40",
    dot: "bg-sev-low-indicator",
    hex: "#2F9E6F",
    indicator: "#2F9E6F",
    surface: "#F0FDF4",
    onSolid: "#FFFFFF",
  },
  MODERATE: {
    label: "MODERATE",
    bars: 2,
    icon: TriangleAlert,
    text: "text-sev-moderate-text",
    bg: "bg-sev-moderate-bg",
    border: "border-sev-moderate-indicator/40",
    dot: "bg-sev-moderate-indicator",
    hex: "#C58A24",
    indicator: "#C58A24",
    surface: "#FEFCE8",
    onSolid: "#FFFFFF",
  },
  HIGH: {
    label: "HIGH",
    bars: 3,
    icon: OctagonAlert,
    text: "text-sev-high-text",
    bg: "bg-sev-high-bg",
    border: "border-sev-high-indicator/40",
    dot: "bg-sev-high-indicator",
    hex: "#D86632",
    indicator: "#D86632",
    surface: "#FFF7ED",
    onSolid: "#FFFFFF",
  },
  CRITICAL: {
    label: "CRITICAL",
    bars: 4,
    icon: Siren,
    text: "text-sev-critical-text",
    bg: "bg-sev-critical-bg",
    border: "border-sev-critical-indicator/40",
    dot: "bg-sev-critical-indicator",
    hex: "#C83D3D",
    indicator: "#C83D3D",
    surface: "#FEF2F2",
    onSolid: "#FFFFFF",
  },
};

const UNKNOWN = {
  label: "UNKNOWN",
  bars: 0,
  icon: HelpCircle,
  text: "text-text-muted",
  bg: "bg-surface-soft",
  border: "border-border",
  dot: "bg-border-strong",
  hex: "#858079",
  indicator: "#858079",
  surface: "#F0EDE8",
  onSolid: "#181716",
};

/** Returns the color/label/icon set for a severity string. Falls back to a neutral "unknown" state — never guesses a severity. */
export function getSeverity(severity) {
  const normalized = (severity || "").toUpperCase();
  return SEVERITY_MAP[normalized] || UNKNOWN;
}
