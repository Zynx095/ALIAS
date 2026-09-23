import { Loader2, AlertTriangle } from 'lucide-react';
import { cn } from '../../lib/utils';

/**
 * Stage of the ALIAS evidence hierarchy:
 * 01 Observed Fact -> 02 Deterministic Finding -> 03 Correlated Risk -> 04 AI Interpretation
 */
export default function EvidenceSection({
  number,
  title,
  dotClassName = 'bg-text-muted',
  numberBg = 'bg-surface-soft text-text-secondary border-border',
  subtitle,
  status, // 'loading' | 'error' | 'empty' | 'success'
  emptyMessage,
  errorMessage,
  children,
}) {
  return (
    <section aria-labelledby={`evidence-${number}`} className="flex flex-col gap-3">
      {/* Stage Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 pb-1">
        <div className="flex items-center gap-2.5">
          <span className={cn("text-2xs font-mono font-bold px-2 py-0.5 rounded border", numberBg)}>
            {String(number).padStart(2, '0')}
          </span>
          <h2 id={`evidence-${number}`} className="text-xs font-bold uppercase tracking-wider text-text-primary">
            {title}
          </h2>
        </div>
        {subtitle && (
          <p className="text-2xs text-text-muted">
            {subtitle}
          </p>
        )}
      </div>

      {/* Loading State */}
      {status === 'loading' && (
        <div className="flex items-center gap-2.5 text-xs text-text-muted p-5 border border-border rounded-lg bg-surface shadow-2xs" role="status" aria-label={`Loading ${title}`}>
          <Loader2 className="w-4 h-4 animate-spin text-brand-ember shrink-0" aria-hidden="true" />
          <span>Analyzing telemetry for {title.toLowerCase()}…</span>
        </div>
      )}

      {/* Error State */}
      {status === 'error' && (
        <div className="flex items-start gap-2.5 text-xs text-sev-critical-text p-4 border border-sev-critical-indicator/40 rounded-lg bg-sev-critical-bg shadow-2xs" role="alert">
          <AlertTriangle className="w-4 h-4 mt-0.5 shrink-0 text-sev-critical-indicator" aria-hidden="true" />
          <span>{errorMessage || `Failed to load ${title.toLowerCase()}.`}</span>
        </div>
      )}

      {/* Empty State */}
      {status === 'empty' && (
        <div className="text-xs text-text-muted italic p-4 border border-border rounded-lg bg-surface-soft/60">
          {emptyMessage}
        </div>
      )}

      {/* Success Content */}
      {status === 'success' && children}
    </section>
  );
}
