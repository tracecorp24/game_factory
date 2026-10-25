'use client';

import React, { useState } from 'react';
import {
  FlaskConical,
  Plus,
  TrendingUp,
  Percent,
  DollarSign,
  Layers,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useAppStore } from '@/lib/store';
import { toast } from '@/lib/toast';

interface ExperimentVariant {
  name: string;
  impressions: number;
  clicks: number;
  installs: number;
  spend: number;
  syntheticScore?: number;
}

interface ExperimentItem {
  id: string;
  title: string;
  variable: string;
  mode: 'real_campaign' | 'offline';
  variants: ExperimentVariant[];
  winner: string;
  status: string;
}

export default function ExperimentsPage() {
  const { projectId } = useAppStore();
  const [filterMode, setFilterMode] = useState<'all' | 'offline' | 'real_campaign'>('all');

  const [experimentsList, setExperimentsList] = useState<ExperimentItem[]>([
    {
      id: 'exp_lava_vs_freeze',
      title: 'Hook Urgency: Rising Lava vs Ice Freeze',
      variable: '0-3s Opening Hazard',
      mode: 'real_campaign',
      variants: [
        { name: 'Variant A (Rising Lava)', impressions: 125000, clicks: 5800, installs: 840, spend: 320.0, syntheticScore: 4.6 },
        { name: 'Variant B (Ice Freeze)', impressions: 118000, clicks: 4200, installs: 510, spend: 310.0, syntheticScore: 3.9 },
      ],
      winner: 'Variant A (+44% IPM)',
      status: 'Completed',
    },
    {
      id: 'exp_cta_copy',
      title: 'Endcard CTA: "Play Now" vs "Save King"',
      variable: 'CTA Endcard Wording',
      mode: 'offline',
      variants: [
        { name: 'Variant A ("Play Free Now")', impressions: 0, clicks: 0, installs: 0, spend: 0.0, syntheticScore: 4.8 },
        { name: 'Variant B ("Save the King!")', impressions: 0, clicks: 0, installs: 0, spend: 0.0, syntheticScore: 4.2 },
      ],
      winner: 'Variant A (Synthetic Judge)',
      status: 'Simulated QA',
    },
  ]);

  const handleCreateExperiment = () => {
    const newExp: ExperimentItem = {
      id: `exp_variant_${Date.now().toString(36).substring(4)}`,
      title: 'Audio Cascade FX: Tactile ASMR vs Orchestral Fanfare',
      variable: 'Audio SFX Track Layer',
      mode: 'offline',
      variants: [
        { name: 'Variant A (Tactile ASMR Pop)', impressions: 0, clicks: 0, installs: 0, spend: 0.0, syntheticScore: 4.9 },
        { name: 'Variant B (Orchestral Fanfare)', impressions: 0, clicks: 0, installs: 0, spend: 0.0, syntheticScore: 4.4 },
      ],
      winner: 'Variant A (Target +25% Retention)',
      status: 'Draft Matrix',
    };
    setExperimentsList((prev) => [newExp, ...prev]);
    toast.success('A/B Deneyi Oluşturuldu', 'Tek değişkenli mutasyon deneyi başarıyla oluşturuldu ve varyant matrisine eklendi.');
  };

  // Zero-safe metric calculators per Master Plan M03
  const calcCTR = (clicks: number, impressions: number): string => {
    if (!impressions || impressions === 0) return '—';
    return `${((clicks / impressions) * 100).toFixed(2)}%`;
  };

  const calcCPI = (spend: number, installs: number): string => {
    if (!installs || installs === 0) return '—';
    return `$${(spend / installs).toFixed(2)}`;
  };

  const calcIPM = (installs: number, impressions: number): string => {
    if (!impressions || impressions === 0) return '—';
    return `${((installs / impressions) * 1000).toFixed(1)}`;
  };

  const filtered = experimentsList.filter((e) =>
    filterMode === 'all' ? true : e.mode === filterMode
  );

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 select-none">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-blue-950/60 border border-blue-800/60 text-blue-300 text-xs font-mono mb-2">
            <FlaskConical className="w-3.5 h-3.5" />
            <span>M03 — A/B Experimentation & Learning Loop</span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Creative Experiments & Variant Matrix</h1>
          <p className="text-slate-400 text-xs mt-1">
            Single-variable mutation testing. Rigorously separates synthetic offline QA tests from real ad network campaign performance metrics.
          </p>
        </div>

        {/* Action & Filter */}
        <div className="flex items-center gap-2">
          <div className="flex items-center bg-slate-900 border border-slate-800 p-0.5 rounded-lg text-xs font-mono">
            {['all', 'real_campaign', 'offline'].map((m) => (
              <button
                key={m}
                onClick={() => setFilterMode(m as any)}
                className={cn(
                  'px-3 py-1 rounded-md transition-colors',
                  filterMode === m ? 'bg-cyan-500/20 text-cyan-300 font-semibold' : 'text-slate-400 hover:text-slate-200'
                )}
              >
                {m === 'all' ? 'All' : m === 'real_campaign' ? 'Real Campaigns' : 'Offline QA'}
              </button>
            ))}
          </div>

          <button
            onClick={handleCreateExperiment}
            className="px-4 py-2 rounded-lg bg-gradient-to-r from-blue-600 to-cyan-500 text-white font-medium text-xs flex items-center gap-1.5 transition-all shadow-md hover:shadow-cyan-500/20"
          >
            <Plus className="w-4 h-4" />
            <span>Create Experiment</span>
          </button>
        </div>
      </div>

      {/* Experiments List */}
      <div className="space-y-6">
        {filtered.map((exp) => (
          <div key={exp.id} className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800/80 pb-4">
              <div>
                <div className="flex items-center gap-2.5">
                  <h3 className="font-bold text-base text-slate-100">{exp.title}</h3>
                  <span className={cn(
                    'text-[10px] font-mono px-2 py-0.5 rounded border',
                    exp.mode === 'real_campaign'
                      ? 'bg-emerald-950 text-emerald-300 border-emerald-800/60'
                      : 'bg-purple-950 text-purple-300 border-purple-800/60'
                  )}>
                    {exp.mode === 'real_campaign' ? 'Real Campaign (CSV Ingested)' : 'Synthetic Offline QA'}
                  </span>
                </div>
                <div className="text-xs text-slate-400 mt-1 font-mono">
                  Controlled Variable: <span className="text-cyan-300">{exp.variable}</span>
                </div>
              </div>

              <div className="text-right">
                <span className="text-[10px] uppercase font-mono text-slate-500">Leading Variant:</span>
                <div className="text-xs font-mono font-bold text-emerald-400 mt-0.5">{exp.winner}</div>
              </div>
            </div>

            {/* Variant Comparison Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {exp.variants.map((v, i) => (
                <div key={i} className="p-4 rounded-xl bg-slate-950 border border-slate-800/80 space-y-3">
                  <div className="font-bold text-xs text-slate-200">{v.name}</div>

                  {exp.mode === 'real_campaign' ? (
                    <div className="grid grid-cols-3 gap-2 font-mono text-xs">
                      <div className="p-2 rounded bg-slate-900 text-center">
                        <div className="text-[10px] text-slate-500">CTR</div>
                        <div className="text-slate-200 font-semibold mt-0.5">
                          {calcCTR(v.clicks, v.impressions)}
                        </div>
                      </div>
                      <div className="p-2 rounded bg-slate-900 text-center">
                        <div className="text-[10px] text-slate-500">CPI</div>
                        <div className="text-emerald-400 font-semibold mt-0.5">
                          {calcCPI(v.spend, v.installs)}
                        </div>
                      </div>
                      <div className="p-2 rounded bg-slate-900 text-center">
                        <div className="text-[10px] text-slate-500">IPM</div>
                        <div className="text-cyan-300 font-semibold mt-0.5">
                          {calcIPM(v.installs, v.impressions)}
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="p-3 rounded bg-slate-900 font-mono text-xs text-center space-y-1">
                      <div className="text-[10px] text-slate-400">LLM Rubric Score (0-5)</div>
                      <div className="text-lg font-bold text-purple-300">{v.syntheticScore} / 5.0</div>
                    </div>
                  )}

                  <div className="flex items-center justify-between text-[10px] font-mono text-slate-500 pt-1">
                    <span>Impressions: {v.impressions.toLocaleString()}</span>
                    <span>Spend: ${v.spend.toFixed(1)}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
