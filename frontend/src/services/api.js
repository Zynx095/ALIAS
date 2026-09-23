/**
 * ALIAS API Client
 * Centralized API communication layer.
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const WS_BASE = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

export const API_ENDPOINTS = {
  health: `${API_BASE}/health`,
  events: `${API_BASE}/api/events`,
  loginEvent: `${API_BASE}/api/events/login`,
  investigations: `${API_BASE}/api/investigations`,
  baselines: `${API_BASE}/api/users`,
  scenarios: `${API_BASE}/api/scenarios`,
  wsAlerts: `${WS_BASE}/ws/alerts`,
};

export async function apiFetch(url, options = {}) {
  const defaultHeaders = { 'Content-Type': 'application/json' };
  const config = {
    ...options,
    headers: { ...defaultHeaders, ...options.headers },
  };

  const response = await fetch(url, config);
  if (!response.ok) {
    let errorMessage = `API Error: ${response.status}`;
    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorMessage;
    } catch(e) {}
    throw new Error(errorMessage);
  }
  return response.json();
}

export async function submitLoginEvent(eventData) {
  return apiFetch(API_ENDPOINTS.loginEvent, {
    method: 'POST',
    body: JSON.stringify(eventData),
  });
}

export async function fetchEvents({ skip = 0, limit = 50 } = {}) {
  return apiFetch(`${API_ENDPOINTS.events}?skip=${skip}&limit=${limit}`);
}

export async function fetchEvent(eventId) {
  return apiFetch(`${API_ENDPOINTS.events}/${eventId}`);
}

export async function fetchEventAnomalies(eventId) {
  return apiFetch(`${API_ENDPOINTS.events}/${eventId}/anomalies`);
}

export async function fetchEventRisk(eventId) {
  return apiFetch(`${API_ENDPOINTS.events}/${eventId}/risk`);
}

export async function fetchInvestigation(eventId) {
  return apiFetch(`${API_ENDPOINTS.investigations}/events/${eventId}`);
}

export async function fetchInvestigations({ skip = 0, limit = 50 } = {}) {
  return apiFetch(`${API_ENDPOINTS.investigations}?skip=${skip}&limit=${limit}`);
}

export async function triggerInvestigation(eventId) {
  return apiFetch(`${API_ENDPOINTS.investigations}/events/${eventId}/investigate`, {
    method: 'POST',
    body: JSON.stringify({ force_reevaluate: false })
  });
}

export async function fetchScenarios() {
  return apiFetch(API_ENDPOINTS.scenarios);
}

export async function runScenario(scenarioId) {
  return apiFetch(`${API_ENDPOINTS.scenarios}/${scenarioId}/run`, { method: 'POST' });
}

export async function resetDemo() {
  return apiFetch(`${API_ENDPOINTS.scenarios}/reset`, { method: 'POST' });
}

export function createAlertWebSocket(onMessage, onOpen, onClose) {
  const ws = new WebSocket(API_ENDPOINTS.wsAlerts);
  ws.onopen = () => {
    console.log('[ALIAS] WebSocket connected');
    if (onOpen) onOpen();
  };
  ws.onclose = () => {
    console.log('[ALIAS] WebSocket disconnected');
    if (onClose) onClose();
  };
  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      if (onMessage) onMessage(data);
    } catch (err) {
      console.error('[ALIAS] WebSocket parse error:', err);
    }
  };
  return ws;
}

export async function fetchPortalConfig() {
  return apiFetch(`${API_BASE}/api/portal/config`);
}

export async function submitPortalLogin(payload) {
  return apiFetch(`${API_BASE}/api/portal/login`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function resetPortalCounters() {
  return apiFetch(`${API_BASE}/api/portal/reset-counters`, {
    method: 'POST',
  });
}

