'use client';

import React, { memo, useState } from 'react';
import { Handle, Position } from '@xyflow/react';
import {
  Cpu,
  CheckCircle2,
  AlertTriangle,
  Clock,
  RefreshCw,
  RotateCcw,
  Eye,
  Play,
  Sparkles,
  Maximize2,
  FileCheck,
  ShieldAlert,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { WorkflowNodeData } from '@/lib/types';
import { useAppStore } from '@/lib/store';
import { toast } from '@/lib/toast';

const PORT_COLORS: Record<string, string> = {
  text: '!bg-cyan-400 !border-cyan-600',
  concept_spec: '!bg-blue-400 !border-blue-600',
  image: '!bg-purple-400 !border-purple-600',
  video: '!bg-amber-400 !border-amber-600',
  code: '!bg-emerald-400 !border-emerald-600',
  eval_report: '!bg-rose-400 !border-rose-600',
  manifest: '!bg-indigo-400 !border-indigo-600',
  trigger: '!bg-slate-300 !border-slate-500',
};

const CATEGORY_STYLES: Record<string, { bg: string; text: string; border: string }> = {
  'Market Intelligence': { bg: 'bg-cyan-950/40', text: 'text-cyan-400', border: 'border-cyan-800/40' },
  'Game DNA': { bg: 'bg-purple-950/40', text: 'text-purple-400', border: 'border-purple-800/40' },
  'Ideation': { bg: 'bg-blue-950/40', text: 'text-blue-400', border: 'border-blue-800/40' },
  'Generation': { bg: 'bg-amber-950/40', text: 'text-amber-400', border: 'border-amber-800/40' },
  'Evaluation': { bg: 'bg-rose-950/40', text: 'text-rose-400', border: 'border-rose-800/40' },
  'Control': { bg: 'bg-slate-900', text: 'text-slate-400', border: 'border-slate-700' },
  'Export': { bg: 'bg-emerald-950/40', text: 'text-emerald-400', border: 'border-emerald-800/40' },
};

export const CustomNode = memo((props: any) => {
  const nodeData = props.data as WorkflowNodeData;
  const selected = props.selected;
  const catStyle = CATEGORY_STYLES[nodeData.category] || CATEGORY_STYLES['Control'];
  const [showQuickActions, setShowQuickActions] = useState(false);

  const handleRerun = (e: React.MouseEvent) => {
    e.stopPropagation();
    toast.info('Checkpoint Yeniden Başlatıldı', `"${nodeData.title}" düğümünden itibaren yürütme tetiklendi. Önceki adımlar önbellekten kullanılıyor.`);
  };

  const handleIntervene = (e: React.MouseEvent) => {
    e.stopPropagation();
    toast.warning('Manuel Müdahale Modu', `"${nodeData.title}" parametreleri Node Inspector paneline kilitlendi.`);
  };

  return (
    <div
      onMouseEnter={() => setShowQuickActions(true)}
      onMouseLeave={() => setShowQuickActions(false)}
      className={cn(
        'w-72 rounded-2xl border bg-slate-900/95 shadow-2xl transition-all duration-200 select-none overflow-hidden backdrop-blur-md relative group',
        selected ? 'border-cyan-400 ring-2 ring-cyan-400/40 shadow-cyan-500/25 scale-[1.02]' : 'border-slate-800 hover:border-slate-700',
        nodeData.status === 'running' && 'border-cyan-400 ring-1 ring-cyan-400/50 shadow-cyan-500/30',
        nodeData.status === 'failed' && 'border-rose-500 shadow-rose-500/30'
      )}
    >
      {/* Input Handles */}
      <div className="relative">
        {nodeData.inputs?.map((input, idx) => {
          const topPercent = ((idx + 1) / (nodeData.inputs.length + 1)) * 100;
          return (
            <Handle
              key={input.id}
              type="target"
              position={Position.Left}
              id={input.id}
              className={cn(
                '!w-3.5 !h-3.5 rounded-full border-2 border-slate-950 shadow-sm transition-transform hover:scale-125 z-10',
                PORT_COLORS[input.type] || '!bg-slate-400'
              )}
              style={{ top: `${topPercent}%` }}
              title={`In: ${input.label} (${input.type})`}
            />
          );
        })}
      </div>

      {/* Node Header */}
      <div className={cn('px-3.5 py-2.5 border-b flex items-center justify-between', catStyle.border, catStyle.bg)}>
        <div className="flex items-center gap-2 min-w-0">
          <div className="w-6 h-6 rounded-md bg-slate-800/80 border border-slate-700 flex items-center justify-center flex-shrink-0">
            <Cpu className={cn('w-3.5 h-3.5', catStyle.text)} />
          </div>
          <div className="min-w-0">
            <div className="text-xs font-semibold text-slate-100 truncate">{nodeData.title}</div>
            <div className="text-[10px] font-mono text-slate-400 truncate">{nodeData.executor}</div>
          </div>
        </div>

        {/* Status Pill */}
        <div>
          {nodeData.status === 'completed' && (
            <span className="flex items-center gap-1 text-[10px] font-mono font-medium text-emerald-400 bg-emerald-950/80 px-1.5 py-0.5 rounded border border-emerald-800/60">
              <CheckCircle2 className="w-3 h-3" /> Done
            </span>
          )}
          {nodeData.status === 'running' && (
            <span className="flex items-center gap-1 text-[10px] font-mono font-medium text-cyan-300 bg-cyan-950/80 px-1.5 py-0.5 rounded border border-cyan-800/60 animate-pulse">
              <RefreshCw className="w-3 h-3 animate-spin" /> Running
            </span>
          )}
          {nodeData.status === 'failed' && (
            <span className="flex items-center gap-1 text-[10px] font-mono font-medium text-rose-400 bg-rose-950/80 px-1.5 py-0.5 rounded border border-rose-800/60">
              <AlertTriangle className="w-3 h-3" /> Failed
            </span>
          )}
          {nodeData.status === 'queued' && (
            <span className="flex items-center gap-1 text-[10px] font-mono font-medium text-amber-400 bg-amber-950/80 px-1.5 py-0.5 rounded border border-amber-800/60">
              <Clock className="w-3 h-3" /> Queued
            </span>
          )}
          {nodeData.status === 'idle' && (
            <span className="text-[10px] font-mono text-slate-400 bg-slate-800/80 px-1.5 py-0.5 rounded">
              Ready
            </span>
          )}
        </div>
      </div>

      {/* Live Running Progress Bar */}
      {nodeData.status === 'running' && (
        <div className="px-3 pt-2 pb-1 space-y-1 bg-cyan-950/20 border-b border-cyan-800/30">
          <div className="flex items-center justify-between text-[10px] font-mono text-cyan-300">
            <span>{nodeData.progressLabel || 'Processing worker stage...'}</span>
            <span>{nodeData.progressPercent || 65}%</span>
          </div>
          <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-cyan-400 rounded-full animate-pulse transition-all duration-300"
              style={{ width: `${nodeData.progressPercent || 65}%` }}
            />
          </div>
        </div>
      )}

      {/* Inline Asset Thumbnail Preview if generated */}
      {nodeData.thumbnailUrl && (
        <div className="relative h-24 w-full bg-slate-950 border-b border-slate-800/80 overflow-hidden group/thumb">
          <img
            src={nodeData.thumbnailUrl}
            alt={nodeData.title}
            className="w-full h-full object-cover transition-transform duration-300 group-hover/thumb:scale-105"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-slate-950/80 via-transparent to-transparent flex items-end p-2 justify-between">
            <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-black/70 text-slate-200 border border-white/10 backdrop-blur-sm">
              Live Preview
            </span>
            <span className="text-[9px] font-mono text-cyan-300 flex items-center gap-1">
              <Eye className="w-3 h-3" /> Inspect
            </span>
          </div>
        </div>
      )}

      {/* Inline Text / Snippet Preview if available */}
      {nodeData.outputSnippet && (
        <div className="px-3 py-1.5 bg-slate-950/60 border-b border-slate-800/80 text-[10px] font-mono text-slate-300 line-clamp-2">
          &quot;{nodeData.outputSnippet}&quot;
        </div>
      )}

      {/* Warning / Intervention Notice */}
      {nodeData.warningMessage && (
        <div className="px-3 py-1.5 bg-amber-950/40 border-b border-amber-800/40 flex items-center justify-between text-[10px] font-mono text-amber-300">
          <span className="truncate pr-1 flex items-center gap-1">
            <ShieldAlert className="w-3 h-3 flex-shrink-0" />
            {nodeData.warningMessage}
          </span>
          <button
            onClick={handleIntervene}
            className="px-1.5 py-0.5 rounded bg-amber-500/20 hover:bg-amber-500/40 border border-amber-500/60 text-amber-200 whitespace-nowrap"
          >
            Review
          </button>
        </div>
      )}

      {/* Node Body Details */}
      <div className="p-3 text-[11px] space-y-1.5">
        <div className="flex items-center justify-between text-slate-400">
          <span>Model / Engine:</span>
          <span className="font-mono text-slate-200">{nodeData.model || 'Deterministic'}</span>
        </div>

        {nodeData.costEstimate !== undefined && (
          <div className="flex items-center justify-between text-slate-400">
            <span>Est. Cost:</span>
            <span className="font-mono text-slate-200">
              {nodeData.costEstimate === 'unknown' ? (
                <span className="text-amber-400 px-1 py-0.2 rounded bg-amber-950/50 border border-amber-800/40 text-[10px]">
                  unknown
                </span>
              ) : (
                `$${nodeData.costEstimate.toFixed(3)}`
              )}
            </span>
          </div>
        )}

        {nodeData.lastAttempt && nodeData.lastAttempt > 1 && (
          <div className="flex items-center justify-between text-rose-400 font-mono text-[10px] bg-rose-950/40 px-2 py-0.5 rounded border border-rose-900/50">
            <span>Attempt #{nodeData.lastAttempt}</span>
            <span>Fallback GPU Applied</span>
          </div>
        )}
      </div>

      {/* Hover Quick Action Strip */}
      <div className="px-3 py-1.5 bg-slate-950/80 border-t border-slate-800 flex items-center justify-between text-[10px] font-mono text-slate-400">
        <button
          onClick={handleRerun}
          className="hover:text-cyan-300 transition-colors flex items-center gap-1"
          title="Rerun pipeline from this checkpoint"
        >
          <RotateCcw className="w-3 h-3" />
          Rerun Node
        </button>
        <span className="text-slate-600">•</span>
        {(nodeData.id === 'node_image_gen' || nodeData.executor === 'ComfyImageWorker') ? (
          <button
            onClick={(e) => {
              e.stopPropagation();
              if (typeof window !== 'undefined') {
                window.dispatchEvent(new CustomEvent('open-comfy-subcanvas'));
              }
            }}
            className="text-cyan-300 hover:text-cyan-200 hover:underline transition-colors flex items-center gap-1 font-semibold"
            title="Open ComfyUI Micro-Graph Sub-Canvas (Tier 2)"
          >
            <Sparkles className="w-3 h-3 text-cyan-400" />
            Sub-Canvas ⚡
          </button>
        ) : (
          <button
            onClick={handleIntervene}
            className="hover:text-amber-300 transition-colors flex items-center gap-1"
            title="Tweak prompt or parameters"
          >
            <Sparkles className="w-3 h-3" />
            Tweak
          </button>
        )}
      </div>

      {/* Output Handles */}
      <div className="relative">
        {nodeData.outputs?.map((output, idx) => {
          const topPercent = ((idx + 1) / (nodeData.outputs.length + 1)) * 100;
          return (
            <Handle
              key={output.id}
              type="source"
              position={Position.Right}
              id={output.id}
              className={cn(
                '!w-3.5 !h-3.5 rounded-full border-2 border-slate-950 shadow-sm transition-transform hover:scale-125 z-10',
                PORT_COLORS[output.type] || '!bg-slate-400'
              )}
              style={{ top: `${topPercent}%` }}
              title={`Out: ${output.label} (${output.type})`}
            />
          );
        })}
      </div>
    </div>
  );
});

CustomNode.displayName = 'CustomNode';
