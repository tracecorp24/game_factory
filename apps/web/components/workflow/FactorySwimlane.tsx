'use client';

import React from 'react';
import {
  Layers,
  Cpu,
  Clock,
  RotateCcw,
  CheckCircle2,
  AlertTriangle,
  Play,
  Pause,
  Sparkles,
  Zap,
  Flame,
  ArrowRight,
  ShieldCheck,
} from 'lucide-react';
import { cn, formatTimestamp } from '@/lib/utils';
import { useAppStore } from '@/lib/store';

export function FactorySwimlane() {
  const { activeRunId, runStatus } = useAppStore();

  const tracks = [
    {
      id: 'track_insight',
      title: 'Track 1: Market & Evidence Ingestion',
      category: 'Market Intelligence',
      status: 'completed',
      duration: '2.1s',
      color: 'border-cyan-500/50 bg-cyan-950/20 text-cyan-300',
      steps: [
        { name: 'Apple Charts Sync', status: 'done', duration: '1.2s', worker: 'ScraperWorker' },
        { name: 'Evidence Resolver', status: 'done', duration: '0.9s', worker: 'EvidenceAgent' },
      ],
    },
    {
      id: 'track_strategy',
      title: 'Track 2: Creative Ideation & Game DNA Freeze',
      category: 'Game DNA & Strategy',
      status: 'completed',
      duration: '2.4s',
      color: 'border-blue-500/50 bg-blue-950/20 text-blue-300',
      steps: [
        { name: 'DNA Spec Lock (v2.1)', status: 'done', duration: '0.7s', worker: 'GameDNAAgent' },
        { name: 'Hypothesis Generator (GPT-4o)', status: 'done', duration: '1.7s', worker: 'HypothesisAgent' },
      ],
    },
    {
      id: 'track_production',
      title: 'Track 3: Parallel Asset Production & Rendering',
      category: 'Asset Generation',
      status: 'completed',
      duration: '17.6s',
      color: 'border-purple-500/50 bg-purple-950/20 text-purple-300',
      steps: [
        { name: 'ComfyUI Keyframes (1080x1920)', status: 'done', duration: '3.2s', worker: 'GPU Cluster #1' },
        { name: 'Remotion 9:16 Video Render', status: 'retried', duration: '10.4s', worker: 'Worker Pool #2 (Attempt #2 Fallback)', note: 'Timeout 9000ms -> Recovered' },
        { name: 'Phaser Playable Sandbox Bundle', status: 'done', duration: '4.0s', worker: 'Isolated Sandbox' },
      ],
    },
    {
      id: 'track_quality',
      title: 'Track 4: 7-Layer Quality & Compliance Gates',
      category: 'Evaluation & QA',
      status: 'warning',
      duration: '3.6s',
      color: 'border-amber-500/50 bg-amber-950/20 text-amber-300',
      steps: [
        { name: 'Playwright Smoke Test', status: 'done', duration: '1.9s', worker: 'Chromium Headless' },
        { name: 'Similarity pHash Check', status: 'warn', duration: '0.5s', worker: 'Cosine 0.74 Overlap' },
        { name: 'LLM Rubric Judge (4.8/5.0)', status: 'done', duration: '1.2s', worker: 'GPT-4o Rubric v3' },
      ],
    },
    {
      id: 'track_governance',
      title: 'Track 5: Governance & Human Sign-off',
      category: 'Sign-off',
      status: 'completed',
      duration: '37.7s',
      color: 'border-emerald-500/50 bg-emerald-950/20 text-emerald-300',
      steps: [
        { name: 'Reasoned Human Approval', status: 'done', duration: '37.7s', worker: 'usr_creative_lead' },
        { name: 'Run Manifest Cryptographic Freeze', status: 'done', duration: '0.1s', worker: 'PostgreSQL Ledger' },
      ],
    },
  ];

  return (
    <div className="flex-1 p-6 overflow-y-auto space-y-6 select-none bg-[#090d16]">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 rounded-xl bg-slate-900/80 border border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <Flame className="w-4 h-4 text-cyan-400" />
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-100 font-mono">
              Factory Floor Concurrency Swimlane
            </h2>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800/80 font-semibold">
              Live Pipeline
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Real-time horizontal workflow concurrency. Shows parallel worker execution tracks, GPU cluster allocations, and checkpoint latencies.
          </p>
        </div>

        <div className="flex items-center gap-2 text-xs font-mono">
          <span className="text-slate-400">Total Run Time:</span>
          <span className="text-cyan-300 font-bold">73.68s</span>
        </div>
      </div>

      {/* Swimlane Tracks */}
      <div className="space-y-4">
        {tracks.map((track) => (
          <div
            key={track.id}
            className={cn('rounded-2xl border p-4 space-y-3 transition-all', track.color)}
          >
            {/* Track Title Bar */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Layers className="w-4 h-4" />
                <span className="font-bold text-xs text-slate-100">{track.title}</span>
                <span className="text-[10px] font-mono opacity-70">({track.category})</span>
              </div>
              <div className="flex items-center gap-2 text-xs font-mono">
                <span className="text-slate-400">Duration:</span>
                <span className="font-semibold text-slate-200">{track.duration}</span>
              </div>
            </div>

            {/* Horizontal Timeline Steps */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {track.steps.map((step, idx) => (
                <div
                  key={idx}
                  className="p-3 rounded-xl bg-slate-950/80 border border-slate-800/80 space-y-1.5 font-mono text-xs"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-slate-200 truncate pr-1">{step.name}</span>
                    {step.status === 'done' && (
                      <span className="flex items-center gap-1 text-[10px] text-emerald-400">
                        <CheckCircle2 className="w-3 h-3" /> Done
                      </span>
                    )}
                    {step.status === 'retried' && (
                      <span className="flex items-center gap-1 text-[10px] text-amber-400 bg-amber-950/80 px-1.5 py-0.5 rounded border border-amber-800/60">
                        <RotateCcw className="w-2.5 h-2.5" /> Retried
                      </span>
                    )}
                    {step.status === 'warn' && (
                      <span className="flex items-center gap-1 text-[10px] text-amber-400">
                        <AlertTriangle className="w-3 h-3" /> Warning
                      </span>
                    )}
                  </div>

                  <div className="flex items-center justify-between text-[10px] text-slate-400">
                    <span className="truncate max-w-[150px]">{step.worker}</span>
                    <span className="text-cyan-300 font-semibold">{step.duration}</span>
                  </div>

                  {step.note && (
                    <div className="text-[10px] text-rose-300/80 bg-rose-950/40 p-1 rounded border border-rose-900/40">
                      {step.note}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
