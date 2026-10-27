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
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-apple-blue/10 border border-apple-blue/25 text-apple-teal text-xs font-medium mb-3">
            <Library className="w-3.5 h-3.5" />
            <span>Typed Artifacts & Cryptographic Lineage</span>
          </div>
          <h1 className="text-2xl font-semibold tracking-tight text-neutral-100">Artifact Library & Previews</h1>
          <p className="text-neutral-400 text-xs mt-1 leading-relaxed">
            Production-ready creatives with immutable parent-child lineage, cryptographic checksums, and Playwright verification.
          </p>
        </div>

        {/* Filter buttons */}
        <div className="apple-segmented">
          {['all', 'video', 'playable', 'image', 'manifest'].map((t) => (
            <button
              key={t}
              onClick={() => setFilterType(t)}
              className={cn(
                'apple-segmented-item capitalize',
                filterType === t && 'apple-segmented-item-active'
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
          <div key={art.id} className="rounded-3xl border border-white/[0.08] bg-[#121724]/80 backdrop-blur-2xl overflow-hidden flex flex-col justify-between shadow-apple-md">
            <div>
              {/* Media Preview Box */}
              <div className="h-44 w-full bg-black/40 relative overflow-hidden flex items-center justify-center">
                {art.type === 'video' && (
                  <div className="relative w-full h-full group">
                    <img src={art.previewUrl} alt={art.name} className="w-full h-full object-cover opacity-80" />
                    <div className="absolute inset-0 bg-black/40 flex items-center justify-center">
                      <div className="w-12 h-12 rounded-full bg-apple-amber text-neutral-950 flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
                        <Play className="w-5 h-5 fill-current ml-0.5" />
                      </div>
                    </div>
                    <span className="absolute bottom-2 right-2 px-2 py-0.5 rounded-full bg-black/70 font-mono text-[10px] text-white backdrop-blur-md">
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
                        className="apple-btn-primary flex items-center gap-1.5 shadow-apple-sm"
                      >
                        <Gamepad2 className="w-4 h-4" />
                        Play Interactive Demo
                      </button>
                      <span className="text-[10px] font-mono text-apple-emerald font-semibold">Phaser 3 • 60 FPS Target</span>
                    </div>
                  </div>
                )}

                {art.type === 'image' && (
                  <img src={art.previewUrl} alt={art.name} className="w-full h-full object-cover" />
                )}

                {art.type === 'manifest' && (
                  <div className="flex flex-col items-center justify-center text-neutral-500 gap-2 p-6 text-center">
                    <FileCode className="w-10 h-10 text-apple-teal" />
                    <span className="text-xs font-mono text-neutral-300">Run Manifest & Evaluation JSON</span>
                  </div>
                )}
              </div>

              {/* Card Meta */}
              <div className="p-4 space-y-3 text-xs">
                <div>
                  <h3 className="font-semibold text-neutral-100">{art.name}</h3>
                  <div className="text-[11px] font-mono text-neutral-400 mt-0.5">{art.format}</div>
                </div>

                <div className="p-2.5 rounded-2xl bg-black/20 border border-white/[0.04] font-mono text-[10px] space-y-1">
                  <div className="flex items-center justify-between text-neutral-400">
                    <span>Artifact ID:</span>
                    <span className="text-neutral-300 truncate max-w-[150px]">{art.id}</span>
                  </div>
                  <div className="flex items-center justify-between text-neutral-400">
                    <span>File Size:</span>
                    <span className="text-neutral-200">{art.size}</span>
                  </div>
                  <div className="flex items-center justify-between text-neutral-400">
                    <span>QA Status:</span>
                    <span className="text-apple-emerald font-semibold">{art.qaStatus}</span>
                  </div>
                  <div className="text-neutral-500 truncate pt-1">
                    SHA256: {art.sha256}
                  </div>
                </div>

                {art.parents.length > 0 && (
                  <div className="text-[10px] font-mono text-neutral-500">
                    Lineage Parents: <span className="text-apple-teal">{art.parents.join(', ')}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Actions */}
            <div className="p-3 border-t border-white/[0.06] bg-black/20 flex items-center justify-between">
              <button
                onClick={() => {
                  toast.success('Paket İndiriliyor', `"${art.name}" (${art.format}) yerel diske aktarılıyor...`);
                  const content = JSON.stringify(art, null, 2);
                  const blob = new Blob([content], { type: 'application/json' });
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = `${art.id}.json`;
                  a.click();
                  URL.revokeObjectURL(url);
                }}
                className="apple-btn-secondary w-full flex items-center justify-center gap-1.5 py-1.5"
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
        <div className="fixed inset-0 bg-black/80 backdrop-blur-2xl flex items-center justify-center p-4 z-50 animate-in fade-in">
          <div className="bg-[#0c101a]/95 border border-white/[0.1] rounded-3xl w-full max-w-md flex flex-col overflow-hidden shadow-2xl">
            <div className="p-3.5 border-b border-white/[0.06] flex items-center justify-between bg-black/20">
              <div className="flex items-center gap-2">
                <Gamepad2 className="w-4 h-4 text-apple-emerald" />
                <span className="font-semibold text-xs text-neutral-100">Responsive Playable Sandbox</span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-apple-emerald/15 text-apple-emerald border border-apple-emerald/25">
                  Phaser 3 / 60 FPS
                </span>
              </div>
              <button
                onClick={() => setActivePlayableModal(false)}
                className="p-1 rounded-md text-neutral-400 hover:text-white hover:bg-white/[0.08] transition-colors"
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
