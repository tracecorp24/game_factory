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
  ChevronRight,
  Wifi,
  WifiOff,
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
    <header className="h-14 border-b border-white/[0.06] bg-[#0c101a]/80 backdrop-blur-2xl px-5 flex items-center justify-between z-20 select-none">
      {/* Left: Apple Style Path Breadcrumb */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-1.5 text-xs">
          <span className="text-neutral-400 font-medium tracking-tight">CreativeForge</span>
          <ChevronRight className="w-3.5 h-3.5 text-neutral-600" />
          <span className="text-neutral-200 font-semibold tracking-tight">{projectId}</span>
          <ChevronRight className="w-3.5 h-3.5 text-neutral-600" />
          <span className="px-2 py-0.5 rounded-full bg-white/[0.06] text-neutral-300 text-[11px] font-mono border border-white/[0.08]">
            {campaignId}
          </span>
        </div>

        {/* Simulation Demo Indicator */}
        {isDemoSimulation && (
          <div className="hidden lg:flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-apple-blue/10 border border-apple-blue/25 text-[11px] font-medium text-apple-teal">
            <span className="w-1.5 h-1.5 rounded-full bg-apple-teal animate-pulse" />
            <span className="tracking-wide">Simulation Stream</span>
            <span className="text-apple-teal/60 font-mono text-[10px]">run_88</span>
          </div>
        )}
      </div>

      {/* Right: Telemetry, Budget, Theme & Controls */}
      <div className="flex items-center gap-3">
        {/* Budget Meter Pill */}
        <div className="hidden md:flex items-center gap-2.5 px-3 py-1 rounded-full bg-white/[0.04] border border-white/[0.07] text-xs">
          <div className="flex items-center gap-1.5">
            <DollarSign className="w-3.5 h-3.5 text-apple-amber" />
            <span className="text-neutral-400 text-[11px]">Budget:</span>
            <span className="font-mono font-semibold text-neutral-100">
              ${budgetSpent.toFixed(2)}
            </span>
            <span className="text-neutral-500 text-[11px]">/ ${budgetApproved.toFixed(0)}</span>
          </div>
          <div className="w-14 h-1.5 rounded-full bg-neutral-800/80 overflow-hidden">
            <div
              className={cn(
                'h-full rounded-full transition-all duration-500',
                spentPercent > 80 ? 'bg-apple-red' : 'bg-apple-blue'
              )}
              style={{ width: `${spentPercent}%` }}
            />
          </div>
        </div>

        {/* SSE Connection Health Status */}
        <div className="flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full bg-white/[0.04] border border-white/[0.07]">
          {isLiveConnected ? (
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-apple-emerald opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-apple-emerald" />
            </span>
          ) : (
            <span className="inline-flex rounded-full h-2 w-2 bg-apple-red" />
          )}
          <span className="text-neutral-400 text-[11px] font-mono">
            {isLiveConnected ? 'Live Telemetry' : 'Offline'}
          </span>
        </div>

        {/* Apple Segmented Theme Switcher */}
        <div className="apple-segmented">
          <button
            onClick={() => setObservatoryTheme('neon')}
            className={cn(
              'apple-segmented-item flex items-center gap-1.5',
              observatoryTheme === 'neon' && 'apple-segmented-item-active'
            )}
            title="Sleek Dark Theme"
          >
            <Sparkles className="w-3 h-3" />
            <span>Studio</span>
          </button>
          <button
            onClick={() => setObservatoryTheme('operations')}
            className={cn(
              'apple-segmented-item flex items-center gap-1.5',
              observatoryTheme === 'operations' && 'apple-segmented-item-active'
            )}
            title="Clean Operations Mode"
          >
            <Gauge className="w-3 h-3" />
            <span>Operations</span>
          </button>
        </div>

        {/* Reduced Motion Toggle */}
        <button
          onClick={() => setReducedMotion(!reducedMotion)}
          className={cn(
            'px-2.5 py-1 rounded-lg border text-xs transition-all flex items-center gap-1.5',
            reducedMotion
              ? 'bg-apple-purple/15 border-apple-purple/40 text-apple-purple'
              : 'bg-white/[0.04] border-white/[0.07] text-neutral-400 hover:text-neutral-200 hover:bg-white/[0.08]'
          )}
          title={reducedMotion ? 'Reduced Motion: ON' : 'Reduced Motion: OFF'}
        >
          <Activity className="w-3.5 h-3.5" />
          <span className="text-[11px] hidden sm:inline">
            {reducedMotion ? 'Static' : 'Motion'}
          </span>
        </button>

        {/* Shutdown Server & Close CLI */}
        <button
          onClick={handleShutdownServer}
          disabled={isShuttingDown}
          className={cn(
            'p-1.5 rounded-lg border text-xs transition-all flex items-center gap-1.5',
            isShuttingDown
              ? 'bg-apple-red/20 text-apple-red border-apple-red/40 opacity-60'
              : 'bg-white/[0.04] border-white/[0.07] text-neutral-400 hover:text-apple-red hover:bg-apple-red/10 hover:border-apple-red/30'
          )}
          title="Sunucuyu ve CMD Sürecini Kapat (Clean Shutdown)"
        >
          <Power className="w-3.5 h-3.5 text-apple-red" />
          <span className="text-[11px] hidden lg:inline text-neutral-300">
            {isShuttingDown ? 'Kapanıyor...' : 'Kapat'}
          </span>
        </button>
      </div>
    </header>
  );
}
