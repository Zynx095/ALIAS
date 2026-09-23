import React, { useState } from 'react';
import { useAlerts } from '../../context/AlertContext';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowRight, User, MapPin, Smartphone, Activity, Radio } from 'lucide-react';
import { cn } from '../../lib/utils';
import { getSeverity } from '../../lib/severity';
import { SeverityBadge } from '../ui/severity-badge';

/**
 * Derives a human-readable telemetry summary from pipeline state
 */
function getEventSummary(state) {
  if (state.INVESTIGATION_REPORT?.summary) {
    const summary = state.INVESTIGATION_REPORT.summary;
    return summary.length > 80 ? summary.substring(0, 77) + '...' : summary;
  }
  if (state.ANOMALY_DETECTED?.anomalies?.length > 0) {
    const first = state.ANOMALY_DETECTED.anomalies[0];
    const count = state.ANOMALY_DETECTED.anomalies.length;
    return count > 1 ? `${first.anomaly_type} (+${count - 1} more deviations)` : first.explanation || first.anomaly_type;
  }
  if (state.RISK_ASSESSMENT?.risk_score === 0) {
    return 'Baseline authentication matching historical profile';
  }
  return 'Telemetry ingested — awaiting behavioral comparison';
}

export default function LiveStream({ onSelectEvent, selectedEventId }) {
  const { eventStream, pipelineState } = useAlerts();
  const [filterSeverity, setFilterSeverity] = useState('ALL');

  const uniqueEventIds = [...new Set(eventStream.map(e => e.event_id))];

  const filteredIds = uniqueEventIds.filter(id => {
    if (filterSeverity === 'ALL') return true;
    const risk = pipelineState[id]?.RISK_ASSESSMENT;
    if (!risk) return false;
    return risk.severity === filterSeverity;
  });

  return (
    <div className="bg-surface border border-border flex flex-col h-full shadow-xs overflow-hidden">
      {/* Feed Header */}
      <div className="px-4 py-3 border-b border-border flex justify-between items-center bg-surface-elevated">
        <div className="flex items-center gap-2">
          <Radio className="w-4 h-4 text-brand-ember" aria-hidden="true" />
          <h2 className="text-xs font-semibold uppercase tracking-wider text-text-primary font-heading">
            Live Event Feed
          </h2>
        </div>
        <div className="flex items-center gap-3">
          <select
            aria-label="Filter events by severity"
            className="bg-surface border border-border text-xs text-text-primary rounded px-2.5 py-1 outline-none focus-visible:ring-2 focus-visible:ring-focus font-medium"
            value={filterSeverity}
            onChange={(e) => setFilterSeverity(e.target.value)}
          >
            <option value="ALL">All Severities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MODERATE">Moderate</option>
            <option value="LOW">Low</option>
          </select>
          <span className="text-2xs text-text-muted font-mono bg-surface-soft px-2 py-0.5 rounded border border-border">
            {filteredIds.length} Stream{filteredIds.length === 1 ? '' : 's'}
          </span>
        </div>
      </div>

      {/* Telemetry Stream List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2.5 bg-canvas/30" tabIndex={0} aria-label="Event stream list">
        <AnimatePresence>
          {filteredIds.length === 0 ? (
            <div className="text-center text-text-muted text-xs mt-12 py-8 bg-surface border border-dashed border-border mx-2">
              <Activity className="w-6 h-6 mx-auto mb-2 text-text-muted/60" aria-hidden="true" />
              {eventStream.length === 0
                ? "Listening for live authentication telemetry..."
                : "No events match active severity filters. Clear filters to view all telemetry."}
            </div>
          ) : (
            filteredIds.map(id => {
              const state = pipelineState[id];
              if (!state || !state.LOGIN_EVENT) return null;

              const login = state.LOGIN_EVENT;
              const hasAnomaly = !!state.ANOMALY_DETECTED;
              const risk = state.RISK_ASSESSMENT;
              const hasReport = !!state.INVESTIGATION_REPORT;
              const isSelected = selectedEventId === id;
              const isCritical = risk?.severity === 'CRITICAL';
              const summaryText = getEventSummary(state);

              const sev = risk ? getSeverity(risk.severity) : null;

              return (
                <motion.div
                  key={id}
                  role="button"
                  tabIndex={0}
                  aria-label={`Open investigation for event ${id}, user ${login.user_id}, severity ${risk?.severity || 'Unassessed'}`}
                  initial={{ opacity: 0, y: -4 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={cn(
                    "p-3 rounded-sm border bg-surface flex flex-col gap-2 cursor-pointer transition-all outline-none shadow-2xs",
                    "hover:bg-surface-elevated hover:border-border-strong",
                    "focus-visible:ring-2 focus-visible:ring-focus",
                    isCritical
                      ? "border-sev-critical-indicator/40 bg-sev-critical-bg/15"
                      : "border-border",
                    isSelected && "border-brand-ember ring-1 ring-brand-ember bg-brand-soft/20"
                  )}
                  onClick={() => onSelectEvent(id)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault();
                      onSelectEvent(id);
                    }
                  }}
                >
                  {/* Top Bar: User & Severity */}
                  <div className="flex justify-between items-start gap-2">
                    <div className="flex items-center gap-2 min-w-0">
                      <span className="w-6 h-6 rounded bg-surface-soft border border-border flex items-center justify-center shrink-0">
                        <User className="w-3.5 h-3.5 text-text-secondary" aria-hidden="true" />
                      </span>
                      <span className="text-xs font-bold text-text-primary tracking-tight truncate">
                        {login.user_id}
                      </span>
                      <span className="text-3xs text-text-muted font-mono shrink-0">
                        {new Date(login.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', timeZoneName: 'short' })}
                      </span>
                    </div>

                    {risk ? (
                      <SeverityBadge severity={risk.severity} showScore score={risk.risk_score} />
                    ) : (
                      <span className="text-3xs font-mono text-text-muted bg-surface-soft px-1.5 py-0.5 rounded border border-border">
                        INGESTED
                      </span>
                    )}
                  </div>

                  {/* Summary Narrative */}
                  <p className="text-xs text-text-secondary leading-snug line-clamp-2">
                    {summaryText}
                  </p>

                  {/* Telemetry Metadata */}
                  <div className="text-2xs text-text-muted flex items-center gap-3 flex-wrap">
                    <span className="flex items-center gap-1 font-mono">
                      <MapPin className="w-3 h-3 text-text-muted shrink-0" aria-hidden="true" />
                      {login.ip_address}
                    </span>
                    <span className="text-border">·</span>
                    <span className="flex items-center gap-1">
                      <Smartphone className="w-3 h-3 text-text-muted shrink-0" aria-hidden="true" />
                      {login.access_pattern || 'DIRECT'}
                    </span>
                  </div>

                  {/* Pipeline Lifecycle Indicator */}
                  <div className="pt-2 mt-1 border-t border-border/60 flex items-center gap-1.5 text-3xs uppercase font-mono tracking-wider">
                    <span className="text-text-muted font-semibold">Ingested</span>
                    <ArrowRight className="w-2.5 h-2.5 text-text-muted/50" aria-hidden="true" />

                    <span className={state.BEHAVIORAL_COMPARISON ? "text-text-primary font-semibold" : "text-text-muted/60"}>
                      Baseline
                    </span>
                    <ArrowRight className="w-2.5 h-2.5 text-text-muted/50" aria-hidden="true" />

                    <span className={hasAnomaly ? "text-sev-high-text font-bold" : state.RISK_ASSESSMENT ? "text-text-muted font-semibold" : "text-text-muted/60"}>
                      {hasAnomaly ? `${state.ANOMALY_DETECTED.anomalies.length} Anom` : "Anomalies"}
                    </span>
                    <ArrowRight className="w-2.5 h-2.5 text-text-muted/50" aria-hidden="true" />

                    <span className={risk ? (risk.risk_score > 0 ? "text-sev-critical-text font-bold" : "text-sev-low-text font-bold") : "text-text-muted/60"}>
                      Risk {risk ? `(${risk.risk_score})` : ''}
                    </span>
                    <ArrowRight className="w-2.5 h-2.5 text-text-muted/50" aria-hidden="true" />

                    <span className={hasReport ? "text-ai-indigo font-bold bg-ai-soft px-1 rounded" : "text-text-muted/60"}>
                      AI Dossier
                    </span>
                  </div>
                </motion.div>
              );
            })
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
