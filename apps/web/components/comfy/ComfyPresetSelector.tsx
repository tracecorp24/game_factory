// CreativeForge Intelligence Studio v3.0 - ComfyUI Deep Hybrid Integration
// components/comfy/ComfyPresetSelector.tsx

'use client';

import React from 'react';
import { COMFY_PRESETS } from '@/lib/comfy/presets';
import { ComfyPreset } from '@/lib/comfy/types';
import { Sparkles, Layers, Check } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ComfyPresetSelectorProps {
  activePresetId: string;
  onSelectPreset: (preset: ComfyPreset) => void;
}

export function ComfyPresetSelector({ activePresetId, onSelectPreset }: ComfyPresetSelectorProps) {
  return (
    <div className="flex flex-col gap-2 p-3 bg-[#080d1a] border-b border-slate-800 select-none">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-cyan-400" />
          <span className="text-xs font-semibold text-slate-200 uppercase tracking-wider font-mono">
            Production Presets (4 Architect-Verified Pipelines)
          </span>
        </div>
        <span className="text-[10px] font-mono text-slate-500">
          Zero-Code Swappable Graph
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-2.5">
        {COMFY_PRESETS.map((preset) => {
          const isActive = preset.id === activePresetId;
          return (
            <button
              key={preset.id}
              onClick={() => onSelectPreset(preset)}
              className={cn(
                'group relative flex items-start gap-2.5 p-2 rounded-lg border text-left transition-all duration-150',
                isActive
                  ? 'bg-gradient-to-r from-cyan-950/60 to-blue-950/40 border-cyan-500/80 shadow-md shadow-cyan-950/40'
                  : 'bg-slate-900/50 border-slate-800/80 hover:border-slate-700 hover:bg-slate-800/50'
              )}
            >
              <div className="relative w-12 h-12 rounded overflow-hidden flex-shrink-0 border border-slate-800 bg-slate-950">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={preset.thumbnailUrl}
                  alt={preset.name}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                />
                {isActive && (
                  <div className="absolute inset-0 bg-cyan-500/20 flex items-center justify-center">
                    <Check className="w-4 h-4 text-cyan-200 drop-shadow" />
                  </div>
                )}
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-1 mb-0.5">
                  <span className="text-xs font-semibold text-slate-200 truncate group-hover:text-cyan-300">
                    {preset.name}
                  </span>
                </div>
                <div className="flex items-center gap-1.5 mb-1">
                  <span className="text-[9px] font-mono px-1.5 py-0.2 rounded bg-slate-800 text-cyan-300 border border-slate-700">
                    {preset.badge}
                  </span>
                  <span className="text-[9px] font-mono text-slate-500 uppercase">
                    {preset.category}
                  </span>
                </div>
                <p className="text-[10px] text-slate-400 line-clamp-1 leading-tight">
                  {preset.description}
                </p>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
