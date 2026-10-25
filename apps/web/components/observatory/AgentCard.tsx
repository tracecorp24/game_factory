'use client';

import React from 'react';
import {
  Sparkles,
  Cpu,
  Clock,
  RotateCcw,
  CheckCircle2,
  AlertTriangle,
  Play,
  Pause,
  ExternalLink,
  Zap,
} from 'lucide-react';
import { cn, formatCurrency, formatTokens } from '@/lib/utils';
import { AgentInfo } from '@/lib/types';
import { useAppStore } from '@/lib/store';

interface AgentCardProps {
  agent: AgentInfo;
  isSelected: boolean;
  onSelect: () => void;
  x: number;
  y: number;
}

const CLUSTER_COLORS: Record<string, { ring: string; badge: string; text: string }> = {
  insight: { ring: 'border-cyan-500/50', badge: 'bg-cyan-950/80 text-cyan-300 border-cyan-800/60', text: 'text-cyan-400' },
  strategy: { ring: 'border-blue-500/50', badge: 'bg-blue-950/80 text-blue-300 border-blue-800/60', text: 'text-blue-400' },
  production: { ring: 'border-purple-500/50', badge: 'bg-purple-950/80 text-purple-300 border-purple-800/60', text: 'text-purple-400' },
  qa: { ring: 'border-rose-500/50', badge: 'bg-rose-950/80 text-rose-300 border-rose-800/60', text: 'text-rose-400' },
  governance: { ring: 'border-amber-500/50', badge: 'bg-amber-950/80 text-amber-300 border-amber-800/60', text: 'text-amber-400' },
};

export function AgentCard({ agent, isSelected, onSelect, x, y }: AgentCardProps) {
  const { observatoryTheme, reducedMotion } = useAppStore();
  const clusterStyle = CLUSTER_COLORS[agent.cluster] || CLUSTER_COLORS.insight;
  const isNeon = observatoryTheme === 'neon';

  return (
    <div
      onClick={onSelect}
      style={{
        position: 'absolute',
        left: `${x}px`,
        top: `${y}px`,
        transform: 'translate(-50%, -50%)',
      }}
      className={cn(
        'w-64 rounded-xl cursor-pointer transition-all duration-300 select-none overflow-hidden z-10',
        isNeon ? 'bg-slate-900/90 backdrop-blur-xl border' : 'bg-slate-900 border border-slate-800',
        isSelected
          ? 'border-cyan-400 ring-2 ring-cyan-400/40 shadow-2xl shadow-cyan-500/30 scale-105'
          : `${clusterStyle.ring} hover:scale-102 hover:border-slate-400`,
        agent.state === 'running' && !reducedMotion && 'animate-pulse-glow border-cyan-400',
        agent.state === 'failed' && 'border-rose-500 shadow-rose-500/30'
      )}
    >
      {/* Top Banner with Cluster and Status */}
      <div className="px-3 py-2 bg-slate-950/80 border-b border-slate-800/80 flex items-center justify-between">
        <span className={cn('text-[10px] font-mono px-1.5 py-0.5 rounded border', clusterStyle.badge)}>
          {agent.cluster.toUpperCase()}
        </span>

        {/* State Pill */}
        <div className="flex items-center gap-1 text-[10px] font-mono">
          {agent.state === 'completed' && (
            <span className="flex items-center gap-1 text-emerald-400">
              <CheckCircle2 className="w-3 h-3" /> idle/done
            </span>
          )}
          {agent.state === 'running' && (
            <span className="flex items-center gap-1 text-cyan-300 animate-pulse font-semibold">
              <span className="w-2 h-2 rounded-full bg-cyan-400" /> running
            </span>
          )}
          {agent.state === 'failed' && (
            <span className="flex items-center gap-1 text-rose-400 font-semibold">
              <AlertTriangle className="w-3 h-3" /> failed
            </span>
          )}
          {agent.state === 'queued' && (
            <span className="flex items-center gap-1 text-amber-400">
              <Clock className="w-3 h-3" /> queued
            </span>
          )}
        </div>
      </div>

      {/* Main Body */}
      <div className="p-3 space-y-2">
        <div className="flex items-center justify-between">
          <div className="font-semibold text-xs text-slate-100 truncate pr-2">{agent.name}</div>
          {agent.attempts > 1 && (
            <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-rose-950 text-rose-300 border border-rose-800/60 flex items-center gap-1">
              <RotateCcw className="w-2.5 h-2.5" /> #{agent.attempts}
            </span>
          )}
        </div>

        <div className="text-[11px] text-slate-400 line-clamp-1">{agent.role}</div>

        <div className="p-2 rounded bg-slate-950/60 border border-slate-800/60 text-[10px] text-slate-300 font-mono line-clamp-2">
          {agent.currentTask}
        </div>

        {/* Telemetry Metrics */}
        <div className="grid grid-cols-2 gap-2 pt-1 border-t border-slate-800/60 text-[10px] font-mono text-slate-400">
          <div>
            <span>Model: </span>
            <span className="text-slate-200">{agent.activeModel ? agent.activeModel.split('/')[0] : 'n/a'}</span>
          </div>
          <div className="text-right">
            <span>Cost: </span>
            <span className="text-cyan-300 font-semibold">
              {formatCurrency(agent.costUsd)}
            </span>
          </div>
          <div>
            <span>Tokens: </span>
            <span className="text-slate-200">{formatTokens(agent.tokensBilled)}</span>
          </div>
          <div className="text-right">
            <span>Latency: </span>
            <span className="text-slate-200">{(agent.latencyMs / 1000).toFixed(1)}s</span>
          </div>
        </div>
      </div>
    </div>
  );
}
