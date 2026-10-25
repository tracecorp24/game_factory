'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  TrendingUp,
  Lightbulb,
  Dna,
  GitFork,
  Radio,
  Library,
  FlaskConical,
  ScrollText,
  BarChart3,
  ShieldCheck,
  Cpu,
  Lock,
  ChevronRight,
  Flame,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useAppStore } from '@/lib/store';

export function Sidebar() {
  const pathname = usePathname();
  const { projectId } = useAppStore();

  const navItems = [
    {
      title: 'Studio Core',
      items: [
        {
          name: 'Overview',
          href: `/`,
          icon: LayoutDashboard,
          badge: null,
        },
        {
          name: 'Trend Intelligence',
          href: `/projects/${projectId}/intelligence`,
          icon: TrendingUp,
          badge: 'Live Sync',
        },
        {
          name: 'Concept Gallery',
          href: `/projects/${projectId}/concepts`,
          icon: Lightbulb,
          badge: '3 Ranked',
        },
        {
          name: 'Game DNA',
          href: `/projects/${projectId}/game-dna`,
          icon: Dna,
          badge: 'v2.1 Frozen',
        },
        {
          name: 'Workflow Studio',
          href: `/projects/${projectId}/studio?tab=workflow`,
          icon: GitFork,
          badge: 'Editor',
        },
        {
          name: 'Agent Observatory',
          href: `/projects/${projectId}/studio?tab=agents&run=run_88`,
          icon: Radio,
          badge: 'Live Pulse',
          pulse: true,
        },
      ],
    },
    {
      title: 'Production & Analytics',
      items: [
        {
          name: 'Artifact Library',
          href: `/projects/${projectId}/artifacts`,
          icon: Library,
          badge: null,
        },
        {
          name: 'Experiments & A/B',
          href: `/projects/${projectId}/experiments`,
          icon: FlaskConical,
          badge: null,
        },
        {
          name: 'Execution Ledger',
          href: `/projects/${projectId}/ledger`,
          icon: ScrollText,
          badge: 'Append-Only',
        },
        {
          name: 'Analytics Dashboard',
          href: `/projects/${projectId}/analytics`,
          icon: BarChart3,
          badge: null,
        },
        {
          name: 'Quality Center',
          href: `/projects/${projectId}/quality`,
          icon: ShieldCheck,
          badge: '7 Gates',
        },
      ],
    },
    {
      title: 'Configuration',
      items: [
        {
          name: 'Model Registry',
          href: `/settings/models`,
          icon: Cpu,
          badge: 'LiteLLM',
        },
        {
          name: 'Security & Governance',
          href: `/settings/security`,
          icon: Lock,
          badge: null,
        },
      ],
    },
  ];

  return (
    <aside className="w-64 border-r border-slate-800 bg-[#070b14] flex flex-col flex-shrink-0 select-none z-30">
      {/* Brand Header */}
      <div className="h-16 border-b border-slate-800/80 px-5 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-500 via-blue-600 to-purple-600 flex items-center justify-center shadow-lg shadow-cyan-500/20 group-hover:shadow-cyan-500/40 transition-all">
            <Flame className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="font-bold text-sm tracking-wide bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent flex items-center gap-1.5">
              CreativeForge
              <span className="text-[10px] px-1.5 py-0.2 rounded font-mono bg-cyan-950 text-cyan-300 border border-cyan-800/60 font-semibold">
                v3.0
              </span>
            </div>
            <div className="text-[11px] text-slate-400 font-mono">Intelligence Studio</div>
          </div>
        </Link>
      </div>

      {/* Navigation Sections */}
      <div className="flex-1 overflow-y-auto px-3 py-4 space-y-6">
        {navItems.map((group, idx) => (
          <div key={idx} className="space-y-1">
            <div className="px-3 text-[10px] uppercase font-mono font-semibold tracking-wider text-slate-400">
              {group.title}
            </div>
            {group.items.map((item) => {
              const Icon = item.icon;
              const isActive =
                item.href.includes('?')
                  ? pathname + (typeof window !== 'undefined' ? window.location.search : '') === item.href
                  : pathname === item.href || (item.href !== '/' && pathname.startsWith(item.href));

              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    'group flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium transition-all duration-150',
                    isActive
                      ? 'bg-cyan-500/10 text-cyan-300 border border-cyan-500/30 shadow-sm shadow-cyan-500/10'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                  )}
                >
                  <div className="flex items-center gap-2.5">
                    <Icon
                      className={cn(
                        'w-4 h-4 transition-colors',
                        isActive
                          ? 'text-cyan-400'
                          : 'text-slate-500 group-hover:text-slate-300'
                      )}
                    />
                    <span>{item.name}</span>
                  </div>

                  {item.badge && (
                    <span
                      className={cn(
                        'text-[10px] px-1.5 py-0.5 rounded font-mono',
                        item.pulse
                          ? 'bg-emerald-950/80 text-emerald-400 border border-emerald-700/50 flex items-center gap-1 animate-pulse'
                          : 'bg-slate-800 text-slate-400'
                      )}
                    >
                      {item.pulse && <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />}
                      {item.badge}
                    </span>
                  )}
                </Link>
              );
            })}
          </div>
        ))}
      </div>

      {/* Footer Info & Active Project Badge */}
      <div className="p-3 border-t border-slate-800/80 bg-slate-950/50">
        <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800 flex items-center justify-between">
          <div>
            <div className="text-[11px] text-slate-400">Current Project</div>
            <div className="text-xs font-semibold text-slate-200">Royal Match Strike</div>
          </div>
          <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800/60">
            P0 Engine
          </span>
        </div>
      </div>
    </aside>
  );
}
