import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { createAlertWebSocket, fetchEvents, fetchInvestigations } from '../services/api';

const AlertContext = createContext();

export function AlertProvider({ children }) {
  const [connectionStatus, setConnectionStatus] = useState('connecting');
  const [eventStream, setEventStream] = useState([]);
  
  // Pipeline groups by event_id
  const [pipelineState, setPipelineState] = useState({});

  const connect = useCallback(() => {
    setConnectionStatus('connecting');
    const ws = createAlertWebSocket(
      (message) => {
        const { type, event_id, payload, timestamp } = message;
        
        // Add to raw stream
        setEventStream(prev => [{ type, event_id, timestamp, payload }, ...prev].slice(0, 500));

        // Update pipeline state
        setPipelineState(prev => {
          const current = prev[event_id] || {};
          return {
            ...prev,
            [event_id]: { ...current, [type]: payload, last_updated: timestamp }
          };
        });
      },
      () => setConnectionStatus('connected'),
      () => {
        setConnectionStatus('disconnected');
        setTimeout(connect, 3000); // auto-reconnect
      }
    );
    return ws;
  }, []);

  useEffect(() => {
    const ws = connect();
    return () => ws.close();
  }, [connect]);

  // P1 requirement: Hydrate existing Overview data from REST on reload
  // Prevents wiping KPIs, live feed, and globe to zeros on page reload.
  useEffect(() => {
    let cancelled = false;

    async function hydrateInitialState() {
      try {
        const [eventsRes, investigationsRes] = await Promise.allSettled([
          fetchEvents({ limit: 50 }),
          fetchInvestigations({ limit: 50 })
        ]);

        if (cancelled) return;

        const events = eventsRes.status === 'fulfilled' && eventsRes.value?.items ? eventsRes.value.items : [];
        const investigations = investigationsRes.status === 'fulfilled' && Array.isArray(investigationsRes.value) ? investigationsRes.value : [];

        if (events.length === 0 && investigations.length === 0) return;

        setPipelineState(prev => {
          const next = { ...prev };
          
          events.forEach(e => {
            const eid = e.id;
            const current = next[eid] || {};
            if (!current.LOGIN_EVENT) {
              next[eid] = {
                ...current,
                LOGIN_EVENT: {
                  event_id: e.id,
                  user_id: e.user_id,
                  ip_address: e.ip_address,
                  location: e.location,
                  latitude: e.latitude,
                  longitude: e.longitude,
                  timestamp: e.timestamp,
                  auth_status: e.auth_status,
                  access_pattern: e.access_pattern,
                  device_fingerprint: e.device_fingerprint,
                  failed_attempts: e.failed_attempts,
                  user_agent: e.user_agent,
                },
                last_updated: current.last_updated || e.timestamp,
              };
            }
          });

          investigations.forEach(inv => {
            const eid = inv.event_id;
            const current = next[eid] || {};
            next[eid] = {
              ...current,
              INVESTIGATION_REPORT: inv,
              RISK_ASSESSMENT: current.RISK_ASSESSMENT || (inv.risk_score != null ? {
                risk_score: inv.risk_score,
                severity: inv.severity,
                explanation: inv.summary,
              } : null),
              last_updated: current.last_updated || inv.created_at,
            };
          });

          return next;
        });

        setEventStream(prev => {
          if (prev.length > 0) return prev;
          const streamItems = [];
          events.forEach(e => {
            streamItems.push({
              type: 'LOGIN_EVENT',
              event_id: e.id,
              timestamp: e.timestamp,
              payload: e,
            });
          });
          investigations.forEach(inv => {
            streamItems.push({
              type: 'INVESTIGATION_REPORT',
              event_id: inv.event_id,
              timestamp: inv.created_at,
              payload: inv,
            });
          });
          streamItems.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
          return streamItems.slice(0, 500);
        });
      } catch (err) {
        console.warn('[ALIAS] Initial state hydration skipped:', err);
      }
    }

    hydrateInitialState();
    return () => { cancelled = true; };
  }, []);

  const [demoRuns, setDemoRuns] = useState({});

  // Clears locally-accumulated stream/pipeline state without touching the WebSocket
  // connection itself — used after a demo reset so the UI reflects the backend's
  // actual (now-empty) demo data instead of continuing to show deleted events.
  const clearStream = useCallback(() => {
    setEventStream([]);
    setPipelineState({});
    setDemoRuns({});
  }, []);

  return (
    <AlertContext.Provider value={{ connectionStatus, eventStream, pipelineState, clearStream, demoRuns, setDemoRuns }}>
      {children}
    </AlertContext.Provider>
  );
}

export const useAlerts = () => useContext(AlertContext);
