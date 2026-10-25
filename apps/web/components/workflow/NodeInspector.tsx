'use client';

import React from 'react';
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
} from 'lucide-react';
import { cn, formatCurrency } from '@/lib/utils';
import { WorkflowNodeData } from '@/lib/types';

interface NodeInspectorProps {
  selectedNode: WorkflowNodeData | null;
  onUpdateNode: (updated: Partial<WorkflowNodeData>) => void;
  onOpenComfySubCanvas?: () => void;
}

export function NodeInspector({ selectedNode, onUpdateNode, onOpenComfySubCanvas }: NodeInspectorProps) {
  if (!selectedNode) {
    return (
      <div className="w-80 border-l border-slate-800 bg-[#070b14]/95 p-6 flex flex-col items-center justify-center text-center text-slate-500 h-full select-none">
        <Layers className="w-10 h-10 mb-3 text-slate-700 animate-pulse" />
        <div className="text-xs font-semibold text-slate-400">No Node Selected</div>
        <p className="text-[11px] text-slate-600 mt-1 max-w-[200px]">
          Click any node on the canvas to configure parameters, prompt templates, models, and retry policies.
        </p>
      </div>
    );
  }

  return (
    <div className="w-80 border-l border-slate-800 bg-[#070b14]/95 flex flex-col flex-shrink-0 select-none overflow-hidden h-full">
      {/* Header */}
      <div className="p-4 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Settings className="w-4 h-4 text-cyan-400" />
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-200 font-mono">
            Node Inspector
          </span>
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
          {selectedNode.category}
        </span>
      </div>

      {/* Inspector Form */}
      <div className="flex-1 overflow-y-auto p-4 space-y-5 text-xs">
        {/* Node Title & Executor */}
        <div className="space-y-1.5">
          <label className="text-[11px] font-medium text-slate-400">Node Title</label>
          <input
            type="text"
            value={selectedNode.title}
            onChange={(e) => onUpdateNode({ title: e.target.value })}
            className="w-full bg-slate-900 border border-slate-800 rounded-md px-3 py-1.5 text-xs text-slate-100 focus:outline-none focus:border-cyan-500"
          />
          <div className="text-[10px] font-mono text-slate-500">
            Executor: <span className="text-slate-300">{selectedNode.executor}</span>
          </div>
        </div>

        {/* ComfyUI Deep Hybrid Sub-Canvas Integration Card */}
        {(selectedNode.id === 'node_image_gen' || selectedNode.executor === 'ComfyImageWorker' || selectedNode.model?.includes('comfy')) && (
          <div className="p-3.5 rounded-xl bg-gradient-to-br from-cyan-950/60 via-slate-900 to-slate-900 border border-cyan-800/70 space-y-2.5 shadow-lg shadow-cyan-950/40">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-1.5">
                <Layers className="w-4 h-4 text-cyan-400" />
                <span className="text-xs font-semibold text-slate-100 font-mono">
                  ComfyUI Micro-Graph
                </span>
              </div>
              <span className="text-[9px] font-mono text-cyan-300 bg-cyan-950 px-1.5 py-0.5 rounded border border-cyan-800">
                Tier-2 Native
              </span>
            </div>
            <p className="text-[10px] text-slate-400 leading-relaxed font-sans">
              Dive into the multi-node diffusion pipeline (KSampler, ControlNet, LoRA, VAE Decode) with real-time latent previews.
            </p>
            <button
              type="button"
              onClick={onOpenComfySubCanvas}
              className="w-full flex items-center justify-center gap-2 py-2 px-3 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-mono text-xs font-semibold shadow-md shadow-cyan-950 transition-all cursor-pointer"
            >
              <ExternalLink className="w-3.5 h-3.5" />
              <span>Customize Comfy Pipeline</span>
            </button>
          </div>
        )}

        {/* Model Selection */}
        <div className="space-y-1.5">
          <label className="text-[11px] font-medium text-slate-400 flex items-center gap-1.5">
            <Cpu className="w-3.5 h-3.5 text-cyan-400" />
            Model / Engine
          </label>
          <select
            value={selectedNode.model || 'Deterministic'}
            onChange={(e) => onUpdateNode({ model: e.target.value })}
            className="w-full bg-slate-900 border border-slate-800 rounded-md px-3 py-1.5 text-xs text-slate-100 focus:outline-none focus:border-cyan-500"
          >
            <option value="gpt-4o">OpenAI: GPT-4o (Vision & Structured)</option>
            <option value="claude-3-5-sonnet">Anthropic: Claude 3.5 Sonnet</option>
            <option value="gemini-1.5-pro">Google: Gemini 1.5 Pro</option>
            <option value="sdxl-turbo / comfy-flux">ComfyUI: SDXL Turbo / FLUX.1</option>
            <option value="remotion-v4-ssr">Remotion: SSR 9:16 Bundle Renderer</option>
            <option value="playwright-chromium">Playwright: Chromium Headless</option>
            <option value="Deterministic">Deterministic / Rule-based</option>
          </select>
        </div>

        {/* Prompt Template Version */}
        <div className="space-y-1.5">
          <label className="text-[11px] font-medium text-slate-400 flex items-center gap-1.5">
            <FileCode className="w-3.5 h-3.5 text-blue-400" />
            Prompt Template Version
          </label>
          <input
            type="text"
            value={selectedNode.promptVersion || 'pt_default_v2'}
            onChange={(e) => onUpdateNode({ promptVersion: e.target.value })}
            className="w-full bg-slate-900 border border-slate-800 rounded-md px-3 py-1.5 text-xs font-mono text-cyan-300 focus:outline-none focus:border-cyan-500"
          />
        </div>

        {/* Resilience & Timeout Controls */}
        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-1.5">
            <label className="text-[11px] font-medium text-slate-400 flex items-center gap-1">
              <Clock className="w-3.5 h-3.5 text-amber-400" />
              Timeout (s)
            </label>
            <input
              type="number"
              value={selectedNode.timeoutSec || 30}
              onChange={(e) => onUpdateNode({ timeoutSec: parseInt(e.target.value, 10) || 10 })}
              className="w-full bg-slate-900 border border-slate-800 rounded-md px-3 py-1.5 text-xs font-mono text-slate-100 focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-[11px] font-medium text-slate-400 flex items-center gap-1">
              <RotateCcw className="w-3.5 h-3.5 text-emerald-400" />
              Max Retries
            </label>
            <input
              type="number"
              value={selectedNode.maxRetries || 3}
              onChange={(e) => onUpdateNode({ maxRetries: parseInt(e.target.value, 10) || 1 })}
              className="w-full bg-slate-900 border border-slate-800 rounded-md px-3 py-1.5 text-xs font-mono text-slate-100 focus:outline-none focus:border-cyan-500"
            />
          </div>
        </div>

        {/* Cost & Token Accounting */}
        <div className="p-3 rounded-lg bg-slate-900/60 border border-slate-800 space-y-2">
          <div className="text-[11px] font-semibold text-slate-300 flex items-center gap-1.5">
            <DollarSign className="w-3.5 h-3.5 text-cyan-400" />
            Estimated Cost / Call
          </div>
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-400">Per Invocation:</span>
            <span className="font-mono font-semibold text-slate-200">
              {selectedNode.costEstimate === 'unknown' ? (
                <span className="text-amber-400 text-[10px] font-mono px-1.5 py-0.5 rounded bg-amber-950/50 border border-amber-800/40">
                  unknown (media quote)
                </span>
              ) : (
                `$${(selectedNode.costEstimate || 0.02).toFixed(4)} USD`
              )}
            </span>
          </div>
          <div className="text-[10px] text-slate-500 leading-tight">
            Enforced by LiteLLM Model Gateway and Run Hard Budget Limit.
          </div>
        </div>

        {/* Typed Ports Inspection */}
        <div className="space-y-2">
          <div className="text-[11px] font-semibold text-slate-300">Input / Output Ports</div>
          <div className="space-y-1 font-mono text-[11px]">
            <div className="text-slate-400 text-[10px] uppercase">Inputs:</div>
            {selectedNode.inputs?.map((p) => (
              <div key={p.id} className="p-1.5 rounded bg-slate-900 border border-slate-800/80 flex items-center justify-between">
                <span className="text-slate-300">{p.label}</span>
                <span className="text-[10px] text-cyan-400">{p.type}</span>
              </div>
            ))}
            <div className="text-slate-400 text-[10px] uppercase pt-1">Outputs:</div>
            {selectedNode.outputs?.map((p) => (
              <div key={p.id} className="p-1.5 rounded bg-slate-900 border border-slate-800/80 flex items-center justify-between">
                <span className="text-slate-300">{p.label}</span>
                <span className="text-[10px] text-purple-400">{p.type}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Retry Attempt Log If Failed / Fallback */}
        {selectedNode.lastAttempt && selectedNode.lastAttempt > 1 && (
          <div className="p-3 rounded-lg bg-rose-950/30 border border-rose-900/50 space-y-2">
            <div className="flex items-center gap-1.5 text-rose-400 font-semibold text-xs">
              <AlertTriangle className="w-3.5 h-3.5" />
              Attempt #{selectedNode.lastAttempt} (Retry Applied)
            </div>
            <p className="text-[11px] text-rose-300/80 leading-relaxed">
              Attempt #1 timed out after 9000ms. Fallback policy switched to secondary GPU cluster.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
