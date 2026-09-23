import { useEffect, useState } from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import { fetchEvent, fetchEventAnomalies, fetchEventRisk, fetchInvestigation } from '../services/api';
import InvestigationHeader from '../components/soc/InvestigationHeader';
import InvestigationDetail from '../components/soc/InvestigationDetail';

const LOADING = { status: 'loading', data: null };

/**
 * The Investigation surface — "why is this event suspicious?"
 * Owns progressive fetching for all four evidence stages; each stage
 * resolves independently (loading -> success/empty/error) rather than
 * blocking on the others.
 */
export default function InvestigationWorkspace({ eventId, onBack, origin = 'overview' }) {
  const [eventState, setEventState] = useState(LOADING);
  const [anomaliesState, setAnomaliesState] = useState(LOADING);
  const [riskState, setRiskState] = useState(LOADING);
  const [reportState, setReportState] = useState(LOADING);
  const reduceMotion = useReducedMotion();

  useEffect(() => {
    let cancelled = false;
    setEventState(LOADING);
    setAnomaliesState(LOADING);
    setRiskState(LOADING);
    setReportState(LOADING);

    fetchEvent(eventId)
      .then(data => { if (!cancelled) setEventState({ status: 'success', data }); })
      .catch(() => { if (!cancelled) setEventState({ status: 'error', data: null }); });

    fetchEventAnomalies(eventId)
      .then(data => {
        if (cancelled) return;
        setAnomaliesState({ status: 'success', data });
        if (!data.has_anomalies) {
          setRiskState({ status: 'empty', data: null });
          setReportState({ status: 'empty', data: null });
          return;
        }
        fetchEventRisk(eventId)
          .then(risk => {
            if (cancelled) return;
            setRiskState({ status: 'success', data: risk });
            if (!(risk.risk_score > 0)) {
              setReportState({ status: 'empty', data: null });
              return;
            }
            fetchInvestigation(eventId)
              .then(report => { if (!cancelled) setReportState({ status: 'success', data: report }); })
              .catch(() => { if (!cancelled) setReportState({ status: 'error', data: null }); });
          })
          .catch(() => {
            if (cancelled) return;
            setRiskState({ status: 'error', data: null });
            setReportState({ status: 'empty', data: null });
          });
      })
      .catch(() => {
        if (cancelled) return;
        setAnomaliesState({ status: 'error', data: null });
        setRiskState({ status: 'empty', data: null });
        setReportState({ status: 'empty', data: null });
      });

    return () => { cancelled = true; };
  }, [eventId]);

  return (
    <motion.div
      initial={reduceMotion ? false : { opacity: 0, y: 4 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.15, ease: 'easeOut' }}
      className="h-full overflow-y-auto flex flex-col gap-6 max-w-5xl mx-auto pb-12"
    >
      <InvestigationHeader eventState={eventState} riskState={riskState} onBack={onBack} origin={origin} />

      <InvestigationDetail
        eventState={eventState}
        anomaliesState={anomaliesState}
        riskState={riskState}
        reportState={reportState}
      />
    </motion.div>
  );
}
