'use client';

import React, { useState } from 'react';
import {
  Library,
  Video,
  Image as ImageIcon,
  Gamepad2,
  FileCode,
  Download,
  ExternalLink,
  ShieldCheck,
  Play,
  RotateCcw,
  CheckCircle2,
  X,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useAppStore } from '@/lib/store';
import { toast } from '@/lib/toast';

export default function ArtifactLibraryPage() {
  const { projectId } = useAppStore();
  const [filterType, setFilterType] = useState('all');
  const [activePlayableModal, setActivePlayableModal] = useState(false);

  const artifacts = [
    {
      id: 'art_video_rescue_final',
      name: 'Rising Lava King Rescue - 15s Ad',
      type: 'video',
      format: 'MP4 (1080x1920, 30fps, h264)',
      size: '8.4 MB',
      sha256: '9f83c12a78129b0a876412e098418290abfde283948192837491029384758192',
      parents: ['artifact_a', 'artifact_b'],
      qaStatus: 'Passed with Advisory',
      previewUrl: 'https://images.unsplash.com/photo-1579783902614-a3fb3927b675?auto=format&fit=crop&w=600&q=80',
    },
    {
      id: 'art_playable_match3_bundle_v1.zip',
      name: 'HTML5 Match-3 Mini-Game Playable',
      type: 'playable',
      format: 'ZIP / Standalone HTML Bundle',
      size: '1.2 MB',
      sha256: 'c3d4e5f6a1b27890123456789abcdef0123456789abcdef0123456789abcdef0',
      parents: ['dna_royal_rescue_v2'],
      qaStatus: 'Passed (0 JS Errors)',
      previewUrl: 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=600&q=80',
    },
    {
      id: 'artifact_a',
      name: 'Rescue Hook Keyframe Visual',
      type: 'image',
      format: 'PNG (1080x1920 High-Res)',
      size: '3.6 MB',
      sha256: 'a1b2c3d4e5f67890123456789abcdef0123456789abcdef0123456789abcdef0',
      parents: ['concept_01'],
      qaStatus: 'Passed Visual QA',
      previewUrl: 'https://images.unsplash.com/photo-1579783902614-a3fb3927b675?auto=format&fit=crop&w=600&q=80',
    },
    {
      id: 'art_evaluation_report_run88.json',
      name: '7-Gate Multi-Layer Evaluation Report',
      type: 'manifest',
      format: 'JSON / Pydantic v2',
      size: '42 KB',
      sha256: '8f7d9a10bc938e71928d9a019284729102938471920384719203847192038471',
      parents: ['run_88'],
      qaStatus: 'Passed (Approved)',
      previewUrl: '',
    },
  ];

  const filtered = artifacts.filter((a) =>
    filterType === 'all' ? true : a.type === filterType
  );

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 select-none">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-cyan-950/60 border border-cyan-800/60 text-cyan-300 text-xs font-mono mb-2">
            <Library className="w-3.5 h-3.5" />
            <span>Typed Artifacts & Cryptographic Lineage</span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Artifact Library & Previews</h1>
          <p className="text-slate-400 text-xs mt-1">
            Production-ready creatives with immutable parent-child lineage, cryptographic checksums, and Playwright verification.
          </p>
        </div>

        {/* Filter buttons */}
        <div className="flex items-center gap-1.5 bg-slate-900 border border-slate-800 p-1 rounded-lg text-xs font-mono">
          {['all', 'video', 'playable', 'image', 'manifest'].map((t) => (
            <button
              key={t}
              onClick={() => setFilterType(t)}
              className={cn(
                'px-3 py-1 rounded-md capitalize transition-colors',
                filterType === t ? 'bg-cyan-500/20 text-cyan-300 font-semibold' : 'text-slate-400 hover:text-slate-200'
              )}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      {/* Artifacts Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filtered.map((art) => (
          <div key={art.id} className="rounded-2xl border border-slate-800 bg-slate-900/60 overflow-hidden flex flex-col justify-between">
            <div>
              {/* Media Preview Box */}
              <div className="h-44 w-full bg-slate-950 relative overflow-hidden flex items-center justify-center">
                {art.type === 'video' && (
                  <div className="relative w-full h-full group">
                    <img src={art.previewUrl} alt={art.name} className="w-full h-full object-cover opacity-80" />
                    <div className="absolute inset-0 bg-black/40 flex items-center justify-center">
                      <div className="w-12 h-12 rounded-full bg-amber-500 text-slate-950 flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
                        <Play className="w-6 h-6 fill-current ml-0.5" />
                      </div>
                    </div>
                    <span className="absolute bottom-2 right-2 px-2 py-0.5 rounded bg-black/80 font-mono text-[10px] text-white">
                      0:15 / 9:16
                    </span>
                  </div>
                )}

                {art.type === 'playable' && (
                  <div className="relative w-full h-full group">
                    <img src={art.previewUrl} alt={art.name} className="w-full h-full object-cover opacity-75" />
                    <div className="absolute inset-0 bg-black/50 flex flex-col items-center justify-center gap-2">
                      <button
                        onClick={() => setActivePlayableModal(true)}
                        className="px-4 py-2 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs flex items-center gap-1.5 shadow-lg group-hover:scale-105 transition-transform"
                      >
                        <Gamepad2 className="w-4 h-4" />
                        Play Interactive Demo
                      </button>
                      <span className="text-[10px] font-mono text-emerald-300">Phaser 3 • 60 FPS Target</span>
                    </div>
                  </div>
                )}

                {art.type === 'image' && (
                  <img src={art.previewUrl} alt={art.name} className="w-full h-full object-cover" />
                )}

                {art.type === 'manifest' && (
                  <div className="flex flex-col items-center justify-center text-slate-500 gap-2 p-6 text-center">
                    <FileCode className="w-10 h-10 text-cyan-400" />
                    <span className="text-xs font-mono text-slate-300">Run Manifest & Evaluation JSON</span>
                  </div>
                )}
              </div>

              {/* Card Meta */}
              <div className="p-4 space-y-3 text-xs">
                <div>
                  <h3 className="font-bold text-slate-100">{art.name}</h3>
                  <div className="text-[11px] font-mono text-slate-400 mt-0.5">{art.format}</div>
                </div>

                <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800/80 font-mono text-[10px] space-y-1">
                  <div className="flex items-center justify-between text-slate-400">
                    <span>Artifact ID:</span>
                    <span className="text-slate-300 truncate max-w-[150px]">{art.id}</span>
                  </div>
                  <div className="flex items-center justify-between text-slate-400">
                    <span>File Size:</span>
                    <span className="text-slate-200">{art.size}</span>
                  </div>
                  <div className="flex items-center justify-between text-slate-400">
                    <span>QA Status:</span>
                    <span className="text-emerald-400 font-semibold">{art.qaStatus}</span>
                  </div>
                  <div className="text-slate-500 truncate pt-1">
                    SHA256: {art.sha256}
                  </div>
                </div>

                {art.parents.length > 0 && (
                  <div className="text-[10px] font-mono text-slate-500">
                    Lineage Parents: <span className="text-cyan-400">{art.parents.join(', ')}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Actions */}
            <div className="p-3 border-t border-slate-800 bg-slate-950/60 flex items-center justify-between">
              <button
                onClick={() => {
                  toast.success('Paket İndiriliyor', `"${art.name}" (${art.format}) yerel diske aktarılıyor...`);
                  // Trigger browser download via Blob
                  const content = JSON.stringify(art, null, 2);
                  const blob = new Blob([content], { type: 'application/json' });
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = `${art.id}.json`;
                  a.click();
                  URL.revokeObjectURL(url);
                }}
                className="w-full py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 font-mono text-xs flex items-center justify-center gap-1.5 transition-colors"
              >
                <Download className="w-3.5 h-3.5" />
                Download Package
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Interactive Playable Sandbox Modal */}
      {activePlayableModal && (
        <div className="fixed inset-0 bg-black/85 backdrop-blur-md flex items-center justify-center p-4 z-50 animate-in fade-in">
          <div className="bg-slate-900 border border-emerald-500/40 rounded-3xl w-full max-w-md flex flex-col overflow-hidden shadow-2xl">
            <div className="p-3.5 border-b border-slate-800 flex items-center justify-between bg-slate-950/80">
              <div className="flex items-center gap-2">
                <Gamepad2 className="w-4 h-4 text-emerald-400" />
                <span className="font-bold text-xs text-white">HTML5 Responsive Playable Mini-Game</span>
                <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-emerald-950 text-emerald-300 border border-emerald-800/60">
                  Phaser 3 / 60 FPS
                </span>
              </div>
              <button
                onClick={() => setActivePlayableModal(false)}
                className="p-1 rounded text-slate-400 hover:text-slate-200 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Embedded Live HTML5 Match-3 Game */}
            <div className="h-[620px] w-full bg-black relative flex flex-col items-center justify-center">
              <iframe
                src="/playable/index.html"
                title="Playable Match-3 Demo"
                className="w-full h-full border-0 select-none"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
