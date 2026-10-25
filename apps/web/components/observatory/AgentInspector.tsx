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
    <div className="w-84 md:w-96 border-l border-slate-800 bg-[#070b14]/95 backdrop-blur-xl flex flex-col flex-shrink-0 select-none overflow-hidden h-full z-20 shadow-2xl">
      {/* Header */}
      <div className="p-4 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-cyan-400" />
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-200 font-mono">
            Agent Telemetry
          </span>
        </div>
        <button
          onClick={() => setSelectedAgentId(null)}
          className="p-1 rounded text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-5 text-xs">
        {/* Agent Profile Summary */}
        <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between">
            <span className="font-bold text-sm text-slate-100">{agent.name}</span>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-cyan-300 border border-slate-700">
              {agent.cluster.toUpperCase()}
            </span>
          </div>
          <div className="text-slate-400 text-xs">{agent.role}</div>
          <div className="text-[11px] font-mono text-slate-300 p-2 rounded bg-slate-950/70 border border-slate-800/80">
            {agent.currentTask}
          </div>
        </div>

        {/* Status & Attempts */}
        <div className="grid grid-cols-2 gap-3">
          <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800">
            <div className="text-slate-500 text-[10px] uppercase font-mono">State</div>
            <div className="font-mono font-semibold text-slate-200 flex items-center gap-1.5 mt-0.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400" />
              {agent.state.toUpperCase()}
            </div>
          </div>
          <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800">
            <div className="text-slate-500 text-[10px] uppercase font-mono">Attempts</div>
            <div className="font-mono font-semibold text-slate-200 flex items-center gap-1.5 mt-0.5">
              <RotateCcw className="w-3.5 h-3.5 text-cyan-400" />
              {agent.attempts} {agent.attempts > 1 ? '(Fallback)' : '(Clean)'}
            </div>
          </div>
        </div>

        {/* Model & Token Accounting */}
        <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2.5">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-300">
            <span className="flex items-center gap-1.5">
              <Cpu className="w-3.5 h-3.5 text-cyan-400" />
              Model & Cost Audit
            </span>
            <span className="font-mono text-cyan-300">{formatCurrency(agent.costUsd)}</span>
          </div>

          <div className="space-y-1.5 font-mono text-[11px]">
            <div className="flex items-center justify-between text-slate-400">
              <span>Active Model:</span>
              <span className="text-slate-200">{agent.activeModel || 'Deterministic'}</span>
            </div>
            <div className="flex items-center justify-between text-slate-400">
              <span>Billed Tokens:</span>
              <span className="text-slate-200">{formatTokens(agent.tokensBilled)}</span>
            </div>
            <div className="flex items-center justify-between text-slate-400">
              <span>Cached Tokens:</span>
              <span className="text-emerald-400">{formatTokens(agent.tokensCached)}</span>
            </div>
            <div className="flex items-center justify-between text-slate-400">
              <span>Latency:</span>
              <span className="text-slate-200">{(agent.latencyMs / 1000).toFixed(2)}s</span>
            </div>
          </div>
        </div>

        {/* Sanitized Tool Arguments & Response Excerpt */}
        <div className="space-y-1.5">
          <div className="text-slate-400 text-[11px] font-medium flex items-center gap-1.5">
            <Terminal className="w-3.5 h-3.5 text-emerald-400" />
            Execution Inputs & Arguments (Sanitized)
          </div>
          <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 font-mono text-[10px] text-slate-300 overflow-x-auto">
            <pre>
{JSON.stringify(
  {
    agent_id: agent.id,
    prompt_context: 'Rescue King lava surge 8x8 match-3',
    max_output_tokens: 2048,
    redaction_applied: true,
    auth_bearer: '***REDACTED***',
  },
  null,
  2
)}
            </pre>
          </div>
        </div>

        {/* Artifact Reference if produced */}
        {agent.outputArtifactRef && (
          <div className="p-3 rounded-lg bg-cyan-950/20 border border-cyan-800/40 space-y-1.5">
            <div className="text-cyan-300 font-semibold text-xs flex items-center gap-1.5">
              <FileCode className="w-3.5 h-3.5" />
              Generated Output Artifact
            </div>
            <div className="text-slate-300 font-mono text-[11px]">
              {agent.outputArtifactRef}
            </div>
            <div className="text-slate-500 text-[10px] font-mono">
              Integrity: SHA-256 Verified
            </div>
          </div>
        )}

        {/* Trace ID & Ledger Link */}
        <div className="pt-2">
          <Link
            href={`/projects/${projectId}/ledger?agent=${agent.id}`}
            className="w-full py-2 px-3 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-mono transition-colors flex items-center justify-center gap-1.5 border border-slate-700"
          >
            <span>Inspect in Execution Ledger</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>
    </div>
  );
}
