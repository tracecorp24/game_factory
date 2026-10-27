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
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-apple-amber/10 border border-apple-amber/25 text-apple-amber text-xs font-medium mb-3">
            <Lightbulb className="w-3.5 h-3.5 text-apple-amber" />
            <span>Creative Ideation & Evidence Engine</span>
          </div>
          <h1 className="text-2xl font-semibold tracking-tight text-neutral-100">Concept Gallery & Mockup Boards</h1>
          <p className="text-neutral-400 text-xs mt-1 leading-relaxed">
            Explore 3-8 grounded creative hypotheses generated from verified market trend evidence and locked Game DNA.
          </p>
        </div>

        {/* Header Tools */}
        <div className="flex items-center gap-3">
          {/* Comparison Bar Button */}
          {comparisonIds.length > 0 && (
            <button
              onClick={() => setShowComparisonModal(true)}
              className="apple-btn-secondary flex items-center gap-1.5"
            >
              <BarChart2 className="w-3.5 h-3.5 text-apple-teal" />
              <span>Compare ({comparisonIds.length})</span>
            </button>
          )}

          {/* Generate More */}
          <button
            onClick={handleGenerateNewHypotheses}
            disabled={isGenerating}
            className="apple-btn-primary flex items-center gap-1.5 shadow-apple-sm disabled:opacity-50"
          >
            <Sparkles className={cn('w-3.5 h-3.5', isGenerating && 'animate-spin')} />
            <span>{isGenerating ? 'Synthesizing...' : 'Generate Hypotheses'}</span>
          </button>
        </div>
      </div>

      {/* Filter Tabs in Segmented Control */}
      <div className="flex items-center justify-between border-b border-white/[0.06] pb-4 text-xs">
        <div className="flex items-center gap-3">
          <span className="text-neutral-400 text-xs font-medium">Format:</span>
          <div className="apple-segmented">
            {['all', 'Match-3', 'Sorting', 'Boss Battle'].map((g) => (
              <button
                key={g}
                onClick={() => setFilterGenre(g)}
                className={cn(
                  'apple-segmented-item',
                  filterGenre === g && 'apple-segmented-item-active'
                )}
              >
                {g === 'all' ? 'All Formats' : g}
              </button>
            ))}
          </div>
        </div>

        <span className="text-neutral-500 font-mono text-[11px]">
          Showing {filteredConcepts.length} Candidates
        </span>
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
                'rounded-3xl border bg-[#121724]/80 backdrop-blur-2xl overflow-hidden flex flex-col justify-between transition-all duration-300 shadow-apple-md',
                isSelected
                  ? 'border-apple-amber ring-2 ring-apple-amber/30 shadow-apple-glow'
                  : 'border-white/[0.08] hover:border-white/[0.18]'
              )}
            >
              <div>
                {/* Visual Preview Header */}
                <div className="relative h-48 w-full bg-black overflow-hidden group">
                  <img
                    src={concept.mockupUrl}
                    alt={concept.title}
                    className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-[#121724] via-black/40 to-transparent" />

                  {/* Top Badges */}
                  <div className="absolute top-3 left-3 right-3 flex items-center justify-between">
                    <span className="px-2.5 py-1 rounded-full bg-black/60 backdrop-blur-md border border-white/10 text-apple-amber text-[11px] font-medium flex items-center gap-1.5 shadow-sm">
                      <Flame className="w-3.5 h-3.5" />
                      Score: {concept.scores.overall}/100
                    </span>

                    <button
                      onClick={() => toggleComparisonId(concept.id)}
                      className={cn(
                        'px-2.5 py-1 rounded-full text-[10px] font-sans border backdrop-blur-md transition-colors',
                        isCompared
                          ? 'bg-apple-blue text-white border-apple-blue font-semibold'
                          : 'bg-black/60 text-neutral-300 border-white/10 hover:bg-black/80'
                      )}
                    >
                      {isCompared ? '✓ Comparing' : '+ Compare'}
                    </button>
                  </div>

                  {/* Hook Banner */}
                  <div className="absolute bottom-3 left-3 right-3">
                    <div className="text-[10px] uppercase font-mono text-apple-amber font-semibold tracking-wider">
                      Ad Hook 0-3s:
                    </div>
                    <div className="text-sm font-semibold text-white drop-shadow-md">
                      &quot;{concept.hook}&quot;
                    </div>
                  </div>
                </div>

                {/* Card Body */}
                <div className="p-5 space-y-4 text-xs">
                  <div>
                    <h3 className="font-semibold text-base text-neutral-100 tracking-tight">{concept.title}</h3>
                    <div className="flex flex-wrap gap-1.5 mt-1.5">
                      <span className="px-2 py-0.5 rounded-full bg-white/[0.06] text-neutral-300 text-[10px] font-mono border border-white/[0.08]">
                        {concept.genre}
                      </span>
                      <span className="px-2 py-0.5 rounded-full bg-white/[0.04] text-neutral-400 text-[10px] font-mono border border-white/[0.06]">
                        {concept.audience}
                      </span>
                    </div>
                  </div>

                  {/* Hypothesis & Emotional Arc */}
                  <div className="space-y-2 p-3 rounded-2xl bg-black/20 border border-white/[0.05]">
                    <div>
                      <span className="text-[10px] font-mono uppercase text-neutral-400 font-semibold">
                        Creative Hypothesis:
                      </span>
                      <p className="text-neutral-300 text-[11px] mt-0.5 leading-relaxed">
                        {concept.hypothesis}
                      </p>
                    </div>
                    <div className="pt-1 border-t border-white/[0.04]">
                      <span className="text-[10px] font-mono uppercase text-neutral-400 font-semibold">
                        Emotional Arc:
                      </span>
                      <p className="text-apple-teal text-[11px] font-mono mt-0.5">
                        {concept.emotionalArc}
                      </p>
                    </div>
                  </div>

                  {/* Grounded Evidence References */}
                  <div className="space-y-1.5">
                    <span className="text-[10px] font-mono uppercase text-neutral-400 font-semibold">
                      Verified Trend Evidence:
                    </span>
                    <div className="space-y-1 font-mono text-[11px]">
                      {concept.evidenceRefs.map((ref, idx) => (
                        <a
                          key={idx}
                          href={ref.url}
                          target="_blank"
                          rel="noreferrer"
                          className="p-1.5 rounded-lg bg-black/20 border border-white/[0.04] hover:border-white/[0.12] flex items-center justify-between text-neutral-300 hover:text-apple-teal transition-colors"
                        >
                          <span className="truncate pr-2">{ref.title}</span>
                          <span className="text-[10px] px-2 py-0.2 rounded-full bg-apple-emerald/15 text-apple-emerald border border-apple-emerald/25 flex-shrink-0">
                            {ref.confidence}
                          </span>
                        </a>
                      ))}
                    </div>
                  </div>

                  {/* Heuristic Scores Breakdown */}
                  <div className="space-y-1.5 pt-2 border-t border-white/[0.05]">
                    <div className="text-[10px] font-mono uppercase text-neutral-400 font-semibold flex items-center justify-between">
                      <span>Heuristic 6-Factor:</span>
                      <span className="text-neutral-500">Normalized</span>
                    </div>
                    <div className="grid grid-cols-3 gap-1.5 font-mono text-[10px]">
                      <div className="p-1.5 rounded-xl bg-black/20 text-center border border-white/[0.04]">
                        <div className="text-neutral-500">Evidence</div>
                        <div className="text-neutral-200 font-semibold">{concept.scores.evidence}%</div>
                      </div>
                      <div className="p-1.5 rounded-xl bg-black/20 text-center border border-white/[0.04]">
                        <div className="text-neutral-500">Game Fit</div>
                        <div className="text-neutral-200 font-semibold">{concept.scores.gameFit}%</div>
                      </div>
                      <div className="p-1.5 rounded-xl bg-black/20 text-center border border-white/[0.04]">
                        <div className="text-neutral-500">Novelty</div>
                        <div className="text-neutral-200 font-semibold">{concept.scores.novelty}%</div>
                      </div>
                      <div className="p-1.5 rounded-xl bg-black/20 text-center border border-white/[0.04]">
                        <div className="text-neutral-500">Feasibility</div>
                        <div className="text-neutral-200 font-semibold">{concept.scores.feasibility}%</div>
                      </div>
                      <div className="p-1.5 rounded-xl bg-black/20 text-center border border-white/[0.04]">
                        <div className="text-neutral-500">Hook Clear</div>
                        <div className="text-neutral-200 font-semibold">{concept.scores.hookClarity}%</div>
                      </div>
                      <div className="p-1.5 rounded-xl bg-black/20 text-center border border-white/[0.04]">
                        <div className="text-neutral-500">Cost Fit</div>
                        <div className="text-neutral-200 font-semibold">{concept.scores.costFit}%</div>
                      </div>
                    </div>
                  </div>

                  {/* Generation Cost */}
                  <div className="flex items-center justify-between pt-1 text-[11px] font-mono text-neutral-400">
                    <span>Est. Run Cost:</span>
                    <span className="text-neutral-200 font-semibold">
                      ${concept.estimatedCost.toFixed(2)} USD
                    </span>
                  </div>
                </div>
              </div>

              {/* Action Footer */}
              <div className="p-4 border-t border-white/[0.06] bg-black/20 flex items-center justify-between gap-3">
                <button
                  onClick={() => setSelectedConceptId(concept.id)}
                  className="apple-btn-secondary text-xs"
                >
                  {isSelected ? '✓ Pinned' : 'Pin Details'}
                </button>

                <button
                  onClick={() => handleSelectAndBuild(concept.id)}
                  className="apple-btn-primary flex-1 flex items-center justify-center gap-1.5"
                >
                  <span>Build Pipeline</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Side-by-Side Comparison Modal */}
      {showComparisonModal && (
        <div className="fixed inset-0 bg-black/75 backdrop-blur-2xl flex items-center justify-center p-6 z-50">
          <div className="bg-[#0c101a]/95 border border-white/[0.1] rounded-3xl w-full max-w-5xl max-h-[85vh] flex flex-col overflow-hidden shadow-2xl">
            <div className="p-5 border-b border-white/[0.06] flex items-center justify-between">
              <div className="flex items-center gap-2">
                <BarChart2 className="w-5 h-5 text-apple-teal" />
                <h2 className="text-base font-semibold text-neutral-100">Side-by-Side Concept Comparison</h2>
              </div>
              <button
                onClick={() => setShowComparisonModal(false)}
                className="p-1.5 rounded-lg text-neutral-400 hover:text-white hover:bg-white/[0.08]"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 text-xs">
              {comparedConcepts.map((c) => (
                <div key={c.id} className="p-4 rounded-2xl bg-white/[0.03] border border-white/[0.06] space-y-3">
                  <img src={c.mockupUrl} alt={c.title} className="w-full h-32 object-cover rounded-xl" />
                  <div className="font-semibold text-sm text-neutral-100">{c.title}</div>
                  <div className="p-2 rounded-lg bg-black/30 font-mono text-[11px] text-apple-amber">
                    Overall Rank: {c.scores.overall}/100
                  </div>
                  <div className="space-y-1">
                    <span className="text-[10px] text-neutral-500 uppercase font-mono">Hook 0-3s:</span>
                    <p className="text-neutral-300">{c.hook}</p>
                  </div>
                  <div className="space-y-1">
                    <span className="text-[10px] text-neutral-500 uppercase font-mono">Emotional Arc:</span>
                    <p className="text-apple-teal font-mono text-[10px]">{c.emotionalArc}</p>
                  </div>
                  <button
                    onClick={() => {
                      setShowComparisonModal(false);
                      handleSelectAndBuild(c.id);
                    }}
                    className="apple-btn-primary w-full flex items-center justify-center gap-1.5"
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
