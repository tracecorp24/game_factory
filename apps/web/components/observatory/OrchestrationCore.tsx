'use client';

import React from 'react';
import { Radio, Flame, Cpu, ShieldCheck } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useAppStore } from '@/lib/store';

export function OrchestrationCore({ x, y }: { x: number; y: number }) {
  const { observatoryTheme, reducedMotion, activeRunId, runStatus } = useAppStore();
  const isNeon = observatoryTheme === 'neon';

  return (
    <div
      style={{
        position: 'absolute',
        left: `${x}px`,
        top: `${y}px`,
        transform: 'translate(-50%, -50%)',
      }}
      className="z-10 flex flex-col items-center justify-center select-none"
    >
      {/* Outer Glow Ring */}
      <div className="relative w-44 h-44 rounded-full flex items-center justify-center">
        {/* Animated Pulsing Orbit Border */}
        <div
          className={cn(
            'absolute inset-0 rounded-full border border-dashed border-cyan-500/40',
            !reducedMotion && 'animate-orbit-spin'
          )}
        />
        <div
          className={cn(
            'absolute inset-2 rounded-full border border-purple-500/30',
            !reducedMotion && 'animate-pulse'
          )}
        />

        {/* Center Reactor Core */}
        <div
          className={cn(
            'w-32 h-32 rounded-full flex flex-col items-center justify-center p-3 text-center shadow-2xl transition-all',
            isNeon
              ? 'bg-gradient-to-tr from-cyan-950 via-slate-900 to-purple-950 border-2 border-cyan-400/80 shadow-cyan-500/40 glow-cyan'
              : 'bg-slate-900 border-2 border-slate-700 shadow-slate-900'
          )}
        >
          <div className="w-8 h-8 rounded-full bg-cyan-500/20 border border-cyan-400 flex items-center justify-center mb-1">
            <Flame className="w-4 h-4 text-cyan-300 animate-pulse" />
          </div>
          <div className="text-[11px] font-bold text-white tracking-wide uppercase font-mono">
            Orchestration Core
          </div>
          <div className="text-[9px] font-mono text-cyan-300 mt-0.5">
            {activeRunId} • {runStatus.toUpperCase()}
          </div>
        </div>
      </div>

      {/* Subtitle Badge */}
      <div className="mt-2 px-2.5 py-0.5 rounded-full bg-slate-950/80 border border-slate-800 text-[10px] font-mono text-slate-400 flex items-center gap-1.5 shadow-sm">
        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
        <span>Append-Only Ledger Active</span>
      </div>
    </div>
  );
}
