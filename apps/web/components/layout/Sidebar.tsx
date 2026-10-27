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
  Sparkles,
  Command,
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
    <aside className="w-60 border-r border-white/[0.06] bg-[#0c101a]/75 backdrop-blur-2xl flex flex-col flex-shrink-0 select-none z-30">
      {/* Apple Studio App Header */}
      <div className="h-14 border-b border-white/[0.06] px-4 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-apple-blue to-apple-purple flex items-center justify-center shadow-sm shadow-apple-blue/20 group-hover:scale-105 transition-all">
            <Sparkles className="w-3.5 h-3.5 text-white" />
          </div>
          <div>
            <div className="font-semibold text-xs tracking-tight text-neutral-100 flex items-center gap-1.5">
              CreativeForge
              <span className="text-[9px] px-1 py-0.2 rounded font-mono bg-white/[0.08] text-neutral-300 border border-white/[0.08] font-medium">
                v3.0
              </span>
            </div>
            <div className="text-[10px] text-neutral-400 font-normal">Game Factory Pro</div>
          </div>
        </Link>
      </div>

      {/* Navigation Groups */}
      <div className="flex-1 overflow-y-auto px-2.5 py-4 space-y-5">
        {navItems.map((group, idx) => (
          <div key={idx} className="space-y-0.5">
            <div className="px-2.5 py-1 text-[10px] uppercase font-semibold tracking-wider text-neutral-400">
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
                    'group flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-medium transition-all duration-150',
                    isActive
                      ? 'bg-apple-blue/15 text-apple-blue shadow-sm'
                      : 'text-neutral-300 hover:text-white hover:bg-white/[0.05]'
                  )}
                >
                  <div className="flex items-center gap-2.5">
                    <Icon
                      className={cn(
                        'w-3.5 h-3.5 transition-colors',
                        isActive ? 'text-apple-blue' : 'text-neutral-400 group-hover:text-neutral-200'
                      )}
                    />
                    <span className="tracking-tight">{item.name}</span>
                  </div>

                  {item.badge && (
                    <span
                      className={cn(
                        'text-[10px] px-1.5 py-0.5 rounded-full font-mono',
                        item.pulse
                          ? 'bg-apple-emerald/15 text-apple-emerald border border-apple-emerald/30 flex items-center gap-1 font-semibold'
                          : 'bg-white/[0.06] text-neutral-400 border border-white/[0.08]'
                      )}
                    >
                      {item.pulse && <span className="w-1.5 h-1.5 rounded-full bg-apple-emerald animate-pulse" />}
                      {item.badge}
                    </span>
                  )}
                </Link>
              );
            })}
          </div>
        ))}
      </div>

      {/* Project Status Pill in Footer */}
      <div className="p-3 border-t border-white/[0.06] bg-black/20">
        <div className="p-2 rounded-xl bg-white/[0.03] border border-white/[0.06] flex items-center justify-between">
          <div className="min-w-0">
            <div className="text-[10px] text-neutral-400">Current DNA</div>
            <div className="text-[11px] font-semibold text-neutral-200 truncate">Royal Match Strike</div>
          </div>
          <span className="text-[9px] font-mono px-1.5 py-0.5 rounded-full bg-apple-purple/15 text-apple-purple border border-apple-purple/25 flex-shrink-0">
            P0 Engine
          </span>
        </div>
      </div>
    </aside>
  );
}
