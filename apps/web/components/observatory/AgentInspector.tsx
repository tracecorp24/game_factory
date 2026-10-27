'use client';

import React from 'react';
import Link from 'next/link';
import {
  X,
  Cpu,
  RotateCcw,
  DollarSign,
  ShieldAlert,
  FileCode,
  ExternalLink,
  Layers,
  Terminal,
  Activity,
  CheckCircle2,
  AlertTriangle,
  Clock,
} from 'lucide-react';
import { cn, formatCurrency, formatTokens } from '@/lib/utils';
import { useAppStore } from '@/lib/store';

export function AgentInspector() {
  const { selectedAgentId, setSelectedAgentId, agents, projectId } = useAppStore();

  if (!selectedAgentId || !agents[selectedAgentId]) {
    return null;
  }

  const agent = agents[selectedAgentId];

  return (
    <div className="w-84 md:w-96 border-l border-white/[0.06] bg-[#0c101a]/85 backdrop-blur-3xl flex flex-col flex-shrink-0 select-none overflow-hidden h-full z-20 shadow-2xl">
      {/* Header */}
      <div className="p-3.5 border-b border-white/[0.06] flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-apple-teal" />
          <span className="text-xs font-semibold tracking-tight text-neutral-200">
            Agent Telemetry
          </span>
        </div>
        <button
          onClick={() => setSelectedAgentId(null)}
          className="p-1 rounded-md text-neutral-400 hover:text-white hover:bg-white/[0.08] transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 text-xs">
        {/* Agent Profile Summary */}
        <div className="p-4 rounded-2xl bg-white/[0.03] border border-white/[0.06] space-y-2">
          <div className="flex items-center justify-between">
            <span className="font-semibold text-sm text-neutral-100">{agent.name}</span>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-apple-blue/15 text-apple-teal border border-apple-blue/25">
              {agent.cluster.toUpperCase()}
            </span>
          </div>
          <div className="text-neutral-400 text-xs">{agent.role}</div>
          <div className="text-[11px] font-mono text-neutral-300 p-2.5 rounded-xl bg-black/25 border border-white/[0.04]">
            {agent.currentTask}
          </div>
        </div>

        {/* Status & Attempts */}
        <div className="grid grid-cols-2 gap-3">
          <div className="p-3 rounded-2xl bg-white/[0.03] border border-white/[0.06]">
            <div className="text-neutral-500 text-[10px] uppercase font-mono">State</div>
            <div className="font-mono font-semibold text-neutral-200 flex items-center gap-1.5 mt-1">
              <span className="w-1.5 h-1.5 rounded-full bg-apple-emerald" />
              {agent.state.toUpperCase()}
            </div>
          </div>
          <div className="p-3 rounded-2xl bg-white/[0.03] border border-white/[0.06]">
            <div className="text-neutral-500 text-[10px] uppercase font-mono">Attempts</div>
            <div className="font-mono font-semibold text-neutral-200 flex items-center gap-1.5 mt-1">
              <RotateCcw className="w-3.5 h-3.5 text-apple-teal" />
              {agent.attempts} {agent.attempts > 1 ? '(Fallback)' : '(Clean)'}
            </div>
          </div>
        </div>

        {/* Model & Token Accounting */}
        <div className="p-4 rounded-2xl bg-white/[0.03] border border-white/[0.06] space-y-2.5">
          <div className="flex items-center justify-between text-xs font-semibold text-neutral-300">
            <span className="flex items-center gap-1.5">
              <Cpu className="w-3.5 h-3.5 text-apple-teal" />
              Model & Cost Audit
            </span>
            <span className="font-mono text-apple-emerald">{formatCurrency(agent.costUsd)}</span>
          </div>

          <div className="space-y-1.5 font-mono text-[11px]">
            <div className="flex items-center justify-between text-neutral-400">
              <span>Active Model:</span>
              <span className="text-neutral-200">{agent.activeModel || 'Deterministic'}</span>
            </div>
            <div className="flex items-center justify-between text-neutral-400">
              <span>Billed Tokens:</span>
              <span className="text-neutral-200">{formatTokens(agent.tokensBilled)}</span>
            </div>
            <div className="flex items-center justify-between text-neutral-400">
              <span>Cached Tokens:</span>
              <span className="text-apple-teal">{formatTokens(agent.tokensCached)}</span>
            </div>
            <div className="flex items-center justify-between text-neutral-400">
              <span>End-to-End Latency:</span>
              <span className="text-neutral-200">{agent.latencyMs}ms</span>
            </div>
          </div>
        </div>

        {/* Link to Artifacts / Ledger */}
        <div className="pt-2">
          <Link
            href={`/projects/${projectId}/ledger`}
            className="apple-btn-secondary w-full flex items-center justify-center gap-1.5 py-2 text-center"
          >
            <Terminal className="w-3.5 h-3.5" />
            <span>View Events in Ledger</span>
          </Link>
        </div>
      </div>
    </div>
  );
}
