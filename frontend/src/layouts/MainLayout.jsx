import React from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import { useAlerts } from '../context/AlertContext';
import { Activity, ShieldCheck, Wifi, WifiOff, FileText, Compass, LogIn } from 'lucide-react';
import { cn } from '../lib/utils';

const NAV_ITEMS = [
  { id: 'dashboard', label: 'Overview', icon: Compass },
  { id: 'investigations', label: 'Investigations', icon: FileText },
  { id: 'portal', label: 'Login Portal', icon: LogIn, badge: 'Demo' },
];

export default function MainLayout({ children, activeView, setView, title, viewKey }) {
  const { connectionStatus } = useAlerts();
  const isLive = connectionStatus === 'connected';
  const reduceMotion = useReducedMotion();

  return (
    <div className="flex h-screen bg-canvas text-text-primary overflow-hidden font-sans">
      {/* Sidebar — White background, crisp architectural borders, ember active states */}
      <aside className="w-64 shrink-0 border-r border-border bg-surface flex flex-col justify-between z-20">
        <div>
          {/* Brand header */}
          <div className="h-16 px-5 flex items-center border-b border-border bg-surface">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-md bg-brand-soft border border-brand-ember/30 flex items-center justify-center text-brand-ember">
                <ShieldCheck className="w-5 h-5" aria-hidden="true" />
              </div>
              <div className="flex flex-col">
                <span className="text-base font-bold tracking-tight text-text-primary leading-none">ALIAS</span>
                <span className="text-[10px] font-mono tracking-wider uppercase text-text-muted mt-0.5">Security Intelligence</span>
              </div>
            </div>
          </div>

          <div className="px-5 py-3 border-b border-border bg-surface-elevated/50">
            <p className="text-[11px] leading-relaxed text-text-secondary">
              AI-assisted Login Investigation
            </p>
          </div>

          {/* Primary Navigation */}
          <nav className="p-3 space-y-1" aria-label="Primary">
            {NAV_ITEMS.map(item => {
              const active = activeView === item.id;
              return (
                <button
                  key={item.id}
                  type="button"
                  aria-current={active ? 'page' : undefined}
                  onClick={() => setView(item.id)}
                  className={cn(
                    "w-full flex items-center gap-3 px-3.5 py-2.5 text-xs rounded-md transition-all outline-none",
                    "focus-visible:ring-2 focus-visible:ring-focus",
                    active
                      ? "bg-brand-soft text-text-primary font-semibold border-l-3 border-brand-ember shadow-xs"
                      : "text-text-secondary hover:text-text-primary hover:bg-surface-soft font-medium"
                  )}
                >
                  <item.icon className={cn("w-4 h-4 shrink-0", active ? "text-brand-ember" : "text-text-muted")} aria-hidden="true" />
                  <span>{item.label}</span>
                  {item.badge && (
                    <span className="ml-auto text-[9px] font-mono uppercase px-1.5 py-0.5 rounded bg-brand-soft text-brand-ember border border-brand-ember/30 font-bold">
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>

        {/* System Status Block (Restrained, no neon/cyberpunk) */}
        <div className="p-4 border-t border-border bg-surface-elevated">
          <div className="text-[10px] font-mono uppercase tracking-widest text-text-muted font-semibold mb-1.5">
            System Status
          </div>
          <div className="flex items-center gap-2 text-xs font-medium text-text-primary">
            <span className="w-2 h-2 rounded-full bg-sev-low-indicator shrink-0" aria-hidden="true" />
            <span>Operational</span>
            <span className="text-[10px] text-text-muted ml-auto font-mono">v1.2</span>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 bg-canvas">
        {/* Top Header */}
        <header className="h-14 shrink-0 border-b border-border bg-surface flex items-center justify-between px-6 gap-4 z-10">
          <div className="flex items-center gap-3 min-w-0">
            <span className="text-sm font-semibold text-text-primary whitespace-nowrap">
              ALIAS
            </span>
            <span className="text-text-muted text-xs">/</span>
            <span className="text-xs font-medium text-text-secondary whitespace-nowrap">
              {title || (activeView === 'investigations' ? 'Forensic Investigations' : 'Security Intelligence Workspace')}
            </span>
            <div className="hidden md:flex items-center gap-1.5 px-2 py-0.5 rounded bg-surface-soft text-text-muted border border-border text-[10px] tracking-wider uppercase shrink-0 font-mono">
              <span className="w-1.5 h-1.5 rounded-full bg-brand-ember" aria-hidden="true" />
              Synthetic Telemetry
            </div>
          </div>

          {/* Connection Status indicator */}
          <div
            className="flex items-center gap-2 px-2.5 py-1 rounded-md bg-surface-elevated border border-border text-xs font-mono shrink-0"
            role="status"
            aria-label={isLive ? 'Live alert gateway connected' : 'Alert gateway disconnected (reconnecting)'}
          >
            <span className="text-[10px] font-bold tracking-wider text-text-muted uppercase">LIVE</span>
            <span
              className={cn(
                "w-2 h-2 rounded-full",
                isLive ? "bg-sev-low-indicator" : "bg-sev-moderate-indicator"
              )}
              aria-hidden="true"
            />
            <span className="text-text-secondary font-sans text-xs">
              {isLive ? 'Connected' : 'Reconnecting...'}
            </span>
          </div>
        </header>

        {/* Dynamic Viewport */}
        <motion.main
          key={viewKey ?? activeView}
          initial={reduceMotion ? false : { opacity: 0, y: 3 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.15, ease: 'easeOut' }}
          className="flex-1 overflow-auto p-6 min-h-0 bg-canvas"
        >
          {children}
        </motion.main>
      </div>
    </div>
  );
}
