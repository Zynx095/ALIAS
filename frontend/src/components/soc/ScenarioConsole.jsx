import { useState, useEffect, useRef, useCallback } from 'react';
import { Play, RotateCcw, Loader2, CheckCircle2, XCircle, ArrowRight, FlaskConical, Layers } from 'lucide-react';
import { fetchScenarios, runScenario, resetDemo, fetchEventRisk, fetchInvestigation } from '../../services/api';
import { useAlerts } from '../../context/AlertContext';
import { cn } from '../../lib/utils';
import { SeverityBadge } from '../ui/severity-badge';

const RESET_ARM_TIMEOUT_MS = 4000;
const SLOW_RUN_HINT_MS = 15000;

const SCENARIO_META = {
  normal_login: { index: '01', subtitle: 'Control baseline scenario', defaultSev: 'LOW' },
  new_device: { index: '02', subtitle: 'Device deviation anomaly', defaultSev: 'LOW' },
  impossible_travel: { index: '03', subtitle: 'Location velocity deviation', defaultSev: 'MODERATE' },
  auth_burst: { index: '04', subtitle: 'Authentication frequency anomaly', defaultSev: 'MODERATE' },
  multi_signal: { index: '05', subtitle: 'Correlated multi-signal compromise', defaultSev: 'CRITICAL' },
  unseen_network: { index: '06', subtitle: 'Unseen network subnet deviation', defaultSev: 'MODERATE' },
};

/**
 * Derives a scenario run's real completion state from the WebSocket pipeline.
 * RISK_ASSESSMENT is broadcast unconditionally for every event;
 * ANOMALY_DETECTED only when anomalies exist;
 * INVESTIGATION_REPORT only when risk_score > 0.
 */
function isTargetEventComplete(pipelineState, targetEventId) {
  const state = pipelineState[targetEventId];
  if (!state?.RISK_ASSESSMENT) return false;
  if (state.RISK_ASSESSMENT.risk_score > 0 && !state.INVESTIGATION_REPORT) return false;
  return true;
}

const initialRunState = { status: 'idle', targetEventId: null, error: null, startedAt: null };

