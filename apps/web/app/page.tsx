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
  Sparkles,
  ChevronRight,
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
      color: 'text-apple-purple',
      bg: 'bg-apple-purple/10',
    },
    {
      title: 'Active Pipeline Run',
      value: 'run_88',
      sub: 'Completed (73.7s runtime)',
      icon: Radio,
      color: 'text-apple-emerald',
      bg: 'bg-apple-emerald/10',
    },
    {
      title: 'Approved Concepts',
      value: `${concepts.length} Ready`,
      sub: 'Top rank score: 89/100',
      icon: Lightbulb,
      color: 'text-apple-amber',
      bg: 'bg-apple-amber/10',
    },
    {
      title: 'Budget Allocation',
      value: `$${budgetSpent.toFixed(2)}`,
      sub: `Cap: $${budgetApproved.toFixed(2)} USD`,
      icon: Zap,
      color: 'text-apple-teal',
      bg: 'bg-apple-teal/10',
    },
  ];

  const quickLinks = [
    {
      title: 'Workflow Studio',
      description: 'Design and execute multi-agent DAG pipelines with React Flow canvas',
      href: `/projects/${projectId}/studio?tab=workflow`,
      icon: GitFork,
      color: 'bg-apple-blue/15 text-apple-blue',
    },
    {
      title: 'Agent Observatory',
      description: 'Real-time telemetry galaxy, live SSE stream, and time-travel replay',
      href: `/projects/${projectId}/studio?tab=agents&run=run_88`,
      icon: Radio,
      color: 'bg-apple-purple/15 text-apple-purple',
    },
    {
      title: 'Concept Gallery',
      description: 'Explore 3-8 heuristic-ranked playable & video concept mockup boards',
      href: `/projects/${projectId}/concepts`,
      icon: Lightbulb,
      color: 'bg-apple-amber/15 text-apple-amber',
    },
    {
      title: 'Execution Ledger',
      description: 'Inspect cryptographic append-only event trail and token/cost accounting',
      href: `/projects/${projectId}/ledger`,
      icon: ScrollText,
      color: 'bg-apple-emerald/15 text-apple-emerald',
    },
  ];

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 select-none">
      {/* Hero Welcome Card - Apple Vision Spatial Aesthetic */}
      <div className="relative rounded-3xl p-8 overflow-hidden bg-gradient-to-br from-[#121724]/90 via-[#0e121d]/90 to-[#0a0d14]/90 border border-white/[0.08] shadow-apple-lg">
        <div className="absolute top-0 right-0 w-80 h-80 bg-apple-blue/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/[0.06] border border-white/[0.08] text-neutral-300 text-xs font-medium mb-4">
            <Sparkles className="w-3.5 h-3.5 text-apple-blue" />
            <span>CreativeForge Studio v3.0 Pro</span>
          </div>
          <h1 className="text-3xl font-semibold tracking-tight text-neutral-100 mb-2">
            Multimodal Game Creative Intelligence Studio
          </h1>
          <p className="text-neutral-400 text-xs sm:text-sm leading-relaxed mb-6 font-normal">
            Autonomous end-to-end creative generation: Market trend scouting, structured ideation, ComfyUI visual assets, Remotion video composition, and isolated Phaser HTML5 playable sandboxes governed by 7 multi-layer quality gates.
          </p>

          <div className="flex flex-wrap items-center gap-3">
            <Link
              href={`/projects/${projectId}/studio?tab=workflow`}
              className="apple-btn-primary inline-flex items-center gap-2 py-2 px-4 shadow-apple-sm"
            >
              <GitFork className="w-4 h-4" />
              Open Workflow Studio
            </Link>
            <Link
              href={`/projects/${projectId}/studio?tab=agents&run=run_88`}
              className="apple-btn-secondary inline-flex items-center gap-2 py-2 px-4"
            >
              <Radio className="w-4 h-4 text-apple-emerald" />
              Launch Observatory
            </Link>
            <Link
              href={`/projects/${projectId}/concepts`}
              className="apple-btn-secondary inline-flex items-center gap-2 py-2 px-4"
            >
              <Lightbulb className="w-4 h-4 text-apple-amber" />
              Concept Gallery
            </Link>
          </div>
        </div>
      </div>

      {/* KPI Bento Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {kpis.map((kpi, i) => {
          const Icon = kpi.icon;
          return (
            <div
              key={i}
              className="p-5 rounded-2xl bg-white/[0.03] border border-white/[0.06] backdrop-blur-xl transition-all hover:border-white/[0.14] hover:shadow-apple-sm"
            >
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs text-neutral-400 font-medium tracking-tight">{kpi.title}</span>
                <div className={`p-2 rounded-xl ${kpi.bg}`}>
                  <Icon className={`w-4 h-4 ${kpi.color}`} />
                </div>
              </div>
              <div className="text-xl font-semibold text-neutral-100 font-sans tracking-tight">
                {kpi.value}
              </div>
              <div className="text-[11px] text-neutral-500 mt-1 font-mono">{kpi.sub}</div>
            </div>
          );
        })}
      </div>

      {/* Core Studio Modules */}
      <div className="space-y-3">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-neutral-400">
          Core Studio Modules
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {quickLinks.map((item, i) => {
            const Icon = item.icon;
            return (
              <Link
                key={i}
                href={item.href}
                className="group p-5 rounded-2xl bg-white/[0.03] border border-white/[0.06] hover:border-white/[0.14] hover:bg-white/[0.05] transition-all flex flex-col justify-between shadow-apple-sm"
              >
                <div>
                  <div
                    className={`w-10 h-10 rounded-xl ${item.color} flex items-center justify-center mb-4 transition-transform group-hover:scale-105`}
                  >
                    <Icon className="w-5 h-5" />
                  </div>
                  <h3 className="font-semibold text-sm text-neutral-200 group-hover:text-apple-blue transition-colors flex items-center justify-between">
                    <span>{item.title}</span>
                    <ArrowUpRight className="w-3.5 h-3.5 text-neutral-500 group-hover:text-apple-blue transition-colors" />
                  </h3>
                  <p className="text-xs text-neutral-400 mt-1.5 line-clamp-2 leading-relaxed">
                    {item.description}
                  </p>
                </div>
                <div className="mt-4 pt-3 border-t border-white/[0.05] flex items-center text-[11px] font-medium text-apple-blue">
                  <span>Enter Module</span>
                  <ChevronRight className="w-3.5 h-3.5 ml-1 transition-transform group-hover:translate-x-0.5" />
                </div>
              </Link>
            );
          })}
        </div>
      </div>

      {/* Recent Ledger Events Trail */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-neutral-400 flex items-center gap-2">
            <Clock className="w-3.5 h-3.5 text-apple-teal" />
            Append-Only Audit Trail ({events.length} Events)
          </h2>
          <Link
            href={`/projects/${projectId}/ledger`}
            className="text-xs text-apple-blue hover:underline font-medium"
          >
            Full Ledger →
          </Link>
        </div>

        <div className="rounded-2xl border border-white/[0.06] bg-white/[0.02] divide-y divide-white/[0.04] overflow-hidden font-mono text-xs">
          {events.slice(-5).reverse().map((evt) => (
            <div
              key={evt.event_id}
              className="p-3 flex flex-wrap items-center justify-between gap-3 hover:bg-white/[0.04] transition-colors"
            >
              <div className="flex items-center gap-3">
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-white/[0.06] text-neutral-400">
                  #{evt.run_seq}
                </span>
                <span className="font-semibold text-neutral-200">{evt.event_type}</span>
                <span className="text-neutral-500 text-[11px]">{evt.agent_id || evt.actor_id}</span>
              </div>
              <div className="flex items-center gap-4 text-neutral-400 text-[11px]">
                <span>{formatTimestamp(evt.occurred_at)}</span>
                <span className="text-neutral-600 truncate max-w-[140px]">
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
