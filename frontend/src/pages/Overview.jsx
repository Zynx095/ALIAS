import { motion, useReducedMotion } from 'framer-motion';
import LiveStream from '../components/soc/LiveStream';
import CyberGlobe from '../components/CyberGlobe';
import ScenarioConsole from '../components/soc/ScenarioConsole';
import { useAlerts } from '../context/AlertContext';
import { ShieldAlert, Users, Activity, Sparkles } from 'lucide-react';

/**
 * Overview surface — "what is happening right now?"
 * Strong editorial layout with horizontal activity summary,
 * dual-panel intelligence workspace (Globe + Telemetry), and
 * scenario simulation controls.
 */
export default function Overview({ onOpenInvestigation }) {
  const { eventStream, pipelineState } = useAlerts();
  const reduceMotion = useReducedMotion();

  // Derived stats sourced directly from the live WebSocket pipeline
  const totalEvents = eventStream.filter(e => e.type === 'LOGIN_EVENT').length;
  const totalAnomalies = eventStream.filter(e => e.type === 'ANOMALY_DETECTED').length;

  let criticalRisks = 0;
  Object.values(pipelineState).forEach(state => {
    if (state.RISK_ASSESSMENT && state.RISK_ASSESSMENT.severity === 'CRITICAL') {
      criticalRisks++;
    }
  });

  const investigations = eventStream.filter(e => e.type === 'INVESTIGATION_REPORT').length;

  return (
    <div className="flex flex-col gap-6 max-w-[1600px] mx-auto pb-8">
      {/* 1. Editorial Header & Activity Summary Bar */}
      <section className="flex flex-col gap-3">
        <div className="flex flex-col sm:flex-row sm:items-baseline justify-between gap-2 border-b border-border pb-3">
          <div>
            <h1 className="text-sm font-bold uppercase tracking-wider text-text-primary">
              Security Overview
            </h1>
            <p className="text-xs text-text-secondary mt-0.5">
              Real-time identity activity and behavioral risk
            </p>
          </div>
          <span className="text-[11px] font-mono text-text-muted">
            Telemetry Gateway: ACTIVE
          </span>
        </div>

        {/* Compact Horizontal Activity Summary Bar (Not a grid of identical cards) */}
        <div className="bg-surface border border-border rounded-lg px-6 py-3.5 flex items-center justify-between gap-4 shadow-xs flex-wrap">
          <div className="flex items-center gap-3">
            <span className="w-8 h-8 rounded-md bg-surface-soft border border-border flex items-center justify-center shrink-0">
              <Users className="w-4 h-4 text-text-secondary" aria-hidden="true" />
            </span>
            <div className="flex flex-col">
              <span className="text-lg font-bold tabular-nums text-text-primary leading-tight font-mono">
                {totalEvents}
              </span>
              <span className="text-[10px] font-mono uppercase tracking-wider text-text-muted">
                Logins Analyzed
              </span>
            </div>
          </div>

          <div className="hidden sm:block h-8 w-[1px] bg-border" aria-hidden="true" />

          <div className="flex items-center gap-3">
            <span className="w-8 h-8 rounded-md bg-surface-soft border border-border flex items-center justify-center shrink-0">
              <Activity className="w-4 h-4 text-sev-high-indicator" aria-hidden="true" />
            </span>
            <div className="flex flex-col">
              <span className="text-lg font-bold tabular-nums text-text-primary leading-tight font-mono">
                {totalAnomalies}
              </span>
              <span className="text-[10px] font-mono uppercase tracking-wider text-text-muted">
                Anomalies Detected
              </span>
            </div>
          </div>

          <div className="hidden sm:block h-8 w-[1px] bg-border" aria-hidden="true" />

          <div className="flex items-center gap-3">
            <span className="w-8 h-8 rounded-md bg-sev-critical-bg border border-sev-critical-indicator/30 flex items-center justify-center shrink-0">
              <ShieldAlert className="w-4 h-4 text-sev-critical-indicator" aria-hidden="true" />
            </span>
            <div className="flex flex-col">
              <span className="text-lg font-bold tabular-nums text-sev-critical-text leading-tight font-mono">
                {criticalRisks}
              </span>
              <span className="text-[10px] font-mono uppercase tracking-wider text-text-muted">
                Critical Risks
              </span>
            </div>
          </div>

          <div className="hidden sm:block h-8 w-[1px] bg-border" aria-hidden="true" />

          <div className="flex items-center gap-3">
            <span className="w-8 h-8 rounded-md bg-ai-soft border border-ai-indigo/30 flex items-center justify-center shrink-0">
              <Sparkles className="w-4 h-4 text-ai-indigo" aria-hidden="true" />
            </span>
            <div className="flex flex-col">
              <span className="text-lg font-bold tabular-nums text-ai-indigo leading-tight font-mono">
                {investigations}
              </span>
              <span className="text-[10px] font-mono uppercase tracking-wider text-text-muted">
                AI Investigations
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* 2. Primary Dual-Panel Intelligence Workspace: Globe + Telemetry */}
      <section className="grid grid-cols-12 gap-5 min-h-[480px]">
        {/* Global Activity (Light Intelligence Globe) */}
        <motion.div
          initial={reduceMotion ? false : { opacity: 0, y: 4 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.15, ease: 'easeOut' }}
          className="col-span-12 lg:col-span-7 h-[480px]"
        >
          <CyberGlobe onSelectEvent={onOpenInvestigation} />
        </motion.div>

        {/* Live Event Feed (Telemetry Cards) */}
        <motion.div
          initial={reduceMotion ? false : { opacity: 0, y: 4 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.15, delay: reduceMotion ? 0 : 0.04, ease: 'easeOut' }}
          className="col-span-12 lg:col-span-5 h-[480px]"
        >
          <LiveStream onSelectEvent={onOpenInvestigation} />
        </motion.div>
      </section>

      {/* 3. Demo Investigations Console */}
      <section>
        <ScenarioConsole onOpenInvestigation={onOpenInvestigation} />
      </section>
    </div>
  );
}