export default function ScenarioConsole({ onOpenInvestigation }) {
  const { pipelineState, clearStream, connectionStatus, demoRuns: runs, setDemoRuns: setRuns } = useAlerts();
  const [scenarios, setScenarios] = useState([]);
  const [resetArmed, setResetArmed] = useState(false);
  const [isResetting, setIsResetting] = useState(false);
  const [now, setNow] = useState(Date.now());
  const resetArmTimer = useRef(null);

  useEffect(() => {
    fetchScenarios()
      .then(data => {
        // Sort deterministically 01 through 06
        const sorted = [...data].sort((a, b) => {
          const idxA = SCENARIO_META[a.scenario_id]?.index || '99';
          const idxB = SCENARIO_META[b.scenario_id]?.index || '99';
          return idxA.localeCompare(idxB);
        });
        setScenarios(sorted);
      })
      .catch(err => console.error('[ALIAS] Failed to fetch scenarios:', err));
  }, []);

  const anyRunning = Object.values(runs).some(r => r.status === 'running');

  // Elapsed timer tick for active runs
  useEffect(() => {
    if (!anyRunning) return;
    const id = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(id);
  }, [anyRunning]);

  // Watch WebSocket-driven pipelineState for in-flight completion
  useEffect(() => {
    setRuns(prev => {
      let changed = false;
      const next = { ...prev };
      for (const [scenarioId, run] of Object.entries(prev)) {
        if (run.status === 'running' && run.targetEventId != null && isTargetEventComplete(pipelineState, run.targetEventId)) {
          next[scenarioId] = { ...run, status: 'completed' };
          changed = true;
        }
      }
      return changed ? next : prev;
    });
  }, [pipelineState]);

  // WebSocket reconnect resync
  const prevConnectionStatus = useRef(connectionStatus);
  useEffect(() => {
    const wasConnected = prevConnectionStatus.current === 'connected';
    prevConnectionStatus.current = connectionStatus;
    if (wasConnected || connectionStatus !== 'connected') return;

    Object.entries(runs)
      .filter(([, r]) => r.status === 'running' && r.targetEventId != null)
      .forEach(async ([scenarioId, run]) => {
        try {
          const risk = await fetchEventRisk(run.targetEventId);
          if (!(risk.risk_score > 0)) {
            setRuns(prev => (prev[scenarioId]?.status === 'running' ? { ...prev, [scenarioId]: { ...prev[scenarioId], status: 'completed' } } : prev));
            return;
          }
          await fetchInvestigation(run.targetEventId);
          setRuns(prev => (prev[scenarioId]?.status === 'running' ? { ...prev, [scenarioId]: { ...prev[scenarioId], status: 'completed' } } : prev));
        } catch {
          // Genuinely still running
        }
      });
  }, [connectionStatus]);

  const handleRun = useCallback(async (scenarioId) => {
    setRuns(prev => ({ ...prev, [scenarioId]: { status: 'running', targetEventId: null, error: null, startedAt: Date.now() } }));
    try {
      const data = await runScenario(scenarioId);
      const eventIds = data?.results?.event_ids || [];
      const targetEventId = eventIds.length > 0 ? eventIds[eventIds.length - 1] : null;
      if (targetEventId == null) {
        setRuns(prev => ({ ...prev, [scenarioId]: { status: 'failed', targetEventId: null, error: 'Produced no trackable event.', startedAt: null } }));
        return;
      }
      setRuns(prev => ({ ...prev, [scenarioId]: { ...prev[scenarioId], targetEventId } }));
    } catch (err) {
      setRuns(prev => ({ ...prev, [scenarioId]: { status: 'failed', targetEventId: null, error: err.message, startedAt: null } }));
    }
  }, []);

  const handleResetClick = async () => {
    if (!resetArmed) {
      setResetArmed(true);
      resetArmTimer.current = setTimeout(() => setResetArmed(false), RESET_ARM_TIMEOUT_MS);
      return;
    }
    clearTimeout(resetArmTimer.current);
    setResetArmed(false);
    setIsResetting(true);
    try {
      await resetDemo();
      clearStream();
    } catch (err) {
      console.error('[ALIAS] Reset failed:', err);
    } finally {
      setIsResetting(false);
    }
  };

  return (
    <div className="bg-surface border border-border rounded-lg p-5 flex flex-col shadow-xs">
      {/* Console Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 mb-4 border-b border-border">
        <div>
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-brand-ember" aria-hidden="true" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-text-primary">
              Demo Investigations
            </h3>
          </div>
          <p className="text-xs text-text-secondary mt-0.5">
            Trigger deterministic attack simulations and behavioral baseline anomalies
          </p>
        </div>

        {/* Two-Click Armed Reset Demo Button */}
        <button
          type="button"
          onClick={handleResetClick}
          disabled={isResetting || anyRunning}
          className={cn(
            "flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all outline-none",
            "focus-visible:ring-2 focus-visible:ring-focus shrink-0",
            resetArmed
              ? "bg-sev-critical-bg text-sev-critical-text border border-sev-critical-indicator shadow-xs font-semibold"
              : "bg-surface-elevated text-text-secondary border border-border hover:text-text-primary hover:border-border-strong",
            (isResetting || anyRunning) && "opacity-50 cursor-not-allowed"
          )}
        >
          {isResetting ? <Loader2 className="w-3.5 h-3.5 animate-spin" aria-hidden="true" /> : <RotateCcw className="w-3.5 h-3.5" aria-hidden="true" />}
          {resetArmed ? 'Confirm Reset All Data?' : 'Reset Environment'}
        </button>
      </div>

      {/* Grid of 6 Investigation Scenarios */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-3">
        {scenarios.map((scen, idx) => {
          const run = runs[scen.scenario_id] || initialRunState;
          const meta = SCENARIO_META[scen.scenario_id] || {
            index: String(idx + 1).padStart(2, '0'),
            subtitle: scen.description,
            defaultSev: 'LOW',
          };
          const isRunning = run.status === 'running';
          const isCompleted = run.status === 'completed';
          const isFailed = run.status === 'failed';
          const elapsedSec = run.startedAt ? Math.floor((now - run.startedAt) / 1000) : 0;

          return (
            <div
              key={scen.scenario_id}
              className={cn(
                "p-3.5 rounded-md border bg-surface flex flex-col justify-between gap-3 transition-all",
                "hover:border-border-strong hover:bg-surface-elevated shadow-2xs",
                isRunning && "border-brand-ember bg-brand-soft/20 ring-1 ring-brand-ember",
                isCompleted && "border-sev-low-indicator/40 bg-sev-low-bg/10"
              )}
            >
              <div>
                {/* Top Number + Expected Severity */}
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-[10px] font-mono font-bold text-text-muted bg-surface-soft px-1.5 py-0.5 rounded border border-border">
                    [{meta.index}]
                  </span>
                  <SeverityBadge severity={meta.defaultSev} className="text-[9px] px-1.5 py-0.2" />
                </div>

                {/* Scenario Title */}
                <h4 className="text-xs font-bold text-text-primary leading-tight mt-1">
                  {scen.scenario_name}
                </h4>

                {/* Subtitle / Deviation */}
                <p className="text-[11px] text-text-secondary leading-snug mt-1">
                  {meta.subtitle}
                </p>
              </div>

              {/* Action / State Button */}
              <div className="pt-2 border-t border-border/60">
                {isRunning ? (
                  <div className="flex items-center justify-between text-xs text-brand-ember font-mono py-1 px-2 rounded bg-brand-soft border border-brand-ember/30">
                    <span className="flex items-center gap-1.5 text-[11px] font-semibold">
                      <Loader2 className="w-3 h-3 animate-spin shrink-0" aria-hidden="true" />
                      Running
                    </span>
                    <span className="text-[10px]">{elapsedSec}s</span>
                  </div>
                ) : isCompleted ? (
                  <button
                    type="button"
                    onClick={() => onOpenInvestigation(run.targetEventId, 'overview')}
                    className="w-full flex items-center justify-center gap-1 py-1.5 px-2 rounded text-[11px] font-semibold text-text-primary bg-surface-soft border border-border hover:bg-brand-soft hover:border-brand-ember hover:text-brand-ember transition-colors outline-none focus-visible:ring-2 focus-visible:ring-focus"
                  >
                    <span>Inspect</span>
                    <ArrowRight className="w-3 h-3" aria-hidden="true" />
                  </button>
                ) : isFailed ? (
                  <div className="flex items-center gap-1 text-[11px] text-sev-critical-text py-1">
                    <XCircle className="w-3.5 h-3.5 shrink-0" aria-hidden="true" />
                    <span className="truncate">{run.error || 'Failed'}</span>
                  </div>
                ) : (
                  <button
                    type="button"
                    onClick={() => handleRun(scen.scenario_id)}
                    disabled={anyRunning}
                    className={cn(
                      "w-full flex items-center justify-center gap-1.5 py-1.5 px-2.5 rounded text-xs font-medium transition-all outline-none",
                      "focus-visible:ring-2 focus-visible:ring-focus",
                      anyRunning
                        ? "bg-surface-soft text-text-muted cursor-not-allowed border border-border"
                        : "bg-surface text-text-primary border border-border hover:border-brand-ember hover:text-brand-ember hover:bg-brand-soft/30 shadow-2xs"
                    )}
                  >
                    <Play className="w-3 h-3 text-brand-ember" aria-hidden="true" />
                    <span>Run</span>
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
