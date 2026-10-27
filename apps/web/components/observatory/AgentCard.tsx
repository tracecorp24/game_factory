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

const CLUSTER_COLORS: Record<string, { border: string; badge: string; text: string }> = {
  insight: { border: 'border-apple-teal/30', badge: 'bg-apple-teal/15 text-apple-teal border-apple-teal/25', text: 'text-apple-teal' },
  strategy: { border: 'border-apple-blue/30', badge: 'bg-apple-blue/15 text-apple-blue border-apple-blue/25', text: 'text-apple-blue' },
  production: { border: 'border-apple-purple/30', badge: 'bg-apple-purple/15 text-apple-purple border-apple-purple/25', text: 'text-apple-purple' },
  qa: { border: 'border-apple-red/30', badge: 'bg-apple-red/15 text-apple-red border-apple-red/25', text: 'text-apple-red' },
  governance: { border: 'border-apple-amber/30', badge: 'bg-apple-amber/15 text-apple-amber border-apple-amber/25', text: 'text-apple-amber' },
};

export function AgentCard({ agent, isSelected, onSelect, x, y }: AgentCardProps) {
  const { observatoryTheme, reducedMotion } = useAppStore();
  const clusterStyle = CLUSTER_COLORS[agent.cluster] || CLUSTER_COLORS.insight;

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
        'w-64 rounded-2xl cursor-pointer transition-all duration-200 select-none overflow-hidden z-10 bg-[#121724]/90 backdrop-blur-2xl border shadow-apple-md',
        isSelected
          ? 'border-apple-blue ring-2 ring-apple-blue/40 shadow-apple-glow scale-105'
          : `${clusterStyle.border} hover:scale-[1.02] hover:border-white/[0.2]`,
        agent.state === 'running' && !reducedMotion && 'ring-1 ring-apple-teal/50 border-apple-teal',
        agent.state === 'failed' && 'border-apple-red shadow-apple-red/30'
      )}
    >
      {/* Top Banner with Cluster and Status */}
      <div className="px-3 py-2 bg-black/30 border-b border-white/[0.06] flex items-center justify-between">
        <span className={cn('text-[9px] font-mono px-2 py-0.5 rounded-full border', clusterStyle.badge)}>
          {agent.cluster.toUpperCase()}
        </span>

        {/* State Pill */}
        <div className="flex items-center gap-1 text-[10px] font-mono">
          {agent.state === 'completed' && (
            <span className="flex items-center gap-1 text-apple-emerald font-medium">
              <span className="w-1.5 h-1.5 rounded-full bg-apple-emerald" /> idle/done
            </span>
          )}
          {agent.state === 'running' && (
            <span className="flex items-center gap-1 text-apple-teal font-semibold">
              <span className="w-1.5 h-1.5 rounded-full bg-apple-teal animate-pulse" /> running
            </span>
          )}
          {agent.state === 'failed' && (
            <span className="flex items-center gap-1 text-apple-red font-semibold">
              <span className="w-1.5 h-1.5 rounded-full bg-apple-red" /> failed
            </span>
          )}
          {agent.state === 'queued' && (
            <span className="flex items-center gap-1 text-apple-amber">
              <Clock className="w-2.5 h-2.5" /> queued
            </span>
          )}
        </div>
      </div>

      {/* Main Body */}
      <div className="p-3 space-y-2">
        <div className="flex items-center justify-between">
          <div className="font-semibold text-xs text-neutral-100 truncate pr-2">{agent.name}</div>
          {agent.attempts > 1 && (
            <span className="text-[10px] font-mono px-1.5 py-0.2 rounded-full bg-apple-red/15 text-apple-red border border-apple-red/25 flex items-center gap-1">
              <RotateCcw className="w-2.5 h-2.5" /> #{agent.attempts}
            </span>
          )}
        </div>

        <div className="text-[11px] text-neutral-400 font-sans line-clamp-2 leading-relaxed">
          {agent.currentTask}
        </div>

        {/* Telemetry Stats Bar */}
        <div className="pt-2 border-t border-white/[0.05] grid grid-cols-2 gap-2 text-[10px] font-mono text-neutral-400">
          <div>
            <span className="text-neutral-500">Model: </span>
            <span className="text-neutral-200 truncate">{agent.activeModel ? agent.activeModel.split('-').slice(0, 2).join('-') : 'Deterministic'}</span>
          </div>
          <div className="text-right">
            <span className="text-neutral-500">Tokens: </span>
            <span className="text-neutral-200">{formatTokens(agent.tokensBilled || 0)}</span>
          </div>
          <div>
            <span className="text-neutral-500">Latency: </span>
            <span className="text-neutral-200">{agent.latencyMs}ms</span>
          </div>
          <div className="text-right">
            <span className="text-neutral-500">Cost: </span>
            <span className="text-apple-emerald font-semibold">
              {typeof agent.costUsd === 'number' ? `$${agent.costUsd.toFixed(4)}` : (agent.costUsd || '$0.0000')}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
