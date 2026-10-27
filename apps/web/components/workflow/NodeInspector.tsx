'use client';

import React, { useState } from 'react';
import {
  Settings,
  Cpu,
  Clock,
  RotateCcw,
  DollarSign,
  FileCode,
  AlertTriangle,
  CheckCircle2,
  ExternalLink,
  ChevronRight,
  Layers,
  Sliders,
  ArrowRightLeft,
} from 'lucide-react';
import { cn, formatCurrency } from '@/lib/utils';
import { WorkflowNodeData } from '@/lib/types';

interface NodeInspectorProps {
  selectedNode: WorkflowNodeData | null;
  onUpdateNode: (updated: Partial<WorkflowNodeData>) => void;
  onOpenComfySubCanvas?: () => void;
}

export function NodeInspector({ selectedNode, onUpdateNode, onOpenComfySubCanvas }: NodeInspectorProps) {
  const [activeTab, setActiveTab] = useState<'general' | 'engine' | 'ports'>('general');

  if (!selectedNode) {
    return (
      <div className="w-80 border-l border-white/[0.06] bg-[#0c101a]/75 backdrop-blur-2xl p-6 flex flex-col items-center justify-center text-center text-neutral-500 h-full select-none">
        <div className="w-12 h-12 rounded-2xl bg-white/[0.03] border border-white/[0.06] flex items-center justify-center mb-3">
          <Layers className="w-6 h-6 text-neutral-500" />
        </div>
        <div className="text-xs font-semibold text-neutral-300">No Block Selected</div>
        <p className="text-[11px] text-neutral-500 mt-1 max-w-[210px] leading-relaxed">
          Select any pipeline node on the canvas to configure parameters, prompt templates, models, and retry limits.
        </p>
      </div>
    );
  }

  const isComfyNode = selectedNode.id === 'node_image_gen' ||
    selectedNode.executor === 'ComfyImageWorker' ||
    selectedNode.model?.includes('comfy');

  return (
    <div className="w-80 border-l border-white/[0.06] bg-[#0c101a]/75 backdrop-blur-2xl flex flex-col flex-shrink-0 select-none overflow-hidden h-full">
      {/* Apple Inspector Header */}
      <div className="p-3.5 border-b border-white/[0.06] flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sliders className="w-4 h-4 text-apple-blue" />
          <span className="text-xs font-semibold tracking-tight text-neutral-200">
            Inspector
          </span>
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-white/[0.06] text-neutral-400 border border-white/[0.08]">
          {selectedNode.category}
        </span>
      </div>

      {/* Segmented Tab Controls */}
      <div className="px-3 py-2 border-b border-white/[0.05] bg-black/10">
        <div className="apple-segmented w-full justify-between">
          <button
            onClick={() => setActiveTab('general')}
            className={cn('apple-segmented-item flex-1 text-center', activeTab === 'general' && 'apple-segmented-item-active')}
          >
            General
          </button>
          <button
            onClick={() => setActiveTab('engine')}
            className={cn('apple-segmented-item flex-1 text-center', activeTab === 'engine' && 'apple-segmented-item-active')}
          >
            Model & Prompt
          </button>
          <button
            onClick={() => setActiveTab('ports')}
            className={cn('apple-segmented-item flex-1 text-center', activeTab === 'ports' && 'apple-segmented-item-active')}
          >
            I/O & Limits
          </button>
        </div>
      </div>

      {/* Tab Content Container */}
      <div className="flex-1 overflow-y-auto p-3.5 space-y-4 text-xs">
        {/* TAB 1: GENERAL */}
        {activeTab === 'general' && (
          <div className="space-y-4">
            {/* Title & Executor Grouped Card */}
            <div className="rounded-xl bg-white/[0.03] border border-white/[0.06] p-3 space-y-2.5">
              <div className="space-y-1">
                <label className="text-[11px] font-medium text-neutral-400">Node Title</label>
                <input
                  type="text"
                  value={selectedNode.title}
                  onChange={(e) => onUpdateNode({ title: e.target.value })}
                  className="w-full bg-black/30 border border-white/[0.08] rounded-lg px-2.5 py-1.5 text-xs text-neutral-100 focus:outline-none focus:border-apple-blue"
                />
              </div>

              <div className="pt-1 border-t border-white/[0.04] flex items-center justify-between text-[10px] font-mono">
                <span className="text-neutral-500">Executor:</span>
                <span className="text-neutral-300 font-semibold">{selectedNode.executor}</span>
              </div>
            </div>

            {/* ComfyUI Deep Hybrid Sub-Canvas Card */}
            {isComfyNode && (
              <div className="p-3.5 rounded-xl bg-gradient-to-br from-apple-purple/15 via-white/[0.02] to-transparent border border-apple-purple/30 space-y-2.5 shadow-sm">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5">
                    <Layers className="w-4 h-4 text-apple-purple" />
                    <span className="text-xs font-semibold text-neutral-100 tracking-tight">
                      ComfyUI Micro-Graph
                    </span>
                  </div>
                  <span className="text-[9px] font-mono text-apple-purple bg-apple-purple/15 px-1.5 py-0.5 rounded-full border border-apple-purple/25">
                    Tier-2
                  </span>
                </div>
                <p className="text-[11px] text-neutral-400 leading-relaxed font-sans">
                  Deep multi-node diffusion pipeline (KSampler, ControlNet, LoRA, VAE Decode) with real-time latent previews.
                </p>
                <button
                  type="button"
                  onClick={onOpenComfySubCanvas}
                  className="w-full flex items-center justify-center gap-2 py-1.5 px-3 rounded-lg bg-apple-purple hover:bg-apple-purple/90 text-white font-medium text-xs shadow-sm transition-all cursor-pointer"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                  <span>Open Comfy Pipeline</span>
                </button>
              </div>
            )}

            {/* Cost & Accounting Pill */}
            <div className="p-3 rounded-xl bg-white/[0.03] border border-white/[0.06] space-y-2">
              <div className="text-[11px] font-semibold text-neutral-300 flex items-center gap-1.5">
                <DollarSign className="w-3.5 h-3.5 text-apple-amber" />
                <span>Cost Accounting</span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-neutral-400">Est. Invocation:</span>
                <span className="font-mono font-semibold text-neutral-200">
                  {selectedNode.costEstimate === 'unknown' ? (
                    <span className="text-apple-amber text-[10px] font-mono px-2 py-0.5 rounded-full bg-apple-amber/10 border border-apple-amber/20">
                      media quote
                    </span>
                  ) : (
                    `$${(selectedNode.costEstimate || 0.02).toFixed(4)} USD`
                  )}
                </span>
              </div>
              <div className="text-[10px] text-neutral-500 leading-tight">
                Protected by LiteLLM Gateway and Hard Budget Cap.
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: ENGINE & PROMPT */}
        {activeTab === 'engine' && (
          <div className="space-y-4">
            {/* Model Selection Group */}
            <div className="rounded-xl bg-white/[0.03] border border-white/[0.06] p-3 space-y-2">
              <label className="text-[11px] font-medium text-neutral-400 flex items-center gap-1.5">
                <Cpu className="w-3.5 h-3.5 text-apple-blue" />
                Foundation Engine
              </label>
              <select
                value={selectedNode.model || 'Deterministic'}
                onChange={(e) => onUpdateNode({ model: e.target.value })}
                className="w-full bg-black/30 border border-white/[0.08] rounded-lg px-2.5 py-1.5 text-xs text-neutral-200 focus:outline-none focus:border-apple-blue"
              >
                <option value="gpt-4o" className="bg-[#121724]">OpenAI: GPT-4o (Vision & Structured)</option>
                <option value="claude-3-5-sonnet" className="bg-[#121724]">Anthropic: Claude 3.5 Sonnet</option>
                <option value="gemini-1.5-pro" className="bg-[#121724]">Google: Gemini 1.5 Pro</option>
                <option value="sdxl-turbo / comfy-flux" className="bg-[#121724]">ComfyUI: SDXL Turbo / FLUX.1</option>
                <option value="remotion-v4-ssr" className="bg-[#121724]">Remotion: SSR 9:16 Bundle Renderer</option>
                <option value="playwright-chromium" className="bg-[#121724]">Playwright: Chromium Headless</option>
                <option value="Deterministic" className="bg-[#121724]">Deterministic / Rule-based</option>
              </select>
            </div>

            {/* Prompt Template Group */}
            <div className="rounded-xl bg-white/[0.03] border border-white/[0.06] p-3 space-y-2">
              <label className="text-[11px] font-medium text-neutral-400 flex items-center gap-1.5">
                <FileCode className="w-3.5 h-3.5 text-apple-purple" />
                Prompt Template
              </label>
              <input
                type="text"
                value={selectedNode.promptVersion || 'pt_default_v2'}
                onChange={(e) => onUpdateNode({ promptVersion: e.target.value })}
                className="w-full bg-black/30 border border-white/[0.08] rounded-lg px-2.5 py-1.5 text-xs font-mono text-apple-teal focus:outline-none focus:border-apple-blue"
              />
              <span className="text-[10px] text-neutral-500">Version-locked prompt artifact</span>
            </div>
          </div>
        )}

        {/* TAB 3: PORTS & LIMITS */}
        {activeTab === 'ports' && (
          <div className="space-y-4">
            {/* Timeout & Retries Steppers */}
            <div className="rounded-xl bg-white/[0.03] border border-white/[0.06] p-3 space-y-3">
              <div className="flex items-center justify-between">
                <label className="text-[11px] font-medium text-neutral-400 flex items-center gap-1.5">
                  <Clock className="w-3.5 h-3.5 text-apple-amber" />
                  Timeout (s)
                </label>
                <input
                  type="number"
                  value={selectedNode.timeoutSec || 30}
                  onChange={(e) => onUpdateNode({ timeoutSec: parseInt(e.target.value, 10) || 10 })}
                  className="w-20 bg-black/30 border border-white/[0.08] rounded-lg px-2 py-1 text-xs font-mono text-right text-neutral-200 focus:outline-none focus:border-apple-blue"
                />
              </div>

              <div className="pt-2 border-t border-white/[0.04] flex items-center justify-between">
                <label className="text-[11px] font-medium text-neutral-400 flex items-center gap-1.5">
                  <RotateCcw className="w-3.5 h-3.5 text-apple-emerald" />
                  Max Retries
                </label>
                <input
                  type="number"
                  value={selectedNode.maxRetries || 3}
                  onChange={(e) => onUpdateNode({ maxRetries: parseInt(e.target.value, 10) || 1 })}
                  className="w-20 bg-black/30 border border-white/[0.08] rounded-lg px-2 py-1 text-xs font-mono text-right text-neutral-200 focus:outline-none focus:border-apple-blue"
                />
              </div>
            </div>

            {/* Typed Ports Inspection */}
            <div className="rounded-xl bg-white/[0.03] border border-white/[0.06] p-3 space-y-2.5">
              <div className="text-[11px] font-semibold text-neutral-300">Connection Ports</div>
              <div className="space-y-1.5 font-mono text-[11px]">
                <div className="text-neutral-500 text-[10px] uppercase font-semibold">Inputs:</div>
                {selectedNode.inputs?.length ? (
                  selectedNode.inputs.map((p) => (
                    <div key={p.id} className="p-1.5 rounded-lg bg-black/20 border border-white/[0.04] flex items-center justify-between">
                      <span className="text-neutral-300">{p.label}</span>
                      <span className="text-[10px] text-apple-teal px-1.5 py-0.2 rounded bg-apple-teal/10">{p.type}</span>
                    </div>
                  ))
                ) : (
                  <div className="text-[10px] text-neutral-600 italic">No incoming ports (Root node)</div>
                )}

                <div className="text-neutral-500 text-[10px] uppercase font-semibold pt-1">Outputs:</div>
                {selectedNode.outputs?.map((p) => (
                  <div key={p.id} className="p-1.5 rounded-lg bg-black/20 border border-white/[0.04] flex items-center justify-between">
                    <span className="text-neutral-300">{p.label}</span>
                    <span className="text-[10px] text-apple-purple px-1.5 py-0.2 rounded bg-apple-purple/10">{p.type}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Retry Attempt Log */}
            {selectedNode.lastAttempt && selectedNode.lastAttempt > 1 && (
              <div className="p-3 rounded-xl bg-apple-red/10 border border-apple-red/25 space-y-1.5">
                <div className="flex items-center gap-1.5 text-apple-red font-semibold text-xs">
                  <AlertTriangle className="w-3.5 h-3.5" />
                  Attempt #{selectedNode.lastAttempt} (Retry Applied)
                </div>
                <p className="text-[11px] text-apple-red/80 leading-relaxed">
                  Attempt #1 timed out after 9000ms. Fallback policy switched to secondary GPU cluster.
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
