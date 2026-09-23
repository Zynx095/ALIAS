import React, { useState, useEffect } from 'react';
import {
  ShieldCheck,
  Lock,
  User,
  MapPin,
  Smartphone,
  Laptop,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  ArrowRight,
  RotateCcw,
  Loader2,
  Globe2,
  Sparkles,
  KeyRound,
  Eye,
  EyeOff
} from 'lucide-react';
import { fetchPortalConfig, submitPortalLogin, resetPortalCounters } from '../services/api';
import { cn } from '../lib/utils';

export default function LoginPortal({ onOpenInvestigation, onGoOverview }) {
  const [config, setConfig] = useState(null);
  const [selectedUserKey, setSelectedUserKey] = useState('yukith');
  const [username, setUsername] = useState('yukith');
  const [password, setPassword] = useState('YukithSecure2026!');
  const [showPassword, setShowPassword] = useState(false);
  const [selectedLocation, setSelectedLocation] = useState('new_york');
  const [selectedDevice, setSelectedDevice] = useState('corporate_laptop');

  const [loading, setLoading] = useState(false);
  const [lastResult, setLastResult] = useState(null);
  const [recentAttempts, setRecentAttempts] = useState([]);
  const [error, setError] = useState(null);
  const [pendingAttempt, setPendingAttempt] = useState(null);

  // Load portal configuration & demo users
  useEffect(() => {
    fetchPortalConfig()
      .then(data => {
        setConfig(data);
      })
      .catch(err => console.error('[ALIAS Portal] Config load failed:', err));
  }, []);

  // Handle user preset click
  const handleSelectUser = (userKey) => {
    setSelectedUserKey(userKey);
    const user = config?.users.find(u => u.key === userKey);
    if (user) {
      setUsername(user.user_id);
      setPassword(user.demo_password);
    }
  };

  // Submit login with custom password override
  const handleAttempt = async (passwordToSubmit, attemptLabel) => {
    setLoading(true);
    setError(null);
    try {
      const res = await submitPortalLogin({
        username,
        password: passwordToSubmit,
        location_preset: selectedLocation,
        device_preset: selectedDevice,
      });

      setLastResult(res);
      setPendingAttempt(null);
      setRecentAttempts(prev => [
        {
          id: res.event_id || Date.now(),
          timestamp: new Date().toLocaleTimeString(),
          user: res.user_id,
          status: res.auth_status,
          failedCount: res.failed_attempts,
          location: res.location,
          ip: res.ip_address,
          label: attemptLabel,
        },
        ...prev.slice(0, 9)
      ]);
    } catch (err) {
      console.error('[ALIAS Portal] Submission failed:', err);
      setError('Unable to reach ALIAS telemetry pipeline. The portal is still usable, but this attempt was not recorded.');
      setPendingAttempt({ passwordToSubmit, attemptLabel });
    } finally {
      setLoading(false);
    }
  };

  const handleRetry = () => {
    if (pendingAttempt) {
      handleAttempt(pendingAttempt.passwordToSubmit, pendingAttempt.attemptLabel);
    }
  };

  const handleResetCounters = async () => {
    if (!window.confirm('Reset all demo counters and clear the activity ledger? This cannot be undone.')) {
      return;
    }
    setError(null);
    try {
      await resetPortalCounters();
      setLastResult(null);
      setRecentAttempts([]);
    } catch (err) {
      console.error('[ALIAS Portal] Reset failed:', err);
      setError('Unable to reset demo state — the backend did not respond.');
    }
  };

  const selectedLocData = config?.locations?.find(l => l.key === selectedLocation);
  const selectedDevData = config?.devices?.find(d => d.key === selectedDevice);

  return (
    <div className="max-w-6xl mx-auto pb-12 flex flex-col gap-6 font-sans">
      {/* Editorial Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-border pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-3xs font-mono uppercase tracking-widest text-brand-ember font-bold bg-brand-soft px-2 py-0.5 rounded border border-brand-ember/30">
              Protected Application
            </span>
            <span className="text-text-muted text-xs">/</span>
            <span className="text-xs font-mono text-text-muted">yukith-hub.vercel.app simulation</span>
          </div>
          <h1 className="text-lg font-bold tracking-tight text-text-primary mt-1 font-heading">
            Yukith Hub · Single Sign-On Portal
          </h1>
          <p className="text-xs text-text-secondary mt-0.5">
            Real enterprise login surface monitored continuously by ALIAS Security Pipeline
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handleResetCounters}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-sm text-xs font-medium text-text-secondary bg-surface border border-border hover:bg-surface-elevated transition-colors outline-none focus-visible:ring-2 focus-visible:ring-focus"
          >
            <RotateCcw className="w-3.5 h-3.5 text-text-muted" aria-hidden="true" />
            <span>Reset Demo State</span>
          </button>
        </div>
      </div>

      {/* Main Grid: Login Card & Telemetry Controls */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">

        {/* Left Column (7 cols): The Protected Application Login Form */}
        <div className="lg:col-span-7 flex flex-col gap-5">

          {/* Quick Preset Selector for Judges */}
          <div className="bg-surface border border-border rounded p-4 shadow-xs">
            <div className="flex items-center justify-between mb-3">
              <span className="text-3xs font-mono uppercase tracking-wider text-text-muted font-bold flex items-center gap-1.5">
                <User className="w-3.5 h-3.5 text-brand-ember" />
Choose Identity Preset
              </span>
              <span className="text-3xs text-text-muted font-mono">1-click credentials</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
              {config?.users?.map(u => {
                const isSelected = selectedUserKey === u.key;
                return (
                  <button
                    key={u.key}
                    type="button"
                    onClick={() => handleSelectUser(u.key)}
                    className={cn(
                      "p-3 rounded-sm border text-left flex flex-col gap-1 transition-all outline-none",
                      "focus-visible:ring-2 focus-visible:ring-focus",
                      isSelected
                        ? "border-brand-ember bg-brand-soft/30 ring-1 ring-brand-ember shadow-xs"
                        : "border-border bg-surface hover:bg-surface-soft hover:border-border-strong"
                    )}
                  >
                    <span className="text-xs font-bold text-text-primary truncate">{u.name}</span>
                    <span className="text-2xs font-mono text-text-secondary truncate">{u.email}</span>
                    <span className="text-3xs text-brand-ember font-medium mt-1">{u.role}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Login Interface Form */}
          <div className="bg-surface border border-border rounded p-6 shadow-xs flex flex-col gap-5">
            <div className="flex items-center justify-between border-b border-border/70 pb-3">
              <div className="flex items-center gap-2">
                <Lock className="w-4 h-4 text-brand-ember" />
                <h2 className="text-xs font-bold uppercase tracking-wider text-text-primary">
                  Authentication Interface
                </h2>
              </div>
              <span className="text-3xs font-mono text-text-muted bg-surface-soft px-2 py-0.5 rounded border border-border">
                TLS Encrypted
              </span>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-text-secondary mb-1.5">
                  Account Identifier / Username
                </label>
                <div className="relative">
                  <User className="w-4 h-4 absolute left-3 top-2.5 text-text-muted" />
                  <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="w-full pl-9 pr-3 py-2 bg-surface border border-border rounded-sm text-xs text-text-primary font-mono outline-none focus:border-brand-ember focus:ring-1 focus:ring-brand-ember"
                    placeholder="e.g. yukith or sarah"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-text-secondary mb-1.5">
                  Password Credential
                </label>
                <div className="relative">
                  <KeyRound className="w-4 h-4 absolute left-3 top-2.5 text-text-muted" />
                  <input
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full pl-9 pr-10 py-2 bg-surface border border-border rounded-sm text-xs text-text-primary font-mono outline-none focus:border-brand-ember focus:ring-1 focus:ring-brand-ember"
                    placeholder="Enter password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                    className="absolute right-3 top-2.5 text-text-muted hover:text-text-primary"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>
            </div>

            {/* Quick Demo Action Buttons for Judges */}
            <div className="pt-2 flex flex-col sm:flex-row gap-3">
              {/* Wrong Password Button (Brute Force Demonstration) */}
              <button
                type="button"
                disabled={loading}
                onClick={() => handleAttempt("WRONG_PASSWORD_" + Math.floor(Math.random() * 999), "Wrong Password")}
                className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-sm text-xs font-semibold bg-sev-critical-bg text-sev-critical-text border border-sev-critical-indicator/40 hover:bg-sev-critical-bg/80 hover:border-sev-critical-indicator transition-all outline-none focus-visible:ring-2 focus-visible:ring-focus shadow-xs"
              >
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <XCircle className="w-4 h-4 text-sev-critical-indicator" />}
                <span>Submit (Wrong Password)</span>
              </button>

              {/* Correct Password Button (Legitimate Login / Compromise Success) */}
              <button
                type="button"
                disabled={loading}
                onClick={() => handleAttempt(password, "Correct Password")}
                className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-sm text-xs font-semibold bg-brand-ember text-white hover:bg-brand-deep transition-all outline-none focus-visible:ring-2 focus-visible:ring-focus shadow-xs"
              >
                {loading ? <Loader2 className="w-4 h-4 animate-spin text-white" /> : <CheckCircle2 className="w-4 h-4 text-white" />}
                <span>Submit (Correct Password)</span>
              </button>
            </div>

            {error && (
              <div className="flex items-start gap-2 text-xs text-sev-critical-text bg-sev-critical-bg border border-sev-critical-indicator/40 rounded-sm p-3">
                <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5 text-sev-critical-indicator" />
                <div className="flex-1">
                  <p>{error}</p>
                  {pendingAttempt && (
                    <button
                      type="button"
                      onClick={handleRetry}
                      disabled={loading}
                      className="mt-2 inline-flex items-center gap-1 text-2xs font-semibold underline hover:no-underline"
                    >
                      Retry
                    </button>
                  )}
                </div>
              </div>
            )}

            <div className="text-2xs text-text-muted font-mono leading-relaxed bg-surface-soft p-3 rounded-sm border border-border">
              <strong>Judge Demo Guide:</strong> Click <em>"Submit (Wrong Password)"</em> 3-4 times to simulate a brute-force credential stuffing burst. Then click <em>"Submit (Correct Password)"</em> to simulate a successful compromise, and observe the ALIAS behavioral pipeline synthesize the full incident.
            </div>
          </div>
        </div>

        {/* Right Column (5 cols): Location Changer & Device Simulation Controls */}
        <div className="lg:col-span-5 flex flex-col gap-5">

          {/* Location Changer Card */}
          <div className="bg-surface border border-border rounded p-5 shadow-xs flex flex-col gap-3">
            <div className="flex items-center justify-between border-b border-border/70 pb-2.5">
              <div className="flex items-center gap-2">
                <Globe2 className="w-4 h-4 text-brand-ember" />
                <h3 className="text-xs font-bold uppercase tracking-wider text-text-primary">
                  Location Changer
                </h3>
              </div>
              <span className="text-3xs text-text-muted font-mono">Geo Simulation</span>
            </div>

            <p className="text-2xs text-text-secondary leading-snug">
              Select origin to test location anomalies and <strong>Impossible Travel</strong> velocity:
            </p>

            <div className="space-y-2">
              {config?.locations?.map(loc => {
                const isSelected = selectedLocation === loc.key;
                return (
                  <button
                    key={loc.key}
                    type="button"
                    onClick={() => setSelectedLocation(loc.key)}
                    className={cn(
                      "w-full p-2.5 rounded-sm border text-left flex items-center justify-between gap-3 transition-all outline-none text-xs",
                      "focus-visible:ring-2 focus-visible:ring-focus",
                      isSelected
                        ? "border-brand-ember bg-brand-soft/25 ring-1 ring-brand-ember shadow-2xs font-semibold"
                        : "border-border bg-surface hover:bg-surface-soft"
                    )}
                  >
                    <div className="flex items-center gap-2.5 min-w-0">
                      <span className="text-base shrink-0">{loc.flag}</span>
                      <div className="flex flex-col min-w-0">
                        <span className="text-text-primary truncate">{loc.name}</span>
                        <span className="text-3xs text-text-muted font-mono truncate">{loc.ip_address}</span>
                      </div>
                    </div>

                    <span className="text-3xs font-mono text-text-muted shrink-0">
                      {loc.latitude.toFixed(1)}, {loc.longitude.toFixed(1)}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Device Profile Selector */}
          <div className="bg-surface border border-border rounded p-5 shadow-xs flex flex-col gap-3">
            <div className="flex items-center justify-between border-b border-border/70 pb-2.5">
              <div className="flex items-center gap-2">
                <Laptop className="w-4 h-4 text-brand-ember" />
                <h3 className="text-xs font-bold uppercase tracking-wider text-text-primary">
                  Device Profile
                </h3>
              </div>
              <span className="text-3xs text-text-muted font-mono">Hardware Telemetry</span>
            </div>

            <div className="space-y-2">
              {config?.devices?.map(dev => {
                const isSelected = selectedDevice === dev.key;
                return (
                  <button
                    key={dev.key}
                    type="button"
                    onClick={() => setSelectedDevice(dev.key)}
                    className={cn(
                      "w-full p-2.5 rounded-sm border text-left flex items-center gap-3 transition-all outline-none text-xs",
                      "focus-visible:ring-2 focus-visible:ring-focus",
                      isSelected
                        ? "border-brand-ember bg-brand-soft/25 ring-1 ring-brand-ember font-semibold"
                        : "border-border bg-surface hover:bg-surface-soft"
                    )}
                  >
                    {dev.key.includes('laptop') ? <Laptop className="w-4 h-4 text-text-muted" /> : <Smartphone className="w-4 h-4 text-text-muted" />}
                    <div className="flex flex-col min-w-0">
                      <span className="text-text-primary truncate">{dev.name}</span>
                      <span className="text-3xs text-text-muted font-mono truncate">{dev.fingerprint}</span>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

        </div>
      </div>

      {/* Live Ingestion Telemetry Acknowledgment (Shows what ALIAS received) */}
      {lastResult && (
        <div className="bg-surface border border-border rounded p-5 shadow-xs flex flex-col gap-3">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-border/70 pb-3">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-brand-ember" />
              <h3 className="text-xs font-bold uppercase tracking-wider text-text-primary">
                Live Ingestion Telemetry Acknowledgment
              </h3>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-2xs font-mono text-text-muted">Event ID:</span>
              <span className="text-xs font-mono font-bold text-text-primary bg-surface-soft px-2 py-0.5 rounded border border-border">
                EVT-{lastResult.event_id}
              </span>
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs font-mono">
            <div className="p-3 rounded bg-surface-soft border border-border flex flex-col gap-1">
              <span className="text-3xs text-text-muted uppercase">Auth Result</span>
              <span className={cn(
                "font-bold text-sm",
                lastResult.auth_status === 'SUCCESS' ? "text-sev-low-text" : "text-sev-critical-text"
              )}>
                {lastResult.auth_status}
              </span>
            </div>

            <div className="p-3 rounded bg-surface-soft border border-border flex flex-col gap-1">
              <span className="text-3xs text-text-muted uppercase">Consecutive Failures</span>
              <span className="font-bold text-sm text-text-primary">
                {lastResult.failed_attempts} attempt{lastResult.failed_attempts === 1 ? '' : 's'}
              </span>
            </div>

            <div className="p-3 rounded bg-surface-soft border border-border flex flex-col gap-1">
              <span className="text-3xs text-text-muted uppercase">Location Telemetry</span>
              <span className="font-bold text-sm text-text-primary truncate">
                {lastResult.location}
              </span>
            </div>

            <div className="p-3 rounded bg-surface-soft border border-border flex flex-col gap-1">
              <span className="text-3xs text-text-muted uppercase">IP Address</span>
              <span className="font-bold text-sm text-text-primary truncate">
                {lastResult.ip_address}
              </span>
            </div>
          </div>

          <div className="flex items-center justify-between pt-2 flex-wrap gap-3">
            <span className="text-3xs font-mono text-text-muted">
              Telemetry successfully delivered to ALIAS via POST /api/events/login (Zero credential leakage).
            </span>

            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={onGoOverview}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-sm text-xs font-medium text-text-secondary bg-surface border border-border hover:bg-surface-elevated transition-colors"
              >
                <span>View in Overview</span>
                <ArrowRight className="w-3 h-3" />
              </button>

              {lastResult.event_id && (
                <button
                  type="button"
                  onClick={() => onOpenInvestigation(lastResult.event_id)}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-sm text-xs font-semibold text-white bg-brand-ember hover:bg-brand-deep transition-colors shadow-xs"
                >
                  <span>Inspect Forensic Dossier</span>
                  <ArrowRight className="w-3 h-3" />
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Historical Attempts Ledger */}
      {recentAttempts.length > 0 && (
        <div className="bg-surface border border-border rounded p-5 shadow-xs flex flex-col gap-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-text-primary">
            Portal Authentication Activity Stream
          </h3>

          <div className="divide-y divide-border border border-border rounded-sm overflow-hidden bg-surface">
            {recentAttempts.map((att, idx) => (
              <div key={idx} className="p-3 flex items-center justify-between text-xs font-mono gap-3 hover:bg-surface-soft/60 transition-colors">
                <div className="flex items-center gap-3">
                  {att.status === 'SUCCESS' ? (
                    <CheckCircle2 className="w-4 h-4 text-sev-low-indicator shrink-0" />
                  ) : (
                    <XCircle className="w-4 h-4 text-sev-critical-indicator shrink-0" />
                  )}
                  <span className="font-bold text-text-primary">{att.user}</span>
                  <span className="text-text-muted">{att.timestamp}</span>
                  <span className="text-text-secondary">[{att.label}]</span>
                </div>

                <div className="flex items-center gap-4">
                  <span className="text-text-muted font-sans text-2xs">{att.location}</span>
                  <span className="text-3xs text-text-muted bg-surface-soft px-1.5 py-0.5 rounded border border-border">
                    Failures: {att.failedCount}
                  </span>
                  <span className={cn(
                    "text-3xs font-bold px-2 py-0.5 rounded uppercase",
                    att.status === 'SUCCESS' ? "bg-sev-low-bg text-sev-low-text" : "bg-sev-critical-bg text-sev-critical-text"
                  )}>
                    {att.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
