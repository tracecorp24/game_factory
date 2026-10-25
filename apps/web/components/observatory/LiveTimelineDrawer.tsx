'use client';

import React, { useState } from 'react';
import {
  ChevronUp,
  ChevronDown,
  Activity,
  Terminal,
  ExternalLink,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
} from 'lucide-react';
import { cn, formatTimestamp } from '@/lib/utils';
import { useAppStore } from '@/lib/store';

export function LiveTimelineDrawer() {
  const [isOpen, setIsOpen] = useState(false);
  const { events, activeRunId, replayStep, setReplayStep } = useAppStore();

  return (
    <div
      className={cn(
        'absolute bottom-0 left-0 right-0 border-t border-slate-800 bg-[#070b14]/95 backdrop-blur-xl transition-all duration-300 z-10 flex flex-col',
        isOpen ? 'h-64' : 'h-9'
      )}
    >
      {/* Top Toggle Bar */}
      <div
        onClick={() => setIsOpen(!isOpen)}
        className="h-9 px-4 flex items-center justify-between cursor-pointer hover:bg-slate-900/60 transition-colors select-none"
      >
        <div className="flex items-center gap-2 text-xs font-mono">
          <Activity className="w-3.5 h-3.5 text-cyan-400" />
          <span className="font-semibold text-slate-300">Live Telemetry Timeline</span>
          <span className="text-[10px] text-slate-500">({events.length} events logged)</span>
        </div>

        <div className="flex items-center gap-2 text-xs text-slate-400">
          <span className="text-[11px] font-mono">
            Active: <span className="text-cyan-300 font-semibold">{activeRunId}</span>
          </span>
          {isOpen ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />}
        </div>
      </div>

      {/* Expanded List */}
      {isOpen && (
        <div className="flex-1 overflow-y-auto p-3 text-xs font-mono divide-y divide-slate-800/60 bg-[#050811]">
          {events.map((evt, idx) => {
            const isSelectedStep = idx === replayStep;
            return (
              <div
                key={evt.event_id}
                onClick={() => setReplayStep(idx)}
                className={cn(
                  'py-2 px-3 flex items-center justify-between cursor-pointer rounded transition-colors',
                  isSelectedStep ? 'bg-cyan-950/40 border border-cyan-800/60' : 'hover:bg-slate-900/50'
                )}
              >
                <div className="flex items-center gap-3">
                  <span className="text-[10px] text-slate-500 w-6">#{evt.run_seq}</span>
                  <span className="text-slate-400 text-[11px]">{formatTimestamp(evt.occurred_at)}</span>
                  <span
                    className={cn(
                      'font-semibold text-xs',
                      evt.event_type.includes('FAILED')
                        ? 'text-rose-400'
                        : evt.event_type.includes('COMPLETED')
                        ? 'text-emerald-300'
                        : 'text-cyan-300'
                    )}
                  >
                    {evt.event_type}
                  </span>
                  <span className="text-slate-400 text-[11px] hidden sm:inline">
                    {evt.agent_id ? `[${evt.agent_id}]` : `[${evt.actor_type}]`}
                  </span>
                  <span className="text-slate-500 text-[10px] truncate max-w-xs hidden md:inline">
                    {JSON.stringify(evt.payload_preview).slice(0, 60)}...
                  </span>
                </div>

                <div className="text-[10px] text-slate-500">
                  {evt.integrity_hash.slice(0, 8)}...
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
