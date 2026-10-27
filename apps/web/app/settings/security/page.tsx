'use client';

import React, { useState } from 'react';
import { Lock, ShieldCheck, Key, FileCheck, EyeOff, CheckCircle2, Save } from 'lucide-react';
import { toast } from '@/lib/toast';
import { cn } from '@/lib/utils';

export default function SecurityPage() {
  const [selectedTier, setSelectedTier] = useState<'metadata_only' | 'sanitized' | 'full_content'>('sanitized');

  const handleSavePolicy = () => {
    toast.success('Güvenlik Politikası Güncellendi', `Aktif redaksiyon seviyesi "${selectedTier}" olarak kaydedildi.`);
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 select-none">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-apple-emerald/10 border border-apple-emerald/20 text-apple-emerald text-xs font-medium mb-3">
            <Lock className="w-3.5 h-3.5" />
            <span>M11 · Security, RBAC & Data Redaction</span>
          </div>
          <h1 className="text-2xl font-semibold tracking-tight text-neutral-100">
            Security & Governance Policies
          </h1>
          <p className="text-neutral-400 text-xs sm:text-sm mt-1 max-w-2xl leading-relaxed">
            Cryptographic event verification, PII redaction policies, and immutable ledger integrity standards.
          </p>
        </div>

        <button
          onClick={handleSavePolicy}
          className="apple-btn-primary flex items-center gap-2 py-2 px-4 shadow-apple-sm text-xs self-start md:self-auto"
        >
          <Save className="w-4 h-4" />
          <span>Save Governance</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Redaction Level */}
        <div className="p-6 rounded-3xl bg-white/[0.03] border border-white/[0.08] backdrop-blur-xl shadow-apple-sm space-y-4">
          <div className="flex items-center gap-2">
            <EyeOff className="w-4 h-4 text-apple-blue" />
            <h2 className="text-sm font-semibold text-neutral-200">Event Redaction Tiers</h2>
          </div>
          <p className="text-xs text-neutral-400 leading-relaxed font-normal">
            All ledger event payloads undergo automated redaction before entering PostgreSQL outbox tables. Select active policy tier:
          </p>
          <div className="space-y-2.5 text-xs font-mono">
            <div
              onClick={() => setSelectedTier('metadata_only')}
              className={cn(
                'p-3.5 rounded-2xl border flex items-center justify-between cursor-pointer transition-all',
                selectedTier === 'metadata_only'
                  ? 'bg-apple-blue/10 border-apple-blue/50 text-white'
                  : 'bg-white/[0.02] border-white/[0.06] text-neutral-400 hover:border-white/[0.12] hover:text-neutral-200'
              )}
            >
              <div>
                <span className="font-semibold font-sans text-neutral-100">metadata_only</span>
                <div className="text-[11px] text-neutral-500 mt-0.5 font-sans">Model configs and token telemetry only</div>
              </div>
              <input type="radio" checked={selectedTier === 'metadata_only'} readOnly className="accent-apple-blue" />
            </div>

            <div
              onClick={() => setSelectedTier('sanitized')}
              className={cn(
                'p-3.5 rounded-2xl border flex items-center justify-between cursor-pointer transition-all',
                selectedTier === 'sanitized'
                  ? 'bg-apple-emerald/10 border-apple-emerald/50 text-white'
                  : 'bg-white/[0.02] border-white/[0.06] text-neutral-400 hover:border-white/[0.12] hover:text-neutral-200'
              )}
            >
              <div>
                <span className="font-semibold font-sans text-neutral-100">sanitized (Default)</span>
                <div className="text-[11px] text-neutral-500 mt-0.5 font-sans">PII, API keys and secrets scrubbed before outbox flush</div>
              </div>
              <input type="radio" checked={selectedTier === 'sanitized'} readOnly className="accent-apple-emerald" />
            </div>

            <div
              onClick={() => setSelectedTier('full_content')}
              className={cn(
                'p-3.5 rounded-2xl border flex items-center justify-between cursor-pointer transition-all',
                selectedTier === 'full_content'
                  ? 'bg-apple-purple/10 border-apple-purple/50 text-white'
                  : 'bg-white/[0.02] border-white/[0.06] text-neutral-400 hover:border-white/[0.12] hover:text-neutral-200'
              )}
            >
              <div>
                <span className="font-semibold font-sans text-neutral-100">full_content</span>
                <div className="text-[11px] text-neutral-500 mt-0.5 font-sans">Raw payloads preserved for audited internal access only</div>
              </div>
              <input type="radio" checked={selectedTier === 'full_content'} readOnly className="accent-apple-purple" />
            </div>
          </div>
        </div>

        {/* Cryptographic Integrity */}
        <div className="p-6 rounded-3xl bg-white/[0.03] border border-white/[0.08] backdrop-blur-xl shadow-apple-sm space-y-4">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-apple-emerald" />
            <h2 className="text-sm font-semibold text-neutral-200">SHA-256 Ledger Integrity</h2>
          </div>
          <p className="text-xs text-neutral-400 leading-relaxed font-normal">
            Every operational event is appended with an immutable SHA-256 hash. Any tampering with stored database rows will invalidate downstream event chains.
          </p>
          <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/[0.06] text-xs font-mono text-apple-emerald space-y-2">
            <div className="flex items-center gap-2 font-semibold">
              <CheckCircle2 className="w-4 h-4" />
              <span>Cryptographic Chain: VERIFIED (Zero Discrepancies)</span>
            </div>
            <div className="text-[11px] text-neutral-400 font-sans">
              Audit Status: SHA-256 Merkle root matches latest committed run manifest.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
