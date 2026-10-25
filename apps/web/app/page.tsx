'use client';

import React from 'react';
import Link from 'next/link';
import {
  Flame,
  GitFork,
  Radio,
  Lightbulb,
  Dna,
  ScrollText,
  BarChart3,
  Play,
  ArrowUpRight,
  ShieldCheck,
  CheckCircle2,
  Clock,
  Zap,
} from 'lucide-react';
import { useAppStore } from '@/lib/store';
import { formatCurrency, formatTokens, formatTimestamp } from '@/lib/utils';

export default function OverviewPage() {
  const { projectId, campaignId, budgetApproved, budgetSpent, events, concepts, gameDNA } = useAppStore();

  const kpis = [
    {
      title: 'Current Project',
      value: gameDNA.name,
      sub: `${projectId} (${gameDNA.version})`,
      icon: Dna,
      color: 'text-purple-400',
      border: 'border-purple-500/20',
      bg: 'bg-purple-950/20',
    },
    {
      title: 'Active Run',
      value: 'run_88',
      sub: 'Completed (73.7s runtime)',
      icon: Radio,
      color: 'text-emerald-400',
      border: 'border-emerald-500/20',
      bg: 'bg-emerald-950/20',
    },
    {
      title: 'Approved Concepts',
      value: `${concepts.length} Ready`,
      sub: 'Top rank score: 89/100',
      icon: Lightbulb,
      color: 'text-amber-400',
      border: 'border-amber-500/20',
      bg: 'bg-amber-950/20',
    },
    {
      title: 'Budget Allocation',
      value: `$${budgetSpent.toFixed(2)}`,
      sub: `Cap: $${budgetApproved.toFixed(2)} USD`,
      icon: Zap,
      color: 'text-cyan-400',
      border: 'border-cyan-500/20',
      bg: 'bg-cyan-950/20',
    },
  ];

  const quickLinks = [
    {
      title: 'Workflow Studio',
      description: 'Design and execute multi-agent DAG pipelines with React Flow canvas',
      href: `/projects/${projectId}/studio?tab=workflow`,
      icon: GitFork,
      color: 'from-blue-600 to-cyan-500',
    },
    {
      title: 'Agent Observatory',
      description: 'Real-time telemetry galaxy, live SSE stream, and time-travel replay',
      href: `/projects/${projectId}/studio?tab=agents&run=run_88`,
      icon: Radio,
      color: 'from-purple-600 to-pink-500',
    },
    {
      title: 'Concept Gallery',
      description: 'Explore 3-8 heuristic-ranked playable & video concept mockup boards',
      href: `/projects/${projectId}/concepts`,
      icon: Lightbulb,
      color: 'from-amber-500 to-orange-600',
    },
    {
      title: 'Execution Ledger',
      description: 'Inspect cryptographic append-only event trail and token/cost accounting',
      href: `/projects/${projectId}/ledger`,
      icon: ScrollText,
      color: 'from-emerald-500 to-teal-600',
    },
  ];

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      {/* Hero Welcome */}
      <div className="relative rounded-2xl p-8 overflow-hidden bg-gradient-to-r from-slate-900 via-[#0d1527] to-slate-900 border border-slate-800 shadow-2xl">
        <div className="absolute top-0 right-0 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-950/80 border border-cyan-800/80 text-cyan-300 text-xs font-mono mb-4">
            <Flame className="w-3.5 h-3.5 text-cyan-400" />
            <span>CreativeForge Intelligence Studio v3.0</span>
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white mb-2">
            Multimodal Game Creative Intelligence Studio
          </h1>
          <p className="text-slate-400 text-sm leading-relaxed mb-6">
            Autonomous end-to-end creative generation: Market trend scouting, structured ideation, ComfyUI visual assets, Remotion video composition, and isolated Phaser HTML5 playable sandboxes governed by 7 multi-layer quality gates.
          </p>

          <div className="flex flex-wrap items-center gap-3">
            <Link
              href={`/projects/${projectId}/studio?tab=workflow`}
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-medium text-xs shadow-lg shadow-cyan-500/25 hover:shadow-cyan-500/40 hover:scale-[1.02] transition-all"
            >
              <GitFork className="w-4 h-4" />
              Open Workflow Studio
            </Link>
            <Link
              href={`/projects/${projectId}/studio?tab=agents&run=run_88`}
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 font-medium text-xs transition-all"
            >
              <Radio className="w-4 h-4 text-emerald-400" />
              Launch Agent Observatory
            </Link>
            <Link
              href={`/projects/${projectId}/concepts`}
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 font-medium text-xs transition-all"
            >
              <Lightbulb className="w-4 h-4 text-amber-400" />
              View Concept Gallery
            </Link>
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {kpis.map((kpi, i) => {
          const Icon = kpi.icon;
          return (
            <div
              key={i}
              className={`p-5 rounded-xl bg-slate-900/60 border ${kpi.border} backdrop-blur-sm transition-all hover:translate-y-[-2px]`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs text-slate-400 font-medium">{kpi.title}</span>
                <div className={`p-2 rounded-lg ${kpi.bg}`}>
                  <Icon className={`w-4 h-4 ${kpi.color}`} />
                </div>
              </div>
              <div className="text-xl font-bold text-slate-100 font-mono tracking-tight">
                {kpi.value}
              </div>
              <div className="text-[11px] text-slate-500 mt-1 font-mono">{kpi.sub}</div>
            </div>
          );
        })}
      </div>

      {/* Quick Launch Action Grid */}
      <div className="space-y-3">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-400 font-mono">
          Core Studio Modules
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {quickLinks.map((item, i) => {
            const Icon = item.icon;
            return (
              <Link
                key={i}
                href={item.href}
                className="group p-5 rounded-xl bg-slate-900/50 border border-slate-800 hover:border-slate-700 hover:bg-slate-800/40 transition-all flex flex-col justify-between"
              >
                <div>
                  <div
                    className={`w-10 h-10 rounded-xl bg-gradient-to-tr ${item.color} flex items-center justify-center text-white mb-4 shadow-md group-hover:scale-105 transition-transform`}
                  >
                    <Icon className="w-5 h-5" />
                  </div>
                  <h3 className="font-semibold text-sm text-slate-200 group-hover:text-cyan-300 transition-colors flex items-center gap-1.5">
                    {item.title}
                    <ArrowUpRight className="w-3.5 h-3.5 opacity-0 group-hover:opacity-100 transition-opacity" />
                  </h3>
                  <p className="text-xs text-slate-400 mt-1.5 line-clamp-2 leading-relaxed">
                    {item.description}
                  </p>
                </div>
                <div className="mt-4 pt-3 border-t border-slate-800/60 flex items-center text-[11px] font-mono text-cyan-400 font-medium">
                  Enter Module →
                </div>
              </Link>
            );
          })}
        </div>
      </div>

      {/* Recent Ledger Events Trail */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-400 font-mono flex items-center gap-2">
            <Clock className="w-4 h-4 text-cyan-400" />
            Recent Append-Only Events Trail ({events.length} Events)
          </h2>
          <Link
            href={`/projects/${projectId}/ledger`}
            className="text-xs font-mono text-cyan-400 hover:underline"
          >
            Open Full Ledger →
          </Link>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/40 divide-y divide-slate-800/80 overflow-hidden font-mono text-xs">
          {events.slice(-5).reverse().map((evt) => (
            <div
              key={evt.event_id}
              className="p-3.5 flex flex-wrap items-center justify-between gap-3 hover:bg-slate-800/30 transition-colors"
            >
              <div className="flex items-center gap-3">
                <span className="text-[11px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">
                  #{evt.run_seq}
                </span>
                <span className="font-semibold text-cyan-300">{evt.event_type}</span>
                <span className="text-slate-500 text-[11px]">{evt.agent_id || evt.actor_id}</span>
              </div>
              <div className="flex items-center gap-4 text-slate-400 text-[11px]">
                <span>{formatTimestamp(evt.occurred_at)}</span>
                <span className="text-slate-600 truncate max-w-[140px]">
                  {evt.integrity_hash.substring(0, 12)}...
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
