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
      color: 'border-apple-teal/30 bg-apple-teal/5 text-apple-teal',
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
      color: 'border-apple-blue/30 bg-apple-blue/5 text-apple-blue',
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
      color: 'border-apple-purple/30 bg-apple-purple/5 text-apple-purple',
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
      color: 'border-apple-amber/30 bg-apple-amber/5 text-apple-amber',
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
      color: 'border-apple-emerald/30 bg-apple-emerald/5 text-apple-emerald',
      steps: [
        { name: 'Reasoned Human Approval', status: 'done', duration: '37.7s', worker: 'usr_creative_lead' },
        { name: 'Run Manifest Cryptographic Freeze', status: 'done', duration: '0.1s', worker: 'PostgreSQL Ledger' },
      ],
    },
  ];

  return (
    <div className="flex-1 p-6 overflow-y-auto space-y-6 select-none bg-[#0a0d14]">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 rounded-2xl bg-white/[0.03] border border-white/[0.06] shadow-apple-sm">
        <div>
          <div className="flex items-center gap-2">
            <Flame className="w-4 h-4 text-apple-amber" />
            <h2 className="text-sm font-semibold tracking-tight text-neutral-100">
              Factory Floor Concurrency Swimlane
            </h2>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-apple-emerald/15 text-apple-emerald border border-apple-emerald/25 font-semibold">
              E2E DAG Synchronized
            </span>
          </div>
          <p className="text-[11px] text-neutral-400 mt-0.5">
            Real-time parallel execution stages, worker cluster assignments, and pipeline timings.
          </p>
        </div>

        <div className="flex items-center gap-3 text-xs font-mono">
          <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/[0.04] border border-white/[0.06] text-neutral-300">
            <span className="text-neutral-500">Run:</span>
            <span className="text-apple-teal font-semibold">{activeRunId}</span>
            <span className="text-neutral-600">•</span>
            <span className="text-apple-emerald">{runStatus.toUpperCase()}</span>
          </div>
        </div>
      </div>

      {/* Swimlane Tracks */}
      <div className="space-y-4">
        {tracks.map((track) => (
          <div
            key={track.id}
            className={cn(
              'rounded-2xl border p-4 space-y-3 transition-all bg-white/[0.02]',
              track.color
            )}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <span className="text-xs font-semibold tracking-tight text-neutral-100">{track.title}</span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-white/[0.06] text-neutral-400 border border-white/[0.08]">
                  {track.category}
                </span>
              </div>
              <span className="text-xs font-mono font-semibold text-neutral-300">{track.duration}</span>
            </div>

            {/* Steps in Track */}
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
              {track.steps.map((step, idx) => (
                <div
                  key={idx}
                  className="p-3 rounded-xl bg-black/30 border border-white/[0.05] space-y-1.5"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-medium text-neutral-200 truncate">{step.name}</span>
                    {step.status === 'done' && <CheckCircle2 className="w-3.5 h-3.5 text-apple-emerald flex-shrink-0" />}
                    {step.status === 'retried' && (
                      <span className="text-[9px] font-mono text-apple-amber flex items-center gap-1 flex-shrink-0">
                        <RotateCcw className="w-3 h-3" /> Retried
                      </span>
                    )}
                    {step.status === 'warn' && <AlertTriangle className="w-3.5 h-3.5 text-apple-amber flex-shrink-0" />}
                  </div>
                  <div className="flex items-center justify-between text-[10px] font-mono text-neutral-500">
                    <span className="truncate pr-1">{step.worker}</span>
                    <span className="text-neutral-400 flex-shrink-0">{step.duration}</span>
                  </div>
                  {(step as any).note && (
                    <div className="text-[9px] font-mono text-apple-amber/90 pt-0.5">
                      {(step as any).note}
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
