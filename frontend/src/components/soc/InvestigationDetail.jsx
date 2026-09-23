import { Cpu, ArrowDown, ShieldCheck, AlertCircle, FileText, CheckCircle2 } from 'lucide-react';
import { cn } from '../../lib/utils';
import { getSeverity } from '../../lib/severity';
import { SeverityBadge } from '../ui/severity-badge';
import EvidenceSection from './EvidenceSection';

/**
 * ALIAS Evidence Body:
 * 01 Observed Fact -> 02 Deterministic Findings -> 03 Correlated Risk -> 04 AI Interpretation
 */
export default function InvestigationDetail({ eventState, anomaliesState, riskState, reportState }) {
  const event = eventState.data;
  const anomalies = anomaliesState.data;
  const risk = riskState.data;
  const report = reportState.data;

  return (
    <div className="flex flex-col gap-6">

      {/* 01. Observed Fact (Neutral White Surface) */}
      <EvidenceSection
        number={1}
        title="Observed Fact"
        numberBg="bg-surface-soft text-text-primary border-border"
        subtitle="Raw authentication telemetry ingested into the baseline comparison pipeline"
        status={eventState.status}
        errorMessage="Failed to load event details."
      >
        {event && (
          <div className="bg-surface border border-border rounded-lg p-5 shadow-xs">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-y-4 gap-x-6 text-xs">
              <div className="flex flex-col gap-1">
                <span className="text-[10px] font-mono uppercase tracking-wider text-text-muted">IP Address</span>
                <span className="font-mono text-sm font-semibold text-text-primary">{event.ip_address}</span>
              </div>

              <div className="flex flex-col gap-1">
                <span className="text-[10px] font-mono uppercase tracking-wider text-text-muted">Resolved Location</span>
                <span className="text-sm font-medium text-text-primary">{event.location || 'Unknown Region'}</span>
              </div>

              <div className="flex flex-col gap-1">
                <span className="text-[10px] font-mono uppercase tracking-wider text-text-muted">Authentication Result</span>
                <span className={cn(
                  "font-mono font-bold text-xs inline-flex items-center gap-1.5 px-2 py-0.5 rounded w-fit",
                  event.auth_status === 'SUCCESS' ? "bg-sev-low-bg text-sev-low-text border border-sev-low-indicator/30" : "bg-sev-critical-bg text-sev-critical-text border border-sev-critical-indicator/30"
                )}>
                  {event.auth_status === 'SUCCESS' ? <CheckCircle2 className="w-3 h-3" /> : <AlertCircle className="w-3 h-3" />}
                  {event.auth_status}
                </span>
              </div>

              <div className="flex flex-col gap-1">
                <span className="text-[10px] font-mono uppercase tracking-wider text-text-muted">Access Route</span>
                <span className="font-mono text-xs font-medium text-text-primary">{event.access_pattern || 'DIRECT'}</span>
              </div>

              {event.device_fingerprint && (
                <div className="flex flex-col gap-1">
                  <span className="text-[10px] font-mono uppercase tracking-wider text-text-muted">Device Identifier</span>
                  <span className="font-mono text-xs text-text-secondary truncate">{event.device_fingerprint}</span>
                </div>
              )}

              {event.failed_attempts > 0 && (
                <div className="flex flex-col gap-1">
                  <span className="text-[10px] font-mono uppercase tracking-wider text-text-muted">Prior Failed Attempts</span>
                  <span className="font-mono font-bold text-sev-critical-text">{event.failed_attempts} attempt{event.failed_attempts === 1 ? '' : 's'}</span>
                </div>
              )}

              <div className="flex flex-col gap-1 md:col-span-2 lg:col-span-3 pt-2 border-t border-border/60">
                <span className="text-[10px] font-mono uppercase tracking-wider text-text-muted">Client User Agent</span>
                <span className="font-mono text-[11px] text-text-secondary break-all bg-surface-soft p-2 rounded border border-border">
                  {event.user_agent || 'Unknown UA Header'}
                </span>
              </div>
            </div>
          </div>
        )}
      </EvidenceSection>

      {/* 02. Deterministic Findings (Neutral + Semantic Cues) */}
      <EvidenceSection
        number={2}
        title="Deterministic Findings"
        numberBg="bg-sev-moderate-bg text-sev-moderate-text border-sev-moderate-indicator/30"
        subtitle="Rule-based statistical anomalies detected against user behavioral baseline"
        status={anomaliesState.status}
        errorMessage="Failed to load anomaly findings."
        emptyMessage={`No behavioral deviations detected against baseline profile ${anomalies?.baseline_version?.substring(0, 8) || ''}. Normal authentication posture.`}
      >
        <div className="space-y-3">
          {anomalies?.anomalies?.map(anom => (
            <div key={anom.anomaly_id} className="p-4 border border-border bg-surface rounded-lg shadow-xs flex flex-col gap-2">
              <div className="flex justify-between items-start gap-3">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-brand-ember shrink-0" aria-hidden="true" />
                  <span className="text-xs font-bold text-text-primary uppercase tracking-wide">
                    {anom.anomaly_type}
                  </span>
                </div>
                <span className="text-[10px] font-mono text-text-muted bg-surface-soft px-2 py-0.5 rounded border border-border shrink-0">
                  {anom.rule_id}
                </span>
              </div>

              <p className="text-xs text-text-secondary leading-relaxed">
                {anom.explanation}
              </p>

              <div className="mt-1 pt-2 border-t border-border/60 text-[11px] grid grid-cols-1 sm:grid-cols-2 gap-2 bg-surface-soft/50 p-2.5 rounded border border-border/40 font-mono">
                <div>
                  <span className="text-text-muted">Observed Value: </span>
                  <span className="font-semibold text-text-primary">{anom.observed_value}</span>
                </div>
                <div>
                  <span className="text-text-muted">Expected Baseline: </span>
                  <span className="font-semibold text-text-secondary">{anom.expected_state}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </EvidenceSection>

      {/* 03. Correlated Risk (Strong Security Emphasis) */}
      <EvidenceSection
        number={3}
        title="Correlated Risk"
        numberBg="bg-sev-critical-bg text-sev-critical-text border-sev-critical-indicator/30"
        subtitle="Multi-signal correlation engine synthesized risk score and severity level"
        status={riskState.status}
        errorMessage="Failed to load the risk assessment."
        emptyMessage="No risk assessment — no behavioral anomalies were detected for this event."
      >
        {risk && (
          <div className="p-5 border border-border bg-surface rounded-lg shadow-xs flex flex-col gap-4">
            <div className="flex items-start gap-4">
              <div className="flex flex-col items-center justify-center p-3 bg-surface-soft rounded-lg border border-border w-20 h-20 shrink-0">
                <span className={cn("text-2xl font-bold font-mono", getSeverity(risk.severity).text)}>
                  {risk.risk_score}
                </span>
                <span className={cn("text-[9px] font-mono font-bold uppercase", getSeverity(risk.severity).text)}>
                  {risk.severity}
                </span>
              </div>

              <div className="flex-1 min-w-0">
                <h4 className="text-xs font-bold text-text-primary uppercase tracking-wide mb-1">
                  Multi-Signal Risk Synthesis
                </h4>
                <p className="text-xs text-text-secondary leading-relaxed">
                  {risk.explanation}
                </p>
              </div>
            </div>

            {/* Correlation Factors Chain */}
            {risk.correlation_factors?.length > 0 && (
              <div className="pt-3 border-t border-border">
                <h5 className="text-[10px] font-mono uppercase tracking-widest text-text-muted font-bold mb-2">
                  Correlation Chain Factors
                </h5>
                <div className="space-y-2">
                  {risk.correlation_factors.map((cf, i) => (
                    <div key={cf.factor_id || i} className="flex items-start gap-2.5 p-2.5 rounded-md bg-surface-soft border border-border">
                      <ArrowDown className="w-3.5 h-3.5 text-brand-ember mt-0.5 shrink-0" aria-hidden="true" />
                      <div className="text-xs">
                        <span className="font-semibold text-text-primary">{cf.name}</span>
                        {cf.description && <p className="text-text-secondary text-[11px] mt-0.5">{cf.description}</p>}
                        {cf.related_anomaly_ids?.length > 0 && (
                          <span className="text-[10px] font-mono text-text-muted mt-1 inline-block">
                            Correlates {cf.related_anomaly_ids.length} anomaly finding{cf.related_anomaly_ids.length === 1 ? '' : 's'}
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </EvidenceSection>

      {/* 04. AI Forensic Interpretation (Quarantined Indigo Treatment) */}
      <EvidenceSection
        number={4}
        title="AI Interpretation"
        numberBg="bg-ai-soft text-ai-indigo border-ai-indigo/30"
        subtitle="Forensic summary synthesized strictly from the deterministic evidence above. Not an autonomous detection."
        status={reportState.status}
        errorMessage="Failed to load the AI investigation."
        emptyMessage="No AI investigation was triggered — risk did not meet the automated investigation threshold (risk score < 1)."
      >
        {report && (
          <div className="p-5 border border-ai-indigo/30 bg-ai-soft/40 rounded-lg shadow-xs flex flex-col gap-4">
            {/* AI Top Header with Provider Badge */}
            <div className="flex justify-between items-center pb-3 border-b border-ai-indigo/20 gap-3 flex-wrap">
              <span className="text-xs text-ai-indigo font-mono font-bold flex items-center gap-1.5">
                <Cpu className="w-4 h-4 text-ai-indigo shrink-0" aria-hidden="true" />
                {report.llm_provider === 'mock-fallback' || report.llm_provider === 'none'
                  ? 'Deterministic template (no LLM key configured)'
                  : report.llm_provider === 'google'
                  ? 'Google Gemini Forensic Synthesis (API)'
                  : report.llm_provider === 'openai'
                  ? 'OpenAI GPT-4o Forensic Synthesis (API)'
                  : report.llm_provider}
              </span>
              <SeverityBadge severity={report.severity} />
            </div>

            {/* AI Synthesis Summary */}
            <div className="prose prose-sm max-w-none text-text-primary text-xs leading-relaxed space-y-3">
              <p>{report.summary}</p>

              {report.recommendations?.length > 0 && (
                <div className="mt-3 pt-3 border-t border-ai-indigo/15">
                  <strong className="text-[10px] font-mono uppercase tracking-wider text-ai-indigo block mb-2">
                    Recommended Security Actions:
                  </strong>
                  <ul className="space-y-1.5 text-xs list-disc pl-4 text-text-secondary">
                    {report.recommendations.map((rec, i) => (
                      <li key={i}>{rec}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* AI Mandatory Legal/Technical Disclaimer */}
            <div className="pt-3 border-t border-ai-indigo/20 text-[10px] text-text-muted leading-relaxed font-mono">
              Notice: AI interpretations are generated exclusively from the deterministic baseline anomalies and correlated risk factors established above. The AI layer does not calculate risk scores or declare compromise verdicts independently.
            </div>
          </div>
        )}
      </EvidenceSection>

    </div>
  );
}
