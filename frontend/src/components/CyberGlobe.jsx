import { useEffect, useState, useRef, useMemo } from 'react';
import Globe from 'react-globe.gl';
import { useAlerts } from '../context/AlertContext';
import { getSeverity } from '../lib/severity';
import { SeverityLegend } from './ui/severity-badge';
import { Globe2 } from 'lucide-react';

const UNASSESSED_COLOR = '#8C7A4E'; // Neutral brass

export default function CyberGlobe({ onSelectEvent, selectedEventId }) {
  const globeRef = useRef();
  const containerRef = useRef();
  const { pipelineState } = useAlerts();
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });

  // Responsive sizing tracking the parent container
  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const observer = new ResizeObserver(entries => {
      if (!entries || entries.length === 0) return;
      const { width, height } = entries[0].contentRect;
      setDimensions({ width, height: Math.max(height, 220) });
    });
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  // Compute active event points from real ALIAS pipeline telemetry
  const pointsData = useMemo(() => {
    return Object.values(pipelineState)
      .filter(state => state.LOGIN_EVENT && state.LOGIN_EVENT.latitude != null)
      .map(state => {
        const event = state.LOGIN_EVENT;
        const risk = state.RISK_ASSESSMENT;
        const isSelected = selectedEventId === event.event_id;

        const sev = risk ? getSeverity(risk.severity) : null;
        const color = isSelected ? '#B84A28' : (sev ? sev.hex : UNASSESSED_COLOR);
        const radius = isSelected ? 1.6 : (risk && risk.risk_score > 50 ? 1.3 : 0.85);

        return {
          id: event.event_id,
          lat: event.latitude,
          lng: event.longitude,
          size: radius,
          color,
          user: event.user_id,
          ip: event.ip_address,
          severity: risk ? risk.severity : 'UNASSESSED',
          score: risk ? risk.risk_score : 0,
        };
      });
  }, [pipelineState, selectedEventId]);

  // Rings around critical or selected events for clean analytical emphasis (no neon glow)
  const ringsData = useMemo(() => {
    return pointsData
      .filter(p => p.severity === 'CRITICAL' || p.id === selectedEventId)
      .map(p => ({
        lat: p.lat,
        lng: p.lng,
        maxR: 3.5,
        propagationSpeed: 1.5,
        repeatPeriod: 1200,
        color: p.id === selectedEventId ? '#B84A28' : '#C83D3D',
      }));
  }, [pointsData, selectedEventId]);

  // Turn off auto-rotation — analysts require stable points of view
  useEffect(() => {
    if (globeRef.current) {
      const controls = globeRef.current.controls();
      if (controls) {
        controls.autoRotate = false;
        controls.enableDamping = true;
      }
      globeRef.current.pointOfView({ altitude: 2.1 });
    }
  }, []);

  return (
    <div className="bg-surface border border-border h-full flex flex-col overflow-hidden shadow-xs">
      {/* Header with Title and Severity Legend */}
      <div className="px-4 py-3 border-b border-border flex items-center justify-between gap-3 bg-surface-elevated">
        <div className="flex items-center gap-2">
          <Globe2 className="w-4 h-4 text-brand-ember" aria-hidden="true" />
          <h3 className="text-xs font-semibold uppercase tracking-wider text-text-primary font-heading">
            Geographic Activity Context
          </h3>
        </div>
        <SeverityLegend className="hidden sm:flex" />
      </div>

      {/* Globe Canvas Container */}
      <div ref={containerRef} className="flex-1 min-h-0 relative bg-surface-soft/40 flex items-center justify-center overflow-hidden">
        {dimensions.width > 0 && (
          <Globe
            ref={globeRef}
            width={dimensions.width}
            height={dimensions.height}
            backgroundColor="rgba(246, 241, 228, 0)"
            globeImageUrl="//unpkg.com/three-globe/example/img/earth-day.jpg"
            showAtmosphere={false}
            pointsData={pointsData}
            pointAltitude="size"
            pointColor="color"
            pointRadius="size"
            pointResolution={16}
            pointLabel={d => `
              <div style="background:#FFFCF4; color:#23201B; padding:8px 12px; border-radius:4px; border:1px solid #DED2B4; font-family:sans-serif; font-size:11px; box-shadow:0 4px 12px rgba(23,21,18,0.12); pointer-events:none;">
                <div style="font-weight:700; color:#23201B; font-size:12px; margin-bottom:2px;">${d.user}</div>
                <div style="font-family:monospace; color:#5C5548; margin-bottom:4px;">${d.ip}</div>
                <div style="display:inline-block; font-size:10px; font-weight:700; font-family:monospace; padding:2px 6px; border-radius:2px; background:${d.color}15; color:${d.color}; border:1px solid ${d.color}40;">
                  ${d.severity} · RISK ${d.score}
                </div>
              </div>
            `}
            ringsData={ringsData}
            ringColor={d => (t) => {
              const alpha = Math.max(0, 1 - t);
              return d.color === '#B84A28'
                ? `rgba(184, 74, 40, ${alpha * 0.7})`
                : `rgba(200, 61, 61, ${alpha * 0.7})`;
            }}
            ringMaxRadius="maxR"
            ringPropagationSpeed="propagationSpeed"
            ringRepeatPeriod="repeatPeriod"
            onPointClick={(pt) => {
              if (onSelectEvent) onSelectEvent(pt.id);
            }}
          />
        )}

        {/* Analytical Overlay Cue */}
        <div className="absolute bottom-2.5 left-3 pointer-events-none bg-surface/90 backdrop-blur-xs px-2.5 py-1 rounded-sm border border-border text-3xs text-text-muted font-mono">
          Drag to rotate · Click node to inspect
        </div>
      </div>
    </div>
  );
}
