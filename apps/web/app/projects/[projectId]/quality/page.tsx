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
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-apple-emerald/10 border border-apple-emerald/25 text-apple-emerald text-xs font-medium mb-3">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>M07 — 7-Layer Multi-Stage Quality & Originality Gates</span>
          </div>
          <h1 className="text-2xl font-semibold tracking-tight text-neutral-100">Quality Center & Governance Gates</h1>
          <p className="text-neutral-400 text-xs mt-1 leading-relaxed">
            End-to-end multi-layer evaluation pipeline. Unifies schema validation, Playwright browser testing, game truth compliance, and reasoned human oversight.
          </p>
        </div>
      </div>

      {/* Human Review Escalation Queue Banner */}
      <div className={cn(
        'p-6 rounded-3xl border transition-all duration-300 space-y-4 backdrop-blur-2xl shadow-apple-md',
        pendingReviewed
          ? 'bg-apple-emerald/5 border-apple-emerald/25'
          : 'bg-apple-amber/5 border-apple-amber/30'
      )}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <UserCheck className="w-5 h-5 text-apple-amber" />
            <h2 className="text-sm font-semibold text-neutral-100 tracking-tight">
              {pendingReviewed ? 'Human Review Resolved' : 'Human Review Gate: Pending Approval'}
            </h2>
          </div>
          <span className={cn(
            'text-[10px] font-mono px-2.5 py-0.5 rounded-full border',
            pendingReviewed
              ? 'bg-apple-emerald/15 text-apple-emerald border-apple-emerald/25 font-semibold'
              : 'bg-apple-amber/15 text-apple-amber border-apple-amber/30 animate-pulse font-semibold'
          )}>
            {pendingReviewed ? 'Approved by usr_creative_lead' : 'Pending Lead Action'}
          </span>
        </div>

        <p className="text-neutral-300 text-xs leading-relaxed font-sans">
          SimilarityGate flagged a <span className="text-apple-amber font-mono font-semibold">0.74 cosine overlap</span> with a competitor ad. Gate policy requires explicit creative director review before public release.
        </p>

        {/* Reviewer Note Input */}
        <div className="space-y-1.5 text-xs">
          <label className="text-neutral-400 font-sans text-[11px] font-medium">Reasoned Decision Rationale:</label>
          <textarea
            value={reviewNote}
            onChange={(e) => setReviewNote(e.target.value)}
            disabled={pendingReviewed}
            rows={2}
            className="w-full bg-black/30 border border-white/[0.08] rounded-xl p-3 text-xs text-neutral-100 focus:outline-none focus:border-apple-blue font-mono leading-relaxed disabled:opacity-60"
          />
        </div>

        {/* Action Buttons */}
        {!pendingReviewed ? (
          <div className="flex items-center gap-3 pt-1">
            <button
              onClick={handleApprove}
              className="apple-btn-primary flex items-center gap-1.5 shadow-apple-sm"
            >
              <ThumbsUp className="w-3.5 h-3.5" />
              <span>Approve & Release Creative</span>
            </button>
            <button
              onClick={handleReject}
              className="apple-btn-secondary flex items-center gap-1.5 hover:text-apple-red hover:border-apple-red/30"
            >
              <ThumbsDown className="w-3.5 h-3.5" />
              <span>Reject with Feedback</span>
            </button>
          </div>
        ) : (
          <div className="text-apple-emerald font-mono text-xs flex items-center gap-2 pt-1">
            <CheckCircle2 className="w-4 h-4" />
            <span>Approved and signed with immutable audit trail. Ready for ad campaign export.</span>
          </div>
        )}
      </div>

      {/* 7-Gate Pipeline Cards */}
      <div className="space-y-4">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-neutral-400 flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-apple-teal" />
          7-Stage Multi-Layer Gates Status
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {gates.map((g) => (
            <div key={g.id} className="p-4 rounded-3xl bg-white/[0.03] border border-white/[0.06] hover:border-white/[0.12] transition-colors space-y-2.5 shadow-apple-sm">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono text-neutral-500 uppercase">Stage #{g.id}</span>
                <span className={cn(
                  'text-[10px] font-mono px-2 py-0.5 rounded-full border font-semibold',
                  g.status === 'PASSED' && 'bg-apple-emerald/15 text-apple-emerald border-apple-emerald/25',
                  g.status === 'WARNING' && 'bg-apple-amber/15 text-apple-amber border-apple-amber/25',
                  g.status === 'APPROVED' && 'bg-apple-emerald/15 text-apple-emerald border-apple-emerald/25',
                  g.status === 'PENDING ACTION' && 'bg-apple-red/15 text-apple-red border-apple-red/25 animate-pulse'
                )}>
                  {g.status}
                </span>
              </div>

              <div>
                <h3 className="font-semibold text-sm text-neutral-100">{g.name}</h3>
                <div className="text-[11px] text-neutral-400 font-sans">{g.category}</div>
              </div>

              <div className="p-2 rounded-xl bg-black/20 border border-white/[0.04] font-mono text-[11px] text-apple-teal flex items-center justify-between">
                <span className="text-neutral-500">Score:</span>
                <span className="font-semibold">{g.score}</span>
              </div>

              <p className="text-[11px] text-neutral-400 leading-relaxed font-sans">{g.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
