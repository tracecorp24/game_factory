// CreativeForge Intelligence Studio v3.0 - ComfyUI Deep Hybrid Integration
// components/comfy/ComfyCustomNode.tsx

'use client';

import React, { memo } from 'react';
import { Handle, Position, NodeProps } from '@xyflow/react';
import {
  Cpu,
  Layers,
  Sparkles,
  Sliders,
  Type,
  Image as ImageIcon,
  CheckCircle2,
  AlertCircle,
  Dices,
  Eye,
} from 'lucide-react';
import { ComfyNodeData, COMFY_PORT_COLORS, ComfyPortType } from '@/lib/comfy/types';
import { cn } from '@/lib/utils';

const CATEGORY_ICONS: Record<string, React.ElementType> = {
  loader: Cpu,
  sampling: Sliders,
  conditioning: Type,
  latent: Sparkles,
  image: ImageIcon,
  controlnet: Layers,
  lora: Sparkles,
};

export const ComfyCustomNode = memo(({ data, selected }: NodeProps<any>) => {
  const nodeData = data as ComfyNodeData;
  const CategoryIcon = CATEGORY_ICONS[nodeData.category || 'sampling'] || Sliders;

  const isExecuting = nodeData.status === 'executing';
  const isCompleted = nodeData.status === 'completed';
  const isError = nodeData.status === 'error';

  return (
    <div
      className={cn(
        'w-72 rounded-xl bg-[#0b101d]/95 border text-slate-200 shadow-2xl transition-all duration-200 font-sans backdrop-blur-md',
        selected
          ? 'border-cyan-400 ring-2 ring-cyan-500/30 shadow-cyan-900/40'
          : 'border-slate-800 hover:border-slate-700',
        isExecuting && 'border-cyan-400 ring-2 ring-cyan-400/50 animate-pulse',
        isError && 'border-rose-500 ring-2 ring-rose-500/30'
      )}
    >
      {/* Node Header */}
      <div className="flex items-center justify-between px-3.5 py-2.5 border-b border-slate-800/80 bg-slate-900/60 rounded-t-xl">
        <div className="flex items-center gap-2 min-w-0">
          <div className="p-1 rounded bg-slate-800 text-cyan-400 border border-slate-700/60">
            <CategoryIcon className="w-3.5 h-3.5" />
          </div>
          <div className="min-w-0">
            <div className="text-xs font-semibold text-slate-100 truncate flex items-center gap-1.5">
              <span>{nodeData.title}</span>
              <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-slate-800 text-slate-400 border border-slate-700">
                #{nodeData.nodeId}
              </span>
            </div>
            <div className="text-[9px] font-mono text-slate-500 truncate">{nodeData.classType}</div>
          </div>
        </div>

        {/* Status Indicator */}
        <div>
          {isExecuting && (
            <span className="flex items-center gap-1 text-[10px] font-mono text-cyan-300 bg-cyan-950/70 border border-cyan-800/80 px-1.5 py-0.5 rounded">
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-ping" />
              Exec
            </span>
          )}
          {isCompleted && (
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
          )}
          {isError && (
            <AlertCircle className="w-3.5 h-3.5 text-rose-400" />
          )}
        </div>
      </div>

      {/* Progress Bar (If executing) */}
      {isExecuting && nodeData.progress && (
        <div className="w-full bg-slate-900 h-1.5 overflow-hidden">
          <div
            className="bg-gradient-to-r from-cyan-500 to-blue-500 h-full transition-all duration-150"
            style={{
              width: `${Math.round((nodeData.progress.step / nodeData.progress.totalSteps) * 100)}%`,
            }}
          />
        </div>
      )}

      {/* Body: Inputs & Outputs with Port Handles */}
      <div className="p-3 space-y-3">
        {/* Dynamic Ports Section */}
        <div className="grid grid-cols-2 gap-2 text-[10px] font-mono">
          {/* Inputs (Left) */}
          <div className="space-y-2">
            {nodeData.inputs.map((port) => {
              const portColor = COMFY_PORT_COLORS[port.type] || '#94a3b8';
              return (
                <div key={port.id} className="relative flex items-center gap-1.5 min-h-[18px]">
                  <Handle
                    type="target"
                    position={Position.Left}
                    id={port.id}
                    style={{
                      backgroundColor: portColor,
                      width: 10,
                      height: 10,
                      border: '2px solid #0b101d',
                      left: -17,
                    }}
                  />
                  <span
                    className="w-2 h-2 rounded-full inline-block flex-shrink-0"
                    style={{ backgroundColor: portColor }}
                  />
                  <span className="text-slate-300 truncate" title={`${port.name} (${port.type})`}>
                    {port.name}
                  </span>
                </div>
              );
            })}
          </div>

          {/* Outputs (Right) */}
          <div className="space-y-2 text-right">
            {nodeData.outputs.map((port) => {
              const portColor = COMFY_PORT_COLORS[port.type] || '#94a3b8';
              return (
                <div key={port.id} className="relative flex items-center justify-end gap-1.5 min-h-[18px]">
                  <span className="text-slate-300 truncate" title={`${port.name} (${port.type})`}>
                    {port.name}
                  </span>
                  <span
                    className="w-2 h-2 rounded-full inline-block flex-shrink-0"
                    style={{ backgroundColor: portColor }}
                  />
                  <Handle
                    type="source"
                    position={Position.Right}
                    id={port.id}
                    style={{
                      backgroundColor: portColor,
                      width: 10,
                      height: 10,
                      border: '2px solid #0b101d',
                      right: -17,
                    }}
                  />
                </div>
              );
            })}
          </div>
        </div>

        {/* Embedded Interactive Controls based on Parameters */}
        {Object.keys(nodeData.parameters || {}).length > 0 && (
          <div className="pt-2 border-t border-slate-800/60 space-y-2.5">
            {/* Text / Prompt Parameter */}
            {nodeData.parameters.text !== undefined && (
              <div className="space-y-1">
                <div className="flex items-center justify-between text-[10px] text-slate-400 font-mono">
                  <span>Prompt / Text</span>
                  <span className="text-cyan-400 text-[9px] bg-cyan-950/40 px-1 rounded border border-cyan-800/40">
                    Tokenized
                  </span>
                </div>
                <textarea
                  readOnly
                  value={nodeData.parameters.text}
                  rows={2}
                  className="w-full bg-slate-900/90 border border-slate-800 rounded px-2 py-1 text-[11px] text-slate-200 resize-none font-mono focus:outline-none"
                />
              </div>
            )}

            {/* Checkpoint Name */}
            {nodeData.parameters.ckpt_name !== undefined && (
              <div className="space-y-1">
                <label className="text-[10px] text-slate-400 font-mono">Checkpoint</label>
                <div className="w-full bg-slate-900/90 border border-slate-800 rounded px-2 py-1 text-[11px] font-mono text-cyan-300 truncate">
                  {nodeData.parameters.ckpt_name}
                </div>
              </div>
            )}

            {/* Steps & CFG Sliders/Displays */}
            {nodeData.parameters.steps !== undefined && (
              <div className="grid grid-cols-2 gap-2 text-[10px] font-mono">
                <div className="bg-slate-900/70 border border-slate-800/80 rounded p-1.5">
                  <span className="text-slate-500">Steps:</span>{' '}
                  <span className="text-cyan-300 font-bold">{nodeData.parameters.steps}</span>
                </div>
                <div className="bg-slate-900/70 border border-slate-800/80 rounded p-1.5">
                  <span className="text-slate-500">CFG:</span>{' '}
                  <span className="text-amber-300 font-bold">{nodeData.parameters.cfg}</span>
                </div>
              </div>
            )}

            {/* Seed parameter */}
            {nodeData.parameters.seed !== undefined && (
              <div className="flex items-center justify-between bg-slate-900/70 border border-slate-800/80 rounded px-2 py-1 text-[10px] font-mono">
                <div className="flex items-center gap-1 text-slate-400">
                  <Dices className="w-3 h-3 text-purple-400" />
                  <span>Seed:</span>
                </div>
                <span className="text-slate-200">{nodeData.parameters.seed}</span>
              </div>
            )}

            {/* Sampler & Scheduler */}
            {nodeData.parameters.sampler_name !== undefined && (
              <div className="flex items-center justify-between text-[9px] font-mono text-slate-400 px-0.5">
                <span>Sampler: <span className="text-slate-300">{nodeData.parameters.sampler_name}</span></span>
                <span>Scheduler: <span className="text-slate-300">{nodeData.parameters.scheduler}</span></span>
              </div>
            )}

            {/* LoRA details */}
            {nodeData.parameters.lora_name !== undefined && (
              <div className="space-y-1">
                <div className="text-[10px] text-slate-400 font-mono truncate">
                  LoRA: <span className="text-purple-300">{nodeData.parameters.lora_name}</span>
                </div>
                <div className="text-[10px] text-slate-400 font-mono">
                  Strength: <span className="text-cyan-300 font-bold">{nodeData.parameters.strength_model}</span>
                </div>
              </div>
            )}

            {/* Empty Latent Dimensions */}
            {nodeData.parameters.width !== undefined && (
              <div className="flex items-center justify-between bg-slate-900/70 border border-slate-800/80 rounded px-2 py-1 text-[10px] font-mono">
                <span className="text-slate-400">Resolution:</span>
                <span className="text-emerald-300 font-semibold">
                  {nodeData.parameters.width} × {nodeData.parameters.height}
                </span>
              </div>
            )}
          </div>
        )}

        {/* Error message if node failed */}
        {nodeData.errorMessage && (
          <div className="p-2 rounded bg-rose-950/40 border border-rose-800/60 text-rose-300 text-[10px] font-mono">
            {nodeData.errorMessage}
          </div>
        )}
      </div>
    </div>
  );
});

ComfyCustomNode.displayName = 'ComfyCustomNode';
