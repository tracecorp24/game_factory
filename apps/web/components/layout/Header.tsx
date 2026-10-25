'use client';

import React, { useState } from 'react';
import {
  Activity,
  Layers,
  Sparkles,
  Zap,
  Gauge,
  Sliders,
  DollarSign,
  Info,
  CheckCircle2,
  Power,
} from 'lucide-react';
import { useAppStore } from '@/lib/store';
import { cn } from '@/lib/utils';
import { toast } from '@/lib/toast';

export function Header() {
  const [isShuttingDown, setIsShuttingDown] = useState(false);
  const {
    projectId,
    campaignId,
    budgetApproved,
    budgetSpent,
    isDemoSimulation,
    isLiveConnected,
    observatoryTheme,
    reducedMotion,
    setObservatoryTheme,
    setReducedMotion,
  } = useAppStore();

  const handleShutdownServer = async () => {
    if (confirm('Geliştirme sunucusunu ve tüm arka plan süreçlerini kapatmak istiyor musunuz?')) {
      setIsShuttingDown(true);
      toast.warning('Sunucu Kapatılıyor', 'CreativeForge sunucusu ve CMD süreçleri sonlandırılıyor...', 8000);
      try {
        await fetch('/api/shutdown', { method: 'POST' });
      } catch {}
    }
  };

  const spentPercent = Math.min(100, Math.round((budgetSpent / budgetApproved) * 100));

  return (
    <header className="h-16 border-b border-slate-800 bg-[#070b14]/90 backdrop-blur-md px-6 flex items-center justify-between z-20">
      {/* Left: Context Breadcrumb */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 text-xs font-mono">
          <span className="text-slate-400">org_creativeforge</span>
          <span className="text-slate-600">/</span>
          <span className="text-slate-300 font-semibold">{projectId}</span>
          <span className="text-slate-600">/</span>
          <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 text-[11px] border border-slate-700">
            {campaignId}
          </span>
        </div>

        {/* Simulation Demo Banner */}
        {isDemoSimulation && (
          <div className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-cyan-950/60 border border-cyan-500/40 text-[11px] font-mono text-cyan-300 shadow-sm shadow-cyan-500/20">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
            <span className="font-semibold tracking-wider">SIMULATION DEMO STREAM</span>
            <span className="text-cyan-500 font-light">| run_88</span>
          </div>
        )}
      </div>

      {/* Right: Telemetry, Budget, Theme, Motion */}
      <div className="flex items-center gap-4">
        {/* Budget Guard Meter */}
        <div className="hidden md:flex items-center gap-3 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800">
          <div className="flex items-center gap-1.5 text-xs">
            <DollarSign className="w-3.5 h-3.5 text-amber-400" />
            <span className="text-slate-400 font-mono text-[11px]">Budget:</span>
            <span className="font-mono font-semibold text-slate-200">
              ${budgetSpent.toFixed(2)}
            </span>
            <span className="text-slate-500 text-[11px]">/ ${budgetApproved.toFixed(0)}</span>
          </div>
          <div className="w-16 h-1.5 rounded-full bg-slate-800 overflow-hidden">
            <div
              className={cn(
                'h-full rounded-full transition-all',
                spentPercent > 80 ? 'bg-rose-500' : 'bg-cyan-400'
              )}
              style={{ width: `${spentPercent}%` }}
            />
          </div>
        </div>

        {/* SSE Connection Health */}
        <div className="flex items-center gap-1.5 text-xs font-mono px-2.5 py-1 rounded bg-slate-900 border border-slate-800">
          <span
            className={cn(
              'w-2 h-2 rounded-full',
              isLiveConnected ? 'bg-emerald-400 shadow-sm shadow-emerald-400 animate-pulse' : 'bg-rose-400'
            )}
          />
          <span className="text-slate-400 text-[11px]">
            {isLiveConnected ? 'SSE Live' : 'Disconnected'}
          </span>
        </div>

        {/* Theme Switcher: Operations vs Neon */}
        <div className="flex items-center rounded-lg bg-slate-900 p-0.5 border border-slate-800">
          <button
            onClick={() => setObservatoryTheme('neon')}
            className={cn(
              'px-2.5 py-1 text-xs rounded-md font-medium transition-all flex items-center gap-1.5',
              observatoryTheme === 'neon'
                ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-sm shadow-cyan-500/30'
                : 'text-slate-400 hover:text-slate-200'
            )}
            title="Cyber Neon Mode (Visual & Presentation)"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span className="text-[11px]">Neon</span>
          </button>
          <button
            onClick={() => setObservatoryTheme('operations')}
            className={cn(
              'px-2.5 py-1 text-xs rounded-md font-medium transition-all flex items-center gap-1.5',
              observatoryTheme === 'operations'
                ? 'bg-slate-800 text-slate-100 shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            )}
            title="Clean Operations Mode"
          >
            <Gauge className="w-3.5 h-3.5" />
            <span className="text-[11px]">Operations</span>
          </button>
        </div>

        {/* Reduced Motion Toggle */}
        <button
          onClick={() => setReducedMotion(!reducedMotion)}
          className={cn(
            'p-1.5 rounded-lg border text-xs transition-all flex items-center gap-1',
            reducedMotion
              ? 'bg-purple-950/80 border-purple-500/60 text-purple-300'
              : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200'
          )}
          title={reducedMotion ? 'Reduced Motion: ON' : 'Reduced Motion: OFF'}
        >
          <Activity className="w-4 h-4" />
          <span className="text-[10px] font-mono hidden sm:inline">
            {reducedMotion ? 'Static' : 'Motion'}
          </span>
        </button>

        {/* Shutdown Server & Close CLI */}
        <button
          onClick={handleShutdownServer}
          disabled={isShuttingDown}
          className={cn(
            'p-1.5 rounded-lg border text-xs transition-all flex items-center gap-1',
            isShuttingDown
              ? 'bg-rose-950 text-rose-400 border-rose-800 opacity-60'
              : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-rose-400 hover:border-rose-900/80'
          )}
          title="Sunucuyu ve CMD Sürecini Kapat (Clean Shutdown)"
        >
          <Power className="w-4 h-4 text-rose-500" />
          <span className="text-[10px] font-mono hidden lg:inline text-rose-400">
            {isShuttingDown ? 'Kapanıyor...' : 'Kapat'}
          </span>
        </button>
      </div>
    </header>
  );
}
