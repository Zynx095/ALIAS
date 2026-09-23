import React from 'react';
import { getSeverity } from '@/lib/severity';
import { cn } from '@/lib/utils';

/**
 * Visual representation of the composite risk score (0.0 to 100.0 linear scale).
 * Clean, elegant horizontal meter conforming to the Ivory Signal design system.
 * Not a circular gauge. Truthful baseline representation.
 */
export function RiskScore({ score = 0, severity, size = 'default', className }) {
  const numScore = typeof score === 'number' ? score : parseFloat(score) || 0;
  const clampedScore = Math.min(Math.max(numScore, 0), 100);

  // Derive severity from score if not provided
  let sevLevel = severity;
  if (!sevLevel) {
    if (clampedScore < 25.0) sevLevel = 'LOW';
    else if (clampedScore < 50.0) sevLevel = 'MODERATE';
    else if (clampedScore < 75.0) sevLevel = 'HIGH';
    else sevLevel = 'CRITICAL';
  }

  const s = getSeverity(sevLevel);
  const isLarge = size === 'large';

  return (
    <div
      className={cn(
        "flex flex-col rounded-md border border-border bg-surface p-3 transition-colors",
        isLarge && "p-4 min-w-[220px]",
        className
      )}
      role="meter"
      aria-valuenow={clampedScore}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-label={`Risk score: ${clampedScore.toFixed(0)} out of 100, severity ${s.label}`}
    >
      <div className="flex justify-between items-center mb-1.5">
        <span className="text-[10px] font-mono uppercase tracking-widest text-text-muted font-semibold">
          Risk Score
        </span>
        <span
          className={cn(
            "text-[11px] font-mono font-bold tracking-wider uppercase px-1.5 py-0.5 rounded",
            s.bg,
            s.text,
            "border border-border"
          )}
        >
          {s.label}
        </span>
      </div>

      <div className="flex items-baseline gap-1 font-mono mb-2">
        <span className={cn("font-bold tabular-nums text-text-primary", isLarge ? "text-2xl" : "text-lg")}>
          {clampedScore.toFixed(0)}
        </span>
        <span className="text-xs text-text-muted font-normal">/ 100</span>
      </div>

      {/* Clean Horizontal Meter Track */}
      <div className="h-2 w-full bg-surface-soft border border-border rounded-full overflow-hidden relative">
        <div
          className="h-full rounded-full transition-all duration-300 ease-out"
          style={{
            width: `${Math.max(clampedScore, 2)}%`,
            backgroundColor: s.indicator,
          }}
        />
      </div>
    </div>
  );
}

export default RiskScore;
