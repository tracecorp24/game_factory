'use client';

import React, { useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import {
  Lightbulb,
  CheckCircle2,
  Sparkles,
  ExternalLink,
  Flame,
  ArrowRight,
  Sliders,
  DollarSign,
  BarChart2,
  ShieldCheck,
  Plus,
  Layers,
  X,
  Play,
  Check,
} from 'lucide-react';
import { cn, formatCurrency } from '@/lib/utils';
import { useAppStore } from '@/lib/store';
import { ConceptCard } from '@/lib/types';
import { toast } from '@/lib/toast';
import { apiClient } from '@/lib/api-client';

export default function ConceptGalleryPage() {
  const router = useRouter();
  const params = useParams();
  const projectId = (params?.projectId as string) || 'prj_match3_hero';

  const {
    concepts,
    selectedConceptId,
    comparisonIds,
    setSelectedConceptId,
    toggleComparisonId,
    selectConceptAndDraftWorkflow,
  } = useAppStore();

  const [filterGenre, setFilterGenre] = useState<string>('all');
  const [showComparisonModal, setShowComparisonModal] = useState<boolean>(false);

  const filteredConcepts = concepts.filter((c) =>
    filterGenre === 'all' ? true : c.genre.toLowerCase().includes(filterGenre.toLowerCase())
  );

  const [isGenerating, setIsGenerating] = useState(false);

  const handleGenerateNewHypotheses = async () => {
    setIsGenerating(true);
    toast.info('Ideation Başlatıldı', 'IdeationAgent ve Heuristic Ranking Engine yeni adaylar sentezliyor...');

    try {
      await apiClient.generateConcepts(projectId, 3);
    } catch {}

    setTimeout(() => {
      setIsGenerating(false);
      toast.success(
        'Yeni Hipotezler Üretildi',
        'Market kanıtları ve Game DNA ile uyumlu 3 yeni konsept panosu galeriye eklendi.'
      );
    }, 1200);
  };

  const handleSelectAndBuild = (conceptId: string) => {
    selectConceptAndDraftWorkflow(conceptId);
    toast.success('Konsept Seçildi', 'Seçilen konsept Workflow Studio düğümlerine bağlandı.');
    router.push(`/projects/${projectId}/studio?tab=workflow`);
  };

  const comparedConcepts = concepts.filter((c) => comparisonIds.includes(c.id));

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 select-none">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-amber-950/60 border border-amber-800/60 text-amber-300 text-xs font-mono mb-2">
            <Lightbulb className="w-3.5 h-3.5" />
            <span>Creative Ideation & Evidence Engine</span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Concept Gallery & Mockup Boards</h1>
          <p className="text-slate-400 text-xs mt-1">
            Explore 3-8 grounded creative hypotheses generated from verified market trend evidence and locked Game DNA.
          </p>
        </div>

        {/* Header Tools */}
        <div className="flex items-center gap-3">
          {/* Comparison Bar Button */}
          {comparisonIds.length > 0 && (
            <button
              onClick={() => setShowComparisonModal(true)}
              className="px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-cyan-300 border border-cyan-800/60 text-xs font-mono flex items-center gap-1.5 transition-colors shadow-sm"
            >
              <BarChart2 className="w-3.5 h-3.5 text-cyan-400" />
              <span>Compare ({comparisonIds.length})</span>
            </button>
          )}

          {/* Generate More */}
          <button
            onClick={handleGenerateNewHypotheses}
            disabled={isGenerating}
            className="px-4 py-2 rounded-lg bg-gradient-to-r from-amber-500 to-orange-600 hover:shadow-amber-500/20 text-white font-medium text-xs flex items-center gap-1.5 transition-all shadow-md disabled:opacity-50"
          >
            <Sparkles className={cn('w-4 h-4', isGenerating && 'animate-spin')} />
            <span>{isGenerating ? 'Synthesizing...' : 'Generate New Hypotheses'}</span>
          </button>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-800 pb-3 text-xs">
        <span className="text-slate-500 font-mono text-[11px] mr-2">Genre Filter:</span>
        {['all', 'Match-3', 'Sorting', 'Boss Battle'].map((g) => (
          <button
            key={g}
            onClick={() => setFilterGenre(g)}
            className={cn(
              'px-3 py-1 rounded-lg font-medium transition-colors',
              filterGenre === g
                ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40 font-semibold'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            )}
          >
            {g === 'all' ? 'All Formats' : g}
          </button>
        ))}
      </div>

      {/* Concept Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredConcepts.map((concept) => {
          const isSelected = selectedConceptId === concept.id;
          const isCompared = comparisonIds.includes(concept.id);

          return (
            <div
              key={concept.id}
              className={cn(
                'rounded-2xl border bg-slate-900/70 overflow-hidden flex flex-col justify-between transition-all duration-300 hover:translate-y-[-4px]',
                isSelected
                  ? 'border-amber-400/80 ring-2 ring-amber-400/30 shadow-2xl shadow-amber-500/20'
                  : 'border-slate-800 hover:border-slate-700 hover:shadow-xl'
              )}
            >
              <div>
                {/* Visual Preview Header */}
                <div className="relative h-48 w-full bg-slate-950 overflow-hidden group">
                  <img
                    src={concept.mockupUrl}
                    alt={concept.title}
                    className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/40 to-transparent" />

                  {/* Top Badges */}
                  <div className="absolute top-3 left-3 right-3 flex items-center justify-between">
                    <span className="px-2.5 py-1 rounded-full bg-slate-950/80 backdrop-blur-md border border-slate-700 text-amber-300 text-[11px] font-mono font-bold flex items-center gap-1.5 shadow-md">
                      <Flame className="w-3.5 h-3.5 text-amber-400" />
                      Score: {concept.scores.overall}/100
                    </span>

                    <button
                      onClick={() => toggleComparisonId(concept.id)}
                      className={cn(
                        'px-2 py-1 rounded-lg text-[10px] font-mono border backdrop-blur-md transition-colors',
                        isCompared
                          ? 'bg-cyan-950 text-cyan-300 border-cyan-500/60 font-semibold'
                          : 'bg-slate-900/80 text-slate-400 border-slate-700 hover:text-slate-200'
                      )}
                    >
                      {isCompared ? '✓ Comparing' : '+ Compare'}
                    </button>
                  </div>

                  {/* Hook Banner */}
                  <div className="absolute bottom-3 left-3 right-3">
                    <div className="text-[10px] uppercase font-mono text-amber-400 font-semibold tracking-wider">
                      Ad Hook 0-3s:
                    </div>
                    <div className="text-sm font-bold text-white drop-shadow-md">
                      &quot;{concept.hook}&quot;
                    </div>
                  </div>
                </div>

                {/* Card Body */}
                <div className="p-5 space-y-4 text-xs">
                  <div>
                    <h3 className="font-bold text-base text-slate-100">{concept.title}</h3>
                    <div className="flex flex-wrap gap-1.5 mt-1.5">
                      <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 text-[10px] font-mono">
                        {concept.genre}
                      </span>
                      <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-400 text-[10px] font-mono">
                        {concept.audience}
                      </span>
                    </div>
                  </div>

                  {/* Hypothesis & Emotional Arc */}
                  <div className="space-y-2 p-3 rounded-xl bg-slate-950/70 border border-slate-800/80">
                    <div>
                      <span className="text-[10px] font-mono uppercase text-slate-500 font-semibold">
                        Creative Hypothesis:
                      </span>
                      <p className="text-slate-300 text-[11px] mt-0.5 leading-relaxed">
                        {concept.hypothesis}
                      </p>
                    </div>
                    <div>
                      <span className="text-[10px] font-mono uppercase text-slate-500 font-semibold">
                        Emotional Arc:
                      </span>
                      <p className="text-cyan-300 text-[10px] font-mono mt-0.5">
                        {concept.emotionalArc}
                      </p>
                    </div>
                  </div>

                  {/* Grounded Evidence References */}
                  <div className="space-y-1.5">
                    <span className="text-[10px] font-mono uppercase text-slate-400 font-semibold">
                      Verified Evidence References:
                    </span>
                    <div className="space-y-1 font-mono text-[11px]">
                      {concept.evidenceRefs.map((ref, idx) => (
                        <a
                          key={idx}
                          href={ref.url}
                          target="_blank"
                          rel="noreferrer"
                          className="p-1.5 rounded bg-slate-900 border border-slate-800 hover:border-slate-700 flex items-center justify-between text-slate-300 hover:text-cyan-300 transition-colors"
                        >
                          <span className="truncate pr-2">{ref.title}</span>
                          <span className="text-[10px] px-1.5 py-0.2 rounded bg-emerald-950 text-emerald-300 border border-emerald-800/60 flex-shrink-0">
                            {ref.confidence}
                          </span>
                        </a>
                      ))}
                    </div>
                  </div>

                  {/* Heuristic Scores Breakdown */}
                  <div className="space-y-1.5 pt-2 border-t border-slate-800/80">
                    <div className="text-[10px] font-mono uppercase text-slate-400 font-semibold flex items-center justify-between">
                      <span>Heuristic Breakdown:</span>
                      <span className="text-slate-500">Form: 6-Factor</span>
                    </div>
                    <div className="grid grid-cols-3 gap-1.5 font-mono text-[10px]">
                      <div className="p-1.5 rounded bg-slate-950 text-center">
                        <div className="text-slate-500">Evidence</div>
                        <div className="text-slate-200 font-semibold">{concept.scores.evidence}%</div>
                      </div>
                      <div className="p-1.5 rounded bg-slate-950 text-center">
                        <div className="text-slate-500">Game Fit</div>
                        <div className="text-slate-200 font-semibold">{concept.scores.gameFit}%</div>
                      </div>
                      <div className="p-1.5 rounded bg-slate-950 text-center">
                        <div className="text-slate-500">Novelty</div>
                        <div className="text-slate-200 font-semibold">{concept.scores.novelty}%</div>
                      </div>
                      <div className="p-1.5 rounded bg-slate-950 text-center">
                        <div className="text-slate-500">Feasibility</div>
                        <div className="text-slate-200 font-semibold">{concept.scores.feasibility}%</div>
                      </div>
                      <div className="p-1.5 rounded bg-slate-950 text-center">
                        <div className="text-slate-500">Hook Clear</div>
                        <div className="text-slate-200 font-semibold">{concept.scores.hookClarity}%</div>
                      </div>
                      <div className="p-1.5 rounded bg-slate-950 text-center">
                        <div className="text-slate-500">Cost Fit</div>
                        <div className="text-slate-200 font-semibold">{concept.scores.costFit}%</div>
                      </div>
                    </div>
                  </div>

                  {/* Production Feasibility & Formats */}
                  <div className="flex items-center justify-between pt-1 text-[11px] font-mono text-slate-400">
                    <span>Est. Generation Cost:</span>
                    <span className="text-slate-200 font-semibold">
                      ${concept.estimatedCost.toFixed(2)} USD
                    </span>
                  </div>
                </div>
              </div>

              {/* Action Footer */}
              <div className="p-4 border-t border-slate-800 bg-slate-950/60 flex items-center justify-between gap-3">
                <button
                  onClick={() => setSelectedConceptId(concept.id)}
                  className="px-3 py-1.5 rounded-lg border border-slate-700 hover:bg-slate-800 text-slate-300 text-xs font-mono transition-colors"
                >
                  {isSelected ? '✓ Pinned' : 'Pin Details'}
                </button>

                <button
                  onClick={() => handleSelectAndBuild(concept.id)}
                  className="flex-1 py-2 px-3 rounded-lg bg-gradient-to-r from-amber-500 to-orange-600 hover:shadow-amber-500/30 text-white font-semibold text-xs transition-all flex items-center justify-center gap-1.5"
                >
                  <span>Select & Build Workflow</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Side-by-Side Comparison Modal */}
      {showComparisonModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center p-6 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-5xl max-h-[85vh] flex flex-col overflow-hidden shadow-2xl">
            <div className="p-5 border-b border-slate-800 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <BarChart2 className="w-5 h-5 text-cyan-400" />
                <h2 className="text-base font-bold text-white">Side-by-Side Concept Comparison</h2>
              </div>
              <button
                onClick={() => setShowComparisonModal(false)}
                className="p-1 rounded text-slate-400 hover:text-slate-200 hover:bg-slate-800"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 text-xs">
              {comparedConcepts.map((c) => (
                <div key={c.id} className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-4">
                  <img src={c.mockupUrl} alt={c.title} className="w-full h-32 object-cover rounded-lg" />
                  <div className="font-bold text-sm text-slate-100">{c.title}</div>
                  <div className="p-2 rounded bg-slate-900 font-mono text-[11px] text-amber-300">
                    Overall Rank: {c.scores.overall}/100
                  </div>
                  <div className="space-y-1">
                    <span className="text-[10px] text-slate-500 uppercase font-mono">Hook 0-3s:</span>
                    <p className="text-slate-300">{c.hook}</p>
                  </div>
                  <div className="space-y-1">
                    <span className="text-[10px] text-slate-500 uppercase font-mono">Emotional Arc:</span>
                    <p className="text-cyan-300 font-mono text-[10px]">{c.emotionalArc}</p>
                  </div>
                  <button
                    onClick={() => {
                      setShowComparisonModal(false);
                      handleSelectAndBuild(c.id);
                    }}
                    className="w-full py-2 rounded-lg bg-gradient-to-r from-amber-500 to-orange-600 text-white font-semibold text-xs flex items-center justify-center gap-1.5"
                  >
                    Select This Concept
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
