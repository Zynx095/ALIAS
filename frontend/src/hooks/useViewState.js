import { useState, useCallback, useEffect } from 'react';

/**
 * Lightweight, dependency-free URL sync for the three ALIAS surfaces.
 * Not a routing library — just enough History API to make an investigation
 * linkable/back-button-able without pulling in react-router. See R6 report
 * ("URL State") for what this does and doesn't cover.
 *
 * /dashboard              -> { name: 'overview' }
 * /investigations         -> { name: 'history' }
 * /investigations/:eventId -> { name: 'investigation', eventId }
 */
function parseLocation() {
  const path = window.location.pathname;
  const investigationMatch = path.match(/^\/investigations\/([^/]+)$/);
  if (investigationMatch) return { name: 'investigation', eventId: investigationMatch[1] };
  if (path === '/investigations') return { name: 'history' };
  if (path === '/portal') return { name: 'portal' };
  return { name: 'overview' };
}

function pathFor(view) {
  if (view.name === 'investigation') return `/investigations/${view.eventId}`;
  if (view.name === 'history') return '/investigations';
  if (view.name === 'portal') return '/portal';
  return '/dashboard';
}

export function useViewState() {
  const [view, setView] = useState(parseLocation);

  useEffect(() => {
    const onPopState = () => setView(parseLocation());
    window.addEventListener('popstate', onPopState);
    return () => window.removeEventListener('popstate', onPopState);
  }, []);

  const navigate = useCallback((next) => {
    setView(next);
    const path = pathFor(next);
    if (window.location.pathname !== path) {
      window.history.pushState(null, '', path);
    }
  }, []);

  return [view, navigate];
}
