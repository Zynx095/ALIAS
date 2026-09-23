import { Badge } from "./badge";
import { getSeverity, SEVERITY_LEVELS } from "@/lib/severity";
import { cn } from "@/lib/utils";

/**
 * Single shared severity indicator. Color carries meaning only.
 * Triple non-color redundancy (DESIGN.md):
 * 1. Lucide glyph (CircleDot / TriangleAlert / OctagonAlert / Siren)
 * 2. Signal bar indicator (1–4 bars)
 * 3. Uppercase text label
 */
export function SeverityBadge({ severity, showScore, score, solid = false, className }) {
  const s = getSeverity(severity);
  const Icon = s.icon;
  const barsCount = s.bars || 0;

  if (solid) {
    return (
      <span
        className={cn(
          "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-[2px] font-mono text-xs font-semibold tracking-wider uppercase border",
          className
        )}
        style={{
          backgroundColor: s.indicator,
          borderColor: s.indicator,
          color: s.onSolid,
        }}
        role="status"
        aria-label={`Severity: ${s.label}${showScore && typeof score === "number" ? ` (Score: ${score})` : ""}`}
      >
        {Icon && <Icon className="w-3.5 h-3.5 shrink-0" aria-hidden="true" />}
        <span className="inline-flex items-end gap-[1.5px] h-2.5" aria-hidden="true">
          {[1, 2, 3, 4].map(b => (
            <span
              key={b}
              className="w-[2px] rounded-[0.5px]"
              style={{
                height: `${b * 2.5}px`,
                backgroundColor: b <= barsCount ? s.onSolid : "rgba(0,0,0,0.3)",
              }}
            />
          ))}
        </span>
        <span>{showScore && typeof score === "number" ? `${score} · ${s.label}` : s.label}</span>
      </span>
    );
  }

  return (
    <Badge
      variant="outline"
      className={cn(
        s.bg,
        s.text,
        s.border,
        "inline-flex items-center gap-1.5 font-mono text-xs font-semibold tracking-wide uppercase px-2 py-0.5 rounded-[2px]",
        className
      )}
      role="status"
      aria-label={`Severity: ${s.label}${showScore && typeof score === "number" ? ` (Score: ${score})` : ""}`}
    >
      {Icon && <Icon className="w-3 h-3 shrink-0" aria-hidden="true" />}
      <span className="inline-flex items-end gap-[1.5px] h-2.5" aria-hidden="true">
        {[1, 2, 3, 4].map(b => (
          <span
            key={b}
            className={cn(
              "w-[2px] rounded-[0.5px]",
              b <= barsCount ? "bg-current" : "bg-border"
            )}
            style={{ height: `${b * 2.5}px` }}
          />
        ))}
      </span>
      <span>{showScore && typeof score === "number" ? `${score} · ${s.label}` : s.label}</span>
    </Badge>
  );
}

/** Small non-interactive severity dot, for compact contexts (list rows, map points). Always paired with adjacent text elsewhere — never the sole indicator. */
export function SeverityDot({ severity, className }) {
  const s = getSeverity(severity);
  return <span className={cn("inline-block w-2 h-2 rounded-full", s.dot, className)} aria-hidden="true" />;
}

/** Compact legend explaining what the severity colors mean, for use next to any severity-colored visualization (e.g. CyberGlobe). */
export function SeverityLegend({ className }) {
  return (
    <div className={cn("flex flex-wrap items-center gap-x-3 gap-y-1", className)} role="list" aria-label="Severity legend">
      {SEVERITY_LEVELS.map(level => {
        const s = getSeverity(level);
        const Icon = s.icon;
        return (
          <span key={level} className="flex items-center gap-1.5 text-2xs text-text-muted font-mono">
            {Icon && <Icon className="w-3 h-3" style={{ color: s.indicator }} aria-hidden="true" />}
            <span>{s.label}</span>
          </span>
        );
      })}
    </div>
  );
}

