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
  Sparkles,
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
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-apple-purple/10 border border-apple-purple/20 text-apple-purple text-xs font-medium mb-3">
            <FlaskConical className="w-3.5 h-3.5" />
            <span>M03 · A/B Experimentation & Learning Loop</span>
          </div>
          <h1 className="text-2xl font-semibold tracking-tight text-neutral-100">
            Creative Experiments & Variant Matrix
          </h1>
          <p className="text-neutral-400 text-xs sm:text-sm mt-1 max-w-2xl leading-relaxed">
            Single-variable mutation testing. Rigorously isolates synthetic offline QA evaluations from real ad network campaign attribution metrics.
          </p>
        </div>

        {/* Action & Filter */}
        <div className="flex items-center gap-3">
          <div className="apple-segmented">
            <button
              onClick={() => setFilterMode('all')}
              className={cn('apple-segmented-item text-xs', filterMode === 'all' && 'active')}
            >
              All Variants
            </button>
            <button
              onClick={() => setFilterMode('real_campaign')}
              className={cn('apple-segmented-item text-xs', filterMode === 'real_campaign' && 'active')}
            >
              Real Campaigns
            </button>
            <button
              onClick={() => setFilterMode('offline')}
              className={cn('apple-segmented-item text-xs', filterMode === 'offline' && 'active')}
            >
              Offline QA
            </button>
          </div>

          <button
            onClick={handleCreateExperiment}
            className="apple-btn-primary flex items-center gap-2 py-2 px-4 shadow-apple-sm text-xs"
          >
            <Plus className="w-4 h-4" />
            <span>Create Experiment</span>
          </button>
        </div>
      </div>

      {/* Experiments List */}
      <div className="space-y-6">
        {filtered.map((exp) => (
          <div
            key={exp.id}
            className="p-6 rounded-3xl bg-white/[0.03] border border-white/[0.08] backdrop-blur-xl shadow-apple-sm space-y-5"
          >
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-white/[0.06] pb-4">
              <div>
                <div className="flex items-center gap-2.5">
                  <h3 className="font-semibold text-base text-neutral-100">{exp.title}</h3>
                  <span
                    className={cn(
                      'text-[11px] font-medium px-2.5 py-0.5 rounded-full border',
                      exp.mode === 'real_campaign'
                        ? 'bg-apple-emerald/10 text-apple-emerald border-apple-emerald/20'
                        : 'bg-apple-purple/10 text-apple-purple border-apple-purple/20'
                    )}
                  >
                    {exp.mode === 'real_campaign' ? 'Real Campaign (Attribution Ingested)' : 'Synthetic Offline QA'}
                  </span>
                </div>
                <div className="text-xs text-neutral-400 mt-1 font-mono">
                  Controlled Variable: <span className="text-apple-blue font-medium">{exp.variable}</span>
                </div>
              </div>

              <div className="sm:text-right">
                <span className="text-[10px] uppercase font-semibold text-neutral-500 tracking-wider">Leading Variant</span>
                <div className="text-xs font-mono font-semibold text-apple-emerald mt-0.5">{exp.winner}</div>
              </div>
            </div>

            {/* Variant Comparison Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {exp.variants.map((v, i) => (
                <div
                  key={i}
                  className="p-4 rounded-2xl bg-white/[0.02] border border-white/[0.06] space-y-3 hover:border-white/[0.12] transition-colors"
                >
                  <div className="font-semibold text-xs text-neutral-200 flex items-center justify-between">
                    <span>{v.name}</span>
                    {v.syntheticScore && (
                      <span className="text-xs text-apple-purple font-mono font-medium">
                        Score: {v.syntheticScore} / 5.0
                      </span>
                    )}
                  </div>

                  {exp.mode === 'real_campaign' ? (
                    <div className="grid grid-cols-3 gap-2 font-mono text-xs">
                      <div className="p-2.5 rounded-xl bg-white/[0.03] border border-white/[0.04] text-center">
                        <div className="text-[10px] text-neutral-500 uppercase tracking-wide">CTR</div>
                        <div className="text-neutral-100 font-semibold mt-1">
                          {calcCTR(v.clicks, v.impressions)}
                        </div>
                      </div>
                      <div className="p-2.5 rounded-xl bg-white/[0.03] border border-white/[0.04] text-center">
                        <div className="text-[10px] text-neutral-500 uppercase tracking-wide">CPI</div>
                        <div className="text-apple-emerald font-semibold mt-1">
                          {calcCPI(v.spend, v.installs)}
                        </div>
                      </div>
                      <div className="p-2.5 rounded-xl bg-white/[0.03] border border-white/[0.04] text-center">
                        <div className="text-[10px] text-neutral-500 uppercase tracking-wide">IPM</div>
                        <div className="text-apple-blue font-semibold mt-1">
                          {calcIPM(v.installs, v.impressions)}
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="p-4 rounded-xl bg-white/[0.03] border border-white/[0.04] font-mono text-xs text-center space-y-1">
                      <div className="text-[10px] text-neutral-400 uppercase tracking-wider">Multi-Agent Rubric Score</div>
                      <div className="text-xl font-bold text-apple-purple">{v.syntheticScore} / 5.0</div>
                    </div>
                  )}

                  <div className="flex items-center justify-between text-[11px] font-mono text-neutral-500 pt-1 border-t border-white/[0.04]">
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
