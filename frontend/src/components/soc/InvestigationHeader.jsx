import { ArrowLeft, User, MapPin, Smartphone, Loader2, ShieldAlert } from 'lucide-react';
import { SeverityBadge } from '../ui/severity-badge';
import { RiskScore } from '../ui/risk-score';

/**
 * Authoritative investigation identity header.
 * Shows exact subject identity, event metadata, and prominent RiskScore horizontal meter.
 */
export default function InvestigationHeader({ eventState, riskState, onBack, origin = 'overview' }) {
  const event = eventState.status === 'success' ? eventState.data : null;
  const risk = riskState.status === 'success' ? riskState.data : null;
  const backLabel = origin === 'history' ? 'Back to Investigation Register' : 'Back to Overview';

  return (
    <div className="bg-surface border border-border p-5 shrink-0 shadow-xs flex flex-col gap-4">
      {/* Origin Navigation */}
      <div className="flex items-center justify-between border-b border-border/80 pb-3">
        <button
          type="button"
          onClick={onBack}
          className="inline-flex items-center gap-2 text-xs font-semibold text-text-secondary hover:text-brand-ember transition-colors outline-none focus-visible:ring-2 focus-visible:ring-focus rounded py-1 px-1.5 -ml-1.5"
        >
          <ArrowLeft className="w-3.5 h-3.5" aria-hidden="true" />
          <span>← {backLabel}</span>
        </button>

        <span className="text-3xs font-mono uppercase tracking-widest text-text-muted bg-surface-soft px-2 py-0.5 border border-border">
          Forensic Telemetry Dossier
        </span>
      </div>

      {/* Main Dossier Subject & Score Summary */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-5">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-3xs font-mono uppercase tracking-widest text-brand-ember font-bold">
              Investigation Target
            </span>
            {event && (
              <span className="text-xs text-text-muted font-mono">
                · EVT-{event.id}
              </span>
            )}
          </div>

          {eventState.status === 'loading' && (
            <div className="flex items-center gap-2 text-sm text-text-muted py-2">
              <Loader2 className="w-4 h-4 animate-spin text-brand-ember" aria-hidden="true" />
              Loading event metadata…
            </div>
          )}

          {eventState.status === 'error' && (
            <p className="text-xs text-sev-critical-text font-medium py-1">Failed to load target event details.</p>
          )}

          {event && (
            <>
              <h1 className="text-xl font-bold tracking-tight text-text-primary flex items-center gap-2.5 font-heading">
                <span className="w-8 h-8 rounded-sm bg-brand-soft border border-brand-ember/30 flex items-center justify-center text-brand-ember shrink-0">
                  <User className="w-4 h-4" aria-hidden="true" />
                </span>
                <span className="truncate">{event.user_id}</span>
              </h1>

              <div className="mt-2.5 flex items-center gap-4 flex-wrap text-xs text-text-secondary">
                <span className="flex items-center gap-1.5 font-mono">
                  <MapPin className="w-3.5 h-3.5 text-text-muted shrink-0" aria-hidden="true" />
                  <span>{event.ip_address}</span>
                  {event.location && <span className="font-sans text-text-muted">({event.location})</span>}
                </span>

                {event.device_fingerprint && (
                  <span className="flex items-center gap-1.5 font-mono text-2xs text-text-muted">
                    <Smartphone className="w-3.5 h-3.5 text-text-muted shrink-0" aria-hidden="true" />
                    <span>{event.device_fingerprint}</span>
                  </span>
                )}

                <span className="text-2xs font-mono text-text-muted">
                  {new Date(event.timestamp).toUTCString()}
                </span>
              </div>
            </>
          )}
        </div>

        {/* Prominent Risk Score Meter */}
        <div className="shrink-0 w-full md:w-auto">
          {risk ? (
            <RiskScore score={risk.risk_score} severity={risk.severity} size="large" className="w-full md:w-60" />
          ) : riskState.status === 'loading' ? (
            <div className="bg-surface border border-border rounded-sm p-4 min-w-[200px] flex items-center justify-center gap-2 text-xs text-text-muted">
              <Loader2 className="w-3.5 h-3.5 animate-spin text-brand-ember" aria-hidden="true" />
              <span>Assessing Risk...</span>
            </div>
          ) : (
            <div className="bg-surface border border-border rounded-sm p-3.5 text-xs text-text-muted">
              No Risk Assessment Recorded
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
