'use client';

import React, { useState } from 'react';
import {
  ShieldCheck,
  AlertTriangle,
  CheckCircle2,
  Clock,
  UserCheck,
  FileText,
  ThumbsUp,
  ThumbsDown,
  RotateCcw,
  Sparkles,
  ExternalLink,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useAppStore } from '@/lib/store';
import { toast } from '@/lib/toast';

export default function QualityCenterPage() {
  const { projectId } = useAppStore();
  const [pendingReviewed, setPendingReviewed] = useState(false);
  const [reviewNote, setReviewNote] = useState(
    'King art style is strictly aligned with internal Game DNA v2; similarity warning is safely generic match-3 layout trope.'
  );

  const gates = [
    {
      id: 1,
      name: 'SchemaGate',
      category: 'Data Integrity',
      status: 'PASSED',
      score: '1.0 / 1.0',
      desc: 'Validates JSON contract, required fields, and UUIDv7 identifiers.',
    },
    {
      id: 2,
      name: 'TechnicalGate',
      category: 'Browser & Code QA',
      status: 'PASSED',
      score: '0 Errors',
      desc: 'Playwright headless mobile test. Zero JS runtime errors, responsive layout.',
    },
    {
      id: 3,
      name: 'GameTruthGate',
      category: 'Compliance',
      status: 'PASSED',
      score: '0.95 / 1.0',
      desc: 'Verifies creative claims vs locked Game DNA mechanics. Prohibits deceptive fake ads.',
    },
    {
      id: 4,
      name: 'VisualGate',
      category: 'Media Probe',
      status: 'PASSED',
      score: '9:16 OK',
      desc: 'Checks 1080x1920 resolution, color contrast ratio, CTA button legibility.',
    },
    {
      id: 5,
      name: 'SimilarityGate',
      category: 'Copyright & Originality',
      status: 'WARNING',
      score: '0.74 Cosine',
      desc: 'Perceptual hash (pHash) against competitor corpus. Raised advisory warning flag.',
    },
    {
      id: 6,
      name: 'LLMJudgeGate',
      category: 'Rubric AI Judge',
      status: 'PASSED',
      score: '4.8 / 5.0',
      desc: 'Multi-criteria rubric: Hook impact (5/5), pacing (4.8/5), clarity (4.6/5).',
    },
    {
      id: 7,
      name: 'HumanReviewGate',
      category: 'Governance & Sign-off',
      status: pendingReviewed ? 'APPROVED' : 'PENDING ACTION',
      score: pendingReviewed ? 'Approved' : 'Action Required',
      desc: 'Escalated to human lead due to SimilarityGate advisory warning flag.',
    },
  ];

  const handleApprove = () => {
    setPendingReviewed(true);
    toast.success('İnsan Onayı Verildi', 'HUMAN_APPROVAL_RESOLVED olayı tetiklendi ve kreatif yayına onaylandı.');
  };

  const handleReject = () => {
    toast.warning('Kreatif Reddedildi', 'Gerekçeli ret kararı işlendi ve yeniden üretim kuyruğu planlandı.');
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 select-none">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-emerald-950/60 border border-emerald-800/60 text-emerald-300 text-xs font-mono mb-2">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>M07 — 7-Layer Multi-Stage Quality & Originality Gates</span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Quality Center & Governance Gates</h1>
          <p className="text-slate-400 text-xs mt-1">
            End-to-end multi-layer evaluation pipeline. Unifies schema validation, Playwright browser testing, game truth compliance, and reasoned human oversight.
          </p>
        </div>
      </div>

      {/* Human Review Escalation Queue Banner */}
      <div className={cn(
        'p-6 rounded-2xl border transition-all duration-300 space-y-4',
        pendingReviewed
          ? 'bg-emerald-950/20 border-emerald-800/50'
          : 'bg-amber-950/25 border-amber-800/60 shadow-xl shadow-amber-500/10'
      )}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <UserCheck className="w-5 h-5 text-amber-400" />
            <h2 className="text-sm font-bold text-white uppercase font-mono tracking-wider">
              {pendingReviewed ? 'Human Review Resolved' : 'Human Review Gate: Pending Approval'}
            </h2>
          </div>
          <span className={cn(
            'text-[10px] font-mono px-2 py-0.5 rounded border',
            pendingReviewed
              ? 'bg-emerald-950 text-emerald-300 border-emerald-800/80 font-semibold'
              : 'bg-amber-950 text-amber-300 border-amber-800/80 animate-pulse font-semibold'
          )}>
            {pendingReviewed ? 'Approved by usr_creative_lead' : 'Pending Lead Action'}
          </span>
        </div>

        <p className="text-slate-300 text-xs leading-relaxed">
          SimilarityGate flagged a <span className="text-amber-300 font-mono">0.74 cosine overlap</span> with a competitor ad. Gate policy requires explicit creative director review before public release.
        </p>

        {/* Reviewer Note Input */}
        <div className="space-y-1.5 text-xs">
          <label className="text-slate-400 font-mono text-[11px]">Reasoned Decision Rationale:</label>
          <textarea
            value={reviewNote}
            onChange={(e) => setReviewNote(e.target.value)}
            disabled={pendingReviewed}
            rows={2}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-xs text-slate-200 focus:outline-none focus:border-amber-500 font-mono leading-relaxed disabled:opacity-75"
          />
        </div>

        {/* Action Buttons */}
        {!pendingReviewed ? (
          <div className="flex items-center gap-3 pt-2">
            <button
              onClick={handleApprove}
              className="px-4 py-2 rounded-lg bg-gradient-to-r from-emerald-500 to-teal-600 hover:shadow-emerald-500/25 text-white font-semibold text-xs flex items-center gap-1.5 transition-all shadow-md"
            >
              <ThumbsUp className="w-3.5 h-3.5" />
              <span>Approve & Release Creative</span>
            </button>
            <button
              onClick={handleReject}
              className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-rose-950 text-slate-300 hover:text-rose-300 border border-slate-700 text-xs font-semibold flex items-center gap-1.5 transition-colors"
            >
              <ThumbsDown className="w-3.5 h-3.5" />
              <span>Reject with Feedback</span>
            </button>
          </div>
        ) : (
          <div className="text-emerald-400 font-mono text-xs flex items-center gap-2 pt-1">
            <CheckCircle2 className="w-4 h-4" />
            <span>Approved and signed with immutable audit trail. Ready for ad campaign export.</span>
          </div>
        )}
      </div>

      {/* 7-Gate Pipeline Cards */}
      <div className="space-y-4">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-300 font-mono flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-cyan-400" />
          7-Stage Multi-Layer Gates Status
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {gates.map((g) => (
            <div key={g.id} className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2.5">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono text-slate-500 uppercase">Stage #{g.id}</span>
                <span className={cn(
                  'text-[10px] font-mono px-2 py-0.5 rounded border font-semibold',
                  g.status === 'PASSED' && 'bg-emerald-950 text-emerald-300 border-emerald-800/60',
                  g.status === 'WARNING' && 'bg-amber-950 text-amber-300 border-amber-800/60',
                  g.status === 'APPROVED' && 'bg-emerald-950 text-emerald-300 border-emerald-800/60',
                  g.status === 'PENDING ACTION' && 'bg-rose-950 text-rose-300 border-rose-800/60 animate-pulse'
                )}>
                  {g.status}
                </span>
              </div>

              <div>
                <h3 className="font-bold text-sm text-slate-200">{g.name}</h3>
                <div className="text-[11px] text-slate-400 font-mono">{g.category}</div>
              </div>

              <div className="p-2 rounded bg-slate-950 border border-slate-800/80 font-mono text-[11px] text-cyan-300 flex items-center justify-between">
                <span>Score:</span>
                <span className="font-semibold">{g.score}</span>
              </div>

              <p className="text-[11px] text-slate-400 leading-relaxed">{g.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
