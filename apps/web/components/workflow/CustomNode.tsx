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
  text: '!bg-[#5de6ff] !border-[#0a0d14]',
  concept_spec: '!bg-[#0a84ff] !border-[#0a0d14]',
  image: '!bg-[#bf5af2] !border-[#0a0d14]',
  video: '!bg-[#ff9f0a] !border-[#0a0d14]',
  code: '!bg-[#30d158] !border-[#0a0d14]',
  eval_report: '!bg-[#ff453a] !border-[#0a0d14]',
  manifest: '!bg-[#5e5ce6] !border-[#0a0d14]',
  trigger: '!bg-[#8e8e93] !border-[#0a0d14]',
};

const CATEGORY_STYLES: Record<string, { bg: string; text: string; iconBg: string }> = {
  'Market Intelligence': { bg: 'bg-[#5de6ff]/10', text: 'text-[#5de6ff]', iconBg: 'bg-[#5de6ff]/15' },
  'Game DNA': { bg: 'bg-[#bf5af2]/10', text: 'text-[#bf5af2]', iconBg: 'bg-[#bf5af2]/15' },
  'Ideation': { bg: 'bg-[#0a84ff]/10', text: 'text-[#0a84ff]', iconBg: 'bg-[#0a84ff]/15' },
  'Generation': { bg: 'bg-[#ff9f0a]/10', text: 'text-[#ff9f0a]', iconBg: 'bg-[#ff9f0a]/15' },
  'Evaluation': { bg: 'bg-[#ff453a]/10', text: 'text-[#ff453a]', iconBg: 'bg-[#ff453a]/15' },
  'Control': { bg: 'bg-white/[0.05]', text: 'text-neutral-400', iconBg: 'bg-white/[0.08]' },
  'Export': { bg: 'bg-[#30d158]/10', text: 'text-[#30d158]', iconBg: 'bg-[#30d158]/15' },
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
        'w-72 rounded-2xl bg-[#121724]/90 backdrop-blur-2xl border transition-all duration-200 select-none overflow-hidden relative group',
        selected
          ? 'border-apple-blue ring-2 ring-apple-blue/40 shadow-apple-glow scale-[1.01]'
          : 'border-white/[0.08] hover:border-white/[0.18] shadow-apple-md',
        nodeData.status === 'running' && 'border-apple-teal/60 ring-1 ring-apple-teal/40',
        nodeData.status === 'failed' && 'border-apple-red/60 shadow-apple-red/20'
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
                '!w-3 !h-3 rounded-full border-2 border-[#0a0d14] shadow-sm transition-transform hover:scale-125 z-10',
                PORT_COLORS[input.type] || '!bg-neutral-400'
              )}
              style={{ top: `${topPercent}%` }}
              title={`In: ${input.label} (${input.type})`}
            />
          );
        })}
      </div>

      {/* Node Header */}
      <div className={cn('px-3.5 py-2.5 border-b border-white/[0.06] flex items-center justify-between', catStyle.bg)}>
        <div className="flex items-center gap-2.5 min-w-0">
          <div className={cn('w-6 h-6 rounded-lg flex items-center justify-center flex-shrink-0', catStyle.iconBg)}>
            <Cpu className={cn('w-3.5 h-3.5', catStyle.text)} />
          </div>
          <div className="min-w-0">
            <div className="text-xs font-semibold text-neutral-100 tracking-tight truncate">{nodeData.title}</div>
            <div className="text-[10px] font-mono text-neutral-400 truncate">{nodeData.executor}</div>
          </div>
        </div>

        {/* Apple Style Status Pill */}
        <div>
          {nodeData.status === 'completed' && (
            <span className="flex items-center gap-1 text-[10px] font-mono font-medium text-apple-emerald bg-apple-emerald/10 px-2 py-0.5 rounded-full border border-apple-emerald/25">
              <span className="w-1.5 h-1.5 rounded-full bg-apple-emerald" /> Done
            </span>
          )}
          {nodeData.status === 'running' && (
            <span className="flex items-center gap-1 text-[10px] font-mono font-medium text-apple-teal bg-apple-teal/10 px-2 py-0.5 rounded-full border border-apple-teal/30">
              <span className="w-1.5 h-1.5 rounded-full bg-apple-teal animate-pulse" /> Running
            </span>
          )}
          {nodeData.status === 'failed' && (
            <span className="flex items-center gap-1 text-[10px] font-mono font-medium text-apple-red bg-apple-red/10 px-2 py-0.5 rounded-full border border-apple-red/25">
              <span className="w-1.5 h-1.5 rounded-full bg-apple-red" /> Failed
            </span>
          )}
          {nodeData.status === 'queued' && (
            <span className="flex items-center gap-1 text-[10px] font-mono font-medium text-apple-amber bg-apple-amber/10 px-2 py-0.5 rounded-full border border-apple-amber/25">
              <Clock className="w-2.5 h-2.5" /> Queued
            </span>
          )}
          {nodeData.status === 'idle' && (
            <span className="text-[10px] font-mono text-neutral-400 bg-white/[0.05] px-2 py-0.5 rounded-full border border-white/[0.06]">
              Ready
            </span>
          )}
        </div>
      </div>

      {/* Live Running Progress Bar */}
      {nodeData.status === 'running' && (
        <div className="px-3 pt-2 pb-1.5 space-y-1 bg-apple-blue/5 border-b border-apple-blue/15">
          <div className="flex items-center justify-between text-[10px] font-mono text-apple-teal">
            <span>{nodeData.progressLabel || 'Worker stage processing...'}</span>
            <span>{nodeData.progressPercent || 65}%</span>
          </div>
          <div className="h-1.5 w-full bg-neutral-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-apple-teal rounded-full transition-all duration-300"
              style={{ width: `${nodeData.progressPercent || 65}%` }}
            />
          </div>
        </div>
      )}

      {/* Inline Asset Thumbnail Preview */}
      {nodeData.thumbnailUrl && (
        <div className="relative h-24 w-full bg-black/40 border-b border-white/[0.06] overflow-hidden group/thumb">
          <img
            src={nodeData.thumbnailUrl}
            alt={nodeData.title}
            className="w-full h-full object-cover transition-transform duration-300 group-hover/thumb:scale-105"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent flex items-end p-2 justify-between">
            <span className="text-[9px] font-mono px-1.5 py-0.5 rounded-full bg-black/60 text-neutral-300 border border-white/10 backdrop-blur-md">
              Artifact
            </span>
            <span className="text-[9px] font-mono text-apple-teal flex items-center gap-1">
              <Eye className="w-3 h-3" /> Inspect
            </span>
          </div>
        </div>
      )}

      {/* Inline Text / Snippet Preview */}
      {nodeData.outputSnippet && (
        <div className="px-3 py-1.5 bg-black/20 border-b border-white/[0.06] text-[10px] font-mono text-neutral-300 line-clamp-2">
          &quot;{nodeData.outputSnippet}&quot;
        </div>
      )}

      {/* Warning / Intervention Notice */}
      {nodeData.warningMessage && (
        <div className="px-3 py-1.5 bg-apple-amber/10 border-b border-apple-amber/25 flex items-center justify-between text-[10px] font-mono text-apple-amber">
          <span className="truncate pr-1 flex items-center gap-1.5">
            <ShieldAlert className="w-3 h-3 flex-shrink-0" />
            {nodeData.warningMessage}
          </span>
          <button
            onClick={handleIntervene}
            className="px-2 py-0.5 rounded-full bg-apple-amber/20 hover:bg-apple-amber/30 border border-apple-amber/40 text-neutral-100 whitespace-nowrap text-[9px] font-sans font-medium transition-colors"
          >
            Review
          </button>
        </div>
      )}

      {/* Node Body Details */}
      <div className="p-3 text-[11px] space-y-1.5">
        <div className="flex items-center justify-between text-neutral-400">
          <span>Engine:</span>
          <span className="font-mono text-neutral-200">{nodeData.model || 'Deterministic'}</span>
        </div>

        {nodeData.costEstimate !== undefined && (
          <div className="flex items-center justify-between text-neutral-400">
            <span>Est. Cost:</span>
            <span className="font-mono text-neutral-200">
              {nodeData.costEstimate === 'unknown' ? (
                <span className="text-apple-amber px-1.5 py-0.2 rounded-full bg-apple-amber/10 border border-apple-amber/20 text-[10px]">
                  media quote
                </span>
              ) : (
                `$${nodeData.costEstimate.toFixed(3)}`
              )}
            </span>
          </div>
        )}

        {nodeData.lastAttempt && nodeData.lastAttempt > 1 && (
          <div className="flex items-center justify-between text-apple-red font-mono text-[10px] bg-apple-red/10 px-2 py-0.5 rounded-lg border border-apple-red/20">
            <span>Attempt #{nodeData.lastAttempt}</span>
            <span>Fallback Applied</span>
          </div>
        )}
      </div>

      {/* Hover Quick Action Strip */}
      <div className="px-3 py-1.5 bg-black/25 border-t border-white/[0.06] flex items-center justify-between text-[10px] font-mono text-neutral-400">
        <button
          onClick={handleRerun}
          className="hover:text-apple-teal transition-colors flex items-center gap-1"
          title="Rerun pipeline from this checkpoint"
        >
          <RotateCcw className="w-3 h-3" />
          Rerun
        </button>
        <span className="text-neutral-700">•</span>
        {(nodeData.id === 'node_image_gen' || nodeData.executor === 'ComfyImageWorker') ? (
          <button
            onClick={(e) => {
              e.stopPropagation();
              if (typeof window !== 'undefined') {
                window.dispatchEvent(new CustomEvent('open-comfy-subcanvas'));
              }
            }}
            className="text-apple-purple hover:text-apple-purple/80 transition-colors flex items-center gap-1 font-semibold"
            title="Open ComfyUI Micro-Graph Sub-Canvas (Tier 2)"
          >
            <Sparkles className="w-3 h-3 text-apple-purple" />
            Comfy Sub-Canvas
          </button>
        ) : (
          <button
            onClick={handleIntervene}
            className="hover:text-apple-amber transition-colors flex items-center gap-1"
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
                '!w-3 !h-3 rounded-full border-2 border-[#0a0d14] shadow-sm transition-transform hover:scale-125 z-10',
                PORT_COLORS[output.type] || '!bg-neutral-400'
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
