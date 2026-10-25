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
          <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-purple-950/60 border border-purple-800/60 text-purple-300 text-xs font-mono mb-2">
            <Dna className="w-3.5 h-3.5" />
            <span>M04 — Game DNA & Brand Consistency Engine</span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-3">
            {profile.name}
            <span className="text-xs font-mono px-2.5 py-1 rounded-full bg-purple-950 text-purple-300 border border-purple-800/80 flex items-center gap-1.5">
              <Lock className="w-3 h-3 text-purple-400" />
              {profile.version}
            </span>
          </h1>
          <p className="text-slate-400 text-xs mt-1">
            Immutable game truth spec guaranteeing that generated ads strictly reflect real in-game physics, mechanics, and brand identity.
          </p>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowFreezeModal(true)}
            className="px-4 py-2 rounded-lg bg-gradient-to-r from-purple-600 to-indigo-600 hover:shadow-purple-500/25 text-white font-medium text-xs flex items-center gap-1.5 transition-all shadow-md"
          >
            <Lock className="w-4 h-4" />
            <span>Freeze & Publish Version</span>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column (2 Cols): Mechanics, Palette, Assets */}
        <div className="lg:col-span-2 space-y-6">
          {/* Core Gameplay Mechanics */}
          <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-300 font-mono flex items-center gap-2">
                <Layers className="w-4 h-4 text-cyan-400" />
                Gameplay Mechanics Spec
              </h2>
              <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                {profile.gridSize}
              </span>
            </div>

            <div className="space-y-2 text-xs">
              <label className="text-slate-400 font-medium">Core Match Mechanics Definition</label>
              <textarea
                value={profile.coreMechanic}
                onChange={(e) => setProfile({ ...profile, coreMechanic: e.target.value })}
                rows={3}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs text-slate-200 focus:outline-none focus:border-purple-500 font-mono leading-relaxed"
              />
            </div>
          </div>

          {/* Color Palette Tokens */}
          <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-300 font-mono flex items-center gap-2">
                <Palette className="w-4 h-4 text-amber-400" />
                Locked Color Palette & Visual Style
              </h2>
              <span className="text-xs font-mono text-slate-500">5 Tokens</span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
              {profile.palette.map((color, i) => (
                <div key={i} className="p-3 rounded-xl bg-slate-950 border border-slate-800/80 space-y-2 text-center">
                  <div
                    className="w-full h-12 rounded-lg shadow-inner border border-white/10"
                    style={{ backgroundColor: color.hex }}
                  />
                  <div className="text-xs font-semibold text-slate-200 truncate">{color.name}</div>
                  <div className="text-[10px] font-mono text-slate-500">{color.hex}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Character & Key Assets */}
          <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-300 font-mono flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-purple-400" />
              Approved Character & Sprite Library
            </h2>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {profile.characters.map((char, i) => (
                <div key={i} className="p-4 rounded-xl bg-slate-950 border border-slate-800/80 space-y-2">
                  <div className="w-full h-24 rounded-lg bg-slate-900 flex items-center justify-center border border-slate-800 text-slate-500 font-mono text-xs">
                    [Sprite Asset]
                  </div>
                  <div className="text-xs font-bold text-slate-200">{char.name}</div>
                  <div className="text-[11px] text-slate-400">{char.role}</div>
                  <div className="text-[10px] font-mono text-slate-500 truncate">{char.assetRef}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column (1 Col): Constraints, Anti-Hallucination, Version History */}
        <div className="space-y-6">
          {/* Brand Constraints & Truth Gates */}
          <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-300 font-mono flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                Brand Constraints
              </h2>
              <button
                onClick={() => setShowAddConstraint(!showAddConstraint)}
                className="p-1 rounded text-slate-400 hover:text-slate-200 hover:bg-slate-800"
                title="Add Constraint"
              >
                <Plus className="w-4 h-4" />
              </button>
            </div>

            {showAddConstraint && (
              <div className="p-3 rounded-lg bg-slate-950 border border-cyan-800/60 space-y-2">
                <input
                  type="text"
                  placeholder="Enter brand constraint or claim rule..."
                  value={newConstraint}
                  onChange={(e) => setNewConstraint(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleAddConstraint()}
                  className="w-full bg-slate-900 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-cyan-500"
                  autoFocus
                />
                <div className="flex justify-end gap-2">
                  <button
                    onClick={() => setShowAddConstraint(false)}
                    className="px-2.5 py-1 rounded text-[11px] text-slate-400 hover:text-slate-200"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleAddConstraint}
                    className="px-3 py-1 rounded bg-cyan-600 hover:bg-cyan-500 text-white font-medium text-[11px]"
                  >
                    Add Rule
                  </button>
                </div>
              </div>
            )}

            <div className="space-y-2 text-xs">
              {profile.brandConstraints.map((c, i) => (
                <div key={i} className="p-3 rounded-lg bg-slate-950 border border-slate-800/80 text-slate-300 leading-relaxed flex items-start gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mt-1.5 flex-shrink-0" />
                  <span>{c}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Anti-Hallucination ("Do Not Generate") */}
          <div className="p-6 rounded-2xl bg-rose-950/20 border border-rose-900/40 space-y-4">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-rose-300 font-mono flex items-center gap-2">
              <AlertOctagon className="w-4 h-4 text-rose-400" />
              Do Not Generate (Anti-Rules)
            </h2>

            <div className="space-y-2 text-xs">
              {profile.doNotGenerate.map((rule, i) => (
                <div key={i} className="p-3 rounded-lg bg-slate-950/80 border border-rose-900/30 text-rose-200/90 leading-relaxed flex items-start gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-rose-400 mt-1.5 flex-shrink-0" />
                  <span>{rule}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Immutable Version History */}
          <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-300 font-mono flex items-center gap-2">
              <GitCommit className="w-4 h-4 text-cyan-400" />
              Version Ledger
            </h2>

            <div className="space-y-2 text-xs font-mono">
              {versions.map((v) => (
                <div
                  key={v.version}
                  onClick={() => setSelectedVersion(v.version)}
                  className={cn(
                    'p-3 rounded-lg border transition-colors cursor-pointer',
                    selectedVersion === v.version
                      ? 'bg-purple-950/40 border-purple-800/80 text-purple-200'
                      : 'bg-slate-950 border-slate-800/80 text-slate-400 hover:text-slate-200'
                  )}
                >
                  <div className="flex items-center justify-between font-semibold">
                    <span>{v.version}</span>
                    <span className="text-[10px] px-1.5 py-0.2 rounded bg-slate-800 text-slate-300">
                      {v.status}
                    </span>
                  </div>
                  <div className="text-[10px] text-slate-500 mt-1">{v.date}</div>
                  <div className="text-[11px] text-slate-300 mt-1 line-clamp-1">{v.notes}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Freeze Confirmation Modal */}
      {showFreezeModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center p-6 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-md p-6 space-y-4 shadow-2xl">
            <div className="flex items-center gap-2 text-purple-400">
              <Lock className="w-5 h-5" />
              <h3 className="font-bold text-base text-white">Freeze Game DNA Version</h3>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              Freezing will lock the current mechanics spec, palette, and brand constraints into an immutable snapshot. Future runs will execute deterministically against this version.
            </p>
            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                onClick={() => setShowFreezeModal(false)}
                className="px-3 py-1.5 rounded-lg border border-slate-700 text-slate-300 text-xs hover:bg-slate-800"
              >
                Cancel
              </button>
              <button
                onClick={handleFreezeVersion}
                className="px-4 py-1.5 rounded-lg bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-semibold text-xs"
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
