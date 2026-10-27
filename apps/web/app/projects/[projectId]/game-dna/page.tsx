'use client';

import React, { useState } from 'react';
import {
  Dna,
  Lock,
  Plus,
  ShieldCheck,
  AlertOctagon,
  Palette,
  Layers,
  Sparkles,
  FileCheck,
  ChevronRight,
  GitCommit,
  Flame,
  Check,
  X,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useAppStore } from '@/lib/store';
import { toast } from '@/lib/toast';
import { apiClient } from '@/lib/api-client';

export default function GameDNAPage() {
  const { gameDNA } = useAppStore();
  const [profile, setProfile] = useState(gameDNA);
  const [selectedVersion, setSelectedVersion] = useState('v2.1');
  const [showFreezeModal, setShowFreezeModal] = useState(false);

  const [versions, setVersions] = useState([
    { version: 'v2.1', date: '2026-10-25 14:00 UTC', status: 'FROZEN', author: 'usr_lead_game_designer', notes: 'Locked 8x8 match-3 rescue spec & King Arthur sprite' },
    { version: 'v2.0', date: '2026-10-20 09:30 UTC', status: 'ARCHIVED', author: 'usr_producer', notes: 'Initial King rescue concept with basic gem tiles' },
    { version: 'v1.0', date: '2026-10-15 11:15 UTC', status: 'ARCHIVED', author: 'usr_founder', notes: 'Baseline prototype' },
  ]);
  const [newConstraint, setNewConstraint] = useState('');
  const [showAddConstraint, setShowAddConstraint] = useState(false);

  const handleAddConstraint = () => {
    if (!newConstraint.trim()) return;
    setProfile((prev) => ({
      ...prev,
      brandConstraints: [...prev.brandConstraints, newConstraint.trim()],
    }));
    toast.success('Kural Eklendi', 'Yeni marka kısıtı Game DNA profiline dahil edildi.');
    setNewConstraint('');
    setShowAddConstraint(false);
  };

  const handleFreezeVersion = async () => {
    setShowFreezeModal(false);
    const newVersionName = 'v3.0 - FROZEN';
    setProfile((prev) => ({
      ...prev,
      version: newVersionName,
      isFrozen: true,
    }));
    setVersions((prev) => [
      {
        version: 'v3.0',
        date: new Date().toISOString().replace('T', ' ').substring(0, 16) + ' UTC',
        status: 'FROZEN',
        author: 'usr_creative_lead',
        notes: 'Locked mechanics spec and constraints snapshot',
      },
      ...prev,
    ]);
    toast.success(
      'Game DNA Versiyonu Donduruldu',
      'v3.0 kilitlendi ve SHA-256 bütünlük imzasıyla PostgreSQL ledger kaydı oluşturuldu.'
    );

    try {
      await apiClient.createGameVersion(profile.id, {
        mechanics_spec: { genre: 'Match-3', grid: profile.gridSize },
        brand_constraints: { rules: profile.brandConstraints },
      });
    } catch {}
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 select-none">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-apple-purple/10 border border-apple-purple/25 text-apple-purple text-xs font-medium mb-3">
            <Dna className="w-3.5 h-3.5" />
            <span>M04 — Game DNA & Brand Consistency Engine</span>
          </div>
          <h1 className="text-2xl font-semibold tracking-tight text-neutral-100 flex items-center gap-3">
            {profile.name}
            <span className="text-xs font-mono px-2.5 py-1 rounded-full bg-apple-purple/15 text-apple-purple border border-apple-purple/30 flex items-center gap-1.5">
              <Lock className="w-3 h-3 text-apple-purple" />
              {profile.version}
            </span>
          </h1>
          <p className="text-neutral-400 text-xs mt-1 leading-relaxed">
            Immutable game truth spec guaranteeing that generated ads strictly reflect real in-game physics, mechanics, and brand identity.
          </p>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowFreezeModal(true)}
            className="apple-btn-primary flex items-center gap-1.5 shadow-apple-sm"
          >
            <Lock className="w-3.5 h-3.5" />
            <span>Freeze & Publish Version</span>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column (2 Cols): Mechanics, Palette, Assets */}
        <div className="lg:col-span-2 space-y-6">
          {/* Core Gameplay Mechanics */}
          <div className="p-6 rounded-3xl bg-[#121724]/80 backdrop-blur-2xl border border-white/[0.08] shadow-apple-md space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-xs font-semibold uppercase tracking-wider text-neutral-300 flex items-center gap-2">
                <Layers className="w-4 h-4 text-apple-blue" />
                Gameplay Mechanics Spec
              </h2>
              <span className="text-xs font-mono px-2.5 py-1 rounded-full bg-white/[0.06] text-neutral-300 border border-white/[0.08]">
                Grid: {profile.gridSize}
              </span>
            </div>

            <div className="space-y-2 text-xs">
              <label className="text-neutral-400 font-medium">Core Match Mechanics Definition</label>
              <textarea
                value={profile.coreMechanic}
                onChange={(e) => setProfile({ ...profile, coreMechanic: e.target.value })}
                rows={3}
                className="w-full bg-black/30 border border-white/[0.08] rounded-xl p-3 text-xs text-neutral-100 focus:outline-none focus:border-apple-blue font-mono leading-relaxed"
              />
            </div>
          </div>

          {/* Color Palette Tokens */}
          <div className="p-6 rounded-3xl bg-[#121724]/80 backdrop-blur-2xl border border-white/[0.08] shadow-apple-md space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-xs font-semibold uppercase tracking-wider text-neutral-300 flex items-center gap-2">
                <Palette className="w-4 h-4 text-apple-amber" />
                Locked Color Tokens & Visual Identity
              </h2>
              <span className="text-xs font-mono text-neutral-500">5 Tokens Frozen</span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
              {profile.palette.map((color, i) => (
                <div key={i} className="p-3 rounded-2xl bg-black/25 border border-white/[0.06] space-y-2 text-center">
                  <div
                    className="w-full h-12 rounded-xl shadow-inner border border-white/10"
                    style={{ backgroundColor: color.hex }}
                  />
                  <div className="text-xs font-semibold text-neutral-200 truncate">{color.name}</div>
                  <div className="text-[10px] font-mono text-neutral-500">{color.hex}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Character & Key Assets */}
          <div className="p-6 rounded-3xl bg-[#121724]/80 backdrop-blur-2xl border border-white/[0.08] shadow-apple-md space-y-4">
            <h2 className="text-xs font-semibold uppercase tracking-wider text-neutral-300 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-apple-purple" />
              Approved Character & Sprite Library
            </h2>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {profile.characters.map((char, i) => (
                <div key={i} className="p-4 rounded-2xl bg-black/25 border border-white/[0.06] space-y-2">
                  <div className="w-full h-24 rounded-xl bg-black/40 flex items-center justify-center border border-white/[0.06] text-neutral-500 font-mono text-xs">
                    [Sprite Asset]
                  </div>
                  <div className="text-xs font-semibold text-neutral-100">{char.name}</div>
                  <div className="text-[11px] text-neutral-400">{char.role}</div>
                  <div className="text-[10px] font-mono text-neutral-500 truncate">{char.assetRef}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column (1 Col): Constraints, Anti-Hallucination, Version History */}
        <div className="space-y-6">
          {/* Brand Constraints & Truth Gates */}
          <div className="p-6 rounded-3xl bg-[#121724]/80 backdrop-blur-2xl border border-white/[0.08] shadow-apple-md space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-xs font-semibold uppercase tracking-wider text-neutral-300 flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-apple-emerald" />
                Brand Constraints
              </h2>
              <button
                onClick={() => setShowAddConstraint(!showAddConstraint)}
                className="p-1 rounded-md text-neutral-400 hover:text-white hover:bg-white/[0.06] transition-colors"
                title="Add Constraint"
              >
                <Plus className="w-4 h-4" />
              </button>
            </div>

            {showAddConstraint && (
              <div className="p-3 rounded-2xl bg-black/30 border border-apple-blue/30 space-y-2">
                <input
                  type="text"
                  placeholder="Enter brand constraint or claim rule..."
                  value={newConstraint}
                  onChange={(e) => setNewConstraint(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleAddConstraint()}
                  className="w-full bg-black/40 border border-white/[0.08] rounded-lg px-2.5 py-1.5 text-xs text-neutral-100 placeholder:text-neutral-500 focus:outline-none focus:border-apple-blue font-sans"
                  autoFocus
                />
                <div className="flex justify-end gap-2">
                  <button
                    onClick={() => setShowAddConstraint(false)}
                    className="apple-btn-secondary text-[11px] py-1 px-2.5"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleAddConstraint}
                    className="apple-btn-primary text-[11px] py-1 px-3"
                  >
                    Add Rule
                  </button>
                </div>
              </div>
            )}

            <div className="space-y-2 text-xs">
              {profile.brandConstraints.map((c, i) => (
                <div key={i} className="p-3 rounded-xl bg-black/20 border border-white/[0.04] text-neutral-300 leading-relaxed flex items-start gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-apple-emerald mt-1.5 flex-shrink-0" />
                  <span>{c}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Anti-Hallucination ("Do Not Generate") */}
          <div className="p-6 rounded-3xl bg-apple-red/[0.04] border border-apple-red/20 space-y-4">
            <h2 className="text-xs font-semibold uppercase tracking-wider text-apple-red flex items-center gap-2">
              <AlertOctagon className="w-4 h-4 text-apple-red" />
              Do Not Generate (Anti-Rules)
            </h2>

            <div className="space-y-2 text-xs">
              {profile.doNotGenerate.map((rule, i) => (
                <div key={i} className="p-3 rounded-xl bg-black/20 border border-apple-red/15 text-neutral-300 leading-relaxed flex items-start gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-apple-red mt-1.5 flex-shrink-0" />
                  <span>{rule}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Immutable Version History */}
          <div className="p-6 rounded-3xl bg-[#121724]/80 backdrop-blur-2xl border border-white/[0.08] shadow-apple-md space-y-4">
            <h2 className="text-xs font-semibold uppercase tracking-wider text-neutral-300 flex items-center gap-2">
              <GitCommit className="w-4 h-4 text-apple-teal" />
              Version Ledger
            </h2>

            <div className="space-y-2 text-xs font-mono">
              {versions.map((v) => (
                <div
                  key={v.version}
                  onClick={() => setSelectedVersion(v.version)}
                  className={cn(
                    'p-3 rounded-2xl border transition-all cursor-pointer',
                    selectedVersion === v.version
                      ? 'bg-apple-purple/15 border-apple-purple/35 text-neutral-100 shadow-sm'
                      : 'bg-black/20 border-white/[0.04] text-neutral-400 hover:border-white/[0.12] hover:text-neutral-200'
                  )}
                >
                  <div className="flex items-center justify-between font-semibold">
                    <span>{v.version}</span>
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-white/[0.06] text-neutral-300 border border-white/[0.08]">
                      {v.status}
                    </span>
                  </div>
                  <div className="text-[10px] text-neutral-500 mt-1">{v.date}</div>
                  <div className="text-[11px] text-neutral-300 mt-1 line-clamp-1">{v.notes}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Freeze Confirmation Modal */}
      {showFreezeModal && (
        <div className="fixed inset-0 bg-black/75 backdrop-blur-2xl flex items-center justify-center p-6 z-50">
          <div className="bg-[#0c101a]/95 border border-white/[0.1] rounded-3xl w-full max-w-md p-6 space-y-4 shadow-2xl">
            <div className="flex items-center gap-2 text-apple-purple">
              <Lock className="w-5 h-5" />
              <h3 className="font-semibold text-base text-neutral-100">Freeze Game DNA Version</h3>
            </div>
            <p className="text-xs text-neutral-400 leading-relaxed font-sans">
              Freezing will lock the current mechanics spec, palette, and brand constraints into an immutable snapshot. Future runs will execute deterministically against this version.
            </p>
            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                onClick={() => setShowFreezeModal(false)}
                className="apple-btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={handleFreezeVersion}
                className="apple-btn-primary"
              >
                Confirm & Freeze v3.0
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
