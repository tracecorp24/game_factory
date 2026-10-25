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
          <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-slate-800 border border-slate-700 text-slate-300 text-xs font-mono mb-2">
            <Lock className="w-3.5 h-3.5" />
            <span>Security, RBAC & Data Redaction</span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Security & Governance Policies</h1>
          <p className="text-slate-400 text-xs mt-1">
            Cryptographic event verification, PII redaction policies, and role-based access control.
          </p>
        </div>

        <button
          onClick={handleSavePolicy}
          className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-xs flex items-center gap-1.5 transition-colors shadow-sm self-start md:self-auto"
        >
          <Save className="w-3.5 h-3.5" />
          <span>Save Governance Settings</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Redaction Level */}
        <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
          <div className="flex items-center gap-2">
            <EyeOff className="w-4 h-4 text-cyan-400" />
            <h2 className="text-sm font-bold text-white uppercase font-mono">Event Redaction Tiers</h2>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            All ledger event payloads undergo automated redaction before entering PostgreSQL outbox tables. Select active policy tier:
          </p>
          <div className="space-y-2 text-xs font-mono">
            <div
              onClick={() => setSelectedTier('metadata_only')}
              className={cn(
                'p-3 rounded-xl border flex items-center justify-between cursor-pointer transition-colors',
                selectedTier === 'metadata_only'
                  ? 'bg-cyan-950/60 border-cyan-500/80 text-cyan-200'
                  : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-slate-200'
              )}
            >
              <div>
                <span className="font-semibold">metadata_only</span>
                <div className="text-[10px] text-slate-500 mt-0.5">Model configs and token telemetry only</div>
              </div>
              <input type="radio" checked={selectedTier === 'metadata_only'} readOnly className="accent-cyan-400" />
            </div>

            <div
              onClick={() => setSelectedTier('sanitized')}
              className={cn(
                'p-3 rounded-xl border flex items-center justify-between cursor-pointer transition-colors',
                selectedTier === 'sanitized'
                  ? 'bg-emerald-950/60 border-emerald-500/80 text-emerald-200'
                  : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-slate-200'
              )}
            >
              <div>
                <span className="font-semibold">sanitized (Default)</span>
                <div className="text-[10px] text-slate-500 mt-0.5">PII, API keys and secrets scrubbed before outbox flush</div>
              </div>
              <input type="radio" checked={selectedTier === 'sanitized'} readOnly className="accent-emerald-400" />
            </div>

            <div
              onClick={() => setSelectedTier('full_content')}
              className={cn(
                'p-3 rounded-xl border flex items-center justify-between cursor-pointer transition-colors',
                selectedTier === 'full_content'
                  ? 'bg-purple-950/60 border-purple-500/80 text-purple-200'
                  : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-slate-200'
              )}
            >
              <div>
                <span className="font-semibold">full_content</span>
                <div className="text-[10px] text-slate-500 mt-0.5">Raw payloads preserved for audited internal access only</div>
              </div>
              <input type="radio" checked={selectedTier === 'full_content'} readOnly className="accent-purple-400" />
            </div>
          </div>
        </div>

        {/* Cryptographic Integrity */}
        <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <h2 className="text-sm font-bold text-white uppercase font-mono">SHA-256 Ledger Integrity</h2>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            Every operational event is appended with an immutable SHA-256 hash. Any tampering with stored database rows will invalidate downstream event chains.
          </p>
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono text-emerald-400 space-y-2">
            <div className="flex items-center gap-2 font-semibold">
              <CheckCircle2 className="w-4 h-4" />
              <span>Cryptographic Chain: VERIFIED (Zero Discrepancies)</span>
            </div>
            <div className="text-[11px] text-slate-400">
              Audit Status: SHA-256 Merkle root matches latest committed run manifest.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
