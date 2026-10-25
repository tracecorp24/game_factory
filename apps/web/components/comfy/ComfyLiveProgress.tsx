// CreativeForge Intelligence Studio v3.0 - ComfyUI Deep Hybrid Integration
// components/comfy/ComfyLiveProgress.tsx

'use client';

import React from 'react';
import {
  Play,
  RotateCcw,
  CheckCircle2,
  AlertCircle,
  Eye,
  Activity,
  Layers,
  Sparkles,
  Download,
} from 'lucide-react';
import { ComfyLiveEvent } from '@/lib/comfy/types';
import { cn } from '@/lib/utils';

interface ComfyLiveProgressProps {
  currentEvent: ComfyLiveEvent | null;
  isExecuting: boolean;
  onTriggerTestRun: () => void;
  onStopRun: () => void;
  outputPreviewUrl: string | null;
}

export function ComfyLiveProgress({
  currentEvent,
  isExecuting,
  onTriggerTestRun,
  onStopRun,
  outputPreviewUrl,
}: ComfyLiveProgressProps) {
  const step = currentEvent?.step || 0;
  const totalSteps = currentEvent?.totalSteps || 25;
  const percentage = currentEvent?.percentage || (isExecuting ? Math.round((step / totalSteps) * 100) : 0);
  const activeNodeId = currentEvent?.nodeId || (isExecuting ? '3' : null);
  const isCompleted = currentEvent?.type === 'done' || (!isExecuting && !!outputPreviewUrl);
  const isError = currentEvent?.type === 'execution_error';

  return (
    <div className="flex flex-col gap-3 p-4 bg-[#070b14] border-t border-slate-800 select-none">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-cyan-400" />
          <span className="text-xs font-semibold text-slate-200 uppercase tracking-wider font-mono">
            ComfyUI Live Execution & Latent Stream
          </span>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2">
          {isExecuting ? (
            <button
              onClick={onStopRun}
              className="flex items-center gap-1.5 px-3 py-1 text-xs font-semibold rounded bg-rose-600 hover:bg-rose-500 text-white transition-colors"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Abort Execution</span>
            </button>
          ) : (
            <button
              onClick={onTriggerTestRun}
              className="flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-semibold rounded-md bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white shadow-lg shadow-cyan-950 transition-all font-mono"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>Test Render Workflow</span>
            </button>
          )}
        </div>
      </div>

      {/* Main Grid: Progress Metrics + Live Latent Frame Preview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
        {/* Left: Progress Status & Steps */}
        <div className="md:col-span-2 space-y-2">
          <div className="flex items-center justify-between text-xs font-mono">
            <div className="flex items-center gap-2">
              <span className="text-slate-400">Current Phase:</span>
              <span className="text-cyan-300 font-semibold">
                {isExecuting
                  ? `Node #${activeNodeId} (KSampler Denoising)`
                  : isCompleted
                  ? 'Render Completed (VAE Decoded)'
                  : 'Idle (Ready for Execution)'}
              </span>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-slate-400">Progress:</span>
              <span className="text-cyan-400 font-bold">
                {isExecuting ? `Step ${step} / ${totalSteps} (${percentage}%)` : isCompleted ? '100%' : '0%'}
              </span>
            </div>
          </div>

          {/* Step Progress Bar */}
          <div className="w-full bg-slate-900 border border-slate-800 rounded-full h-2.5 overflow-hidden p-0.5">
            <div
              className={cn(
                'h-full rounded-full transition-all duration-150',
                isCompleted
                  ? 'bg-emerald-500 shadow-md shadow-emerald-500/50'
                  : 'bg-gradient-to-r from-cyan-500 via-blue-500 to-indigo-500'
              )}
              style={{ width: `${isCompleted ? 100 : percentage}%` }}
            />
          </div>

          <div className="flex items-center justify-between text-[10px] font-mono text-slate-500">
            <span>Daemon: <span className="text-emerald-400">127.0.0.1:8188 [Active]</span></span>
            <span>VRAM: <span className="text-slate-300">6.4 GB / 12.0 GB (Peak)</span></span>
            <span>Telemetry: <span className="text-cyan-400">SSE Outbox Stream</span></span>
          </div>

          {isError && (
            <div className="p-2.5 rounded bg-rose-950/60 border border-rose-800/80 text-rose-300 text-xs font-mono flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-rose-400 flex-shrink-0" />
              <span>{currentEvent?.error || 'Execution encountered an unrecoverable node error.'}</span>
            </div>
          )}
        </div>

        {/* Right: Live Preview Box */}
        <div className="flex items-center gap-3 bg-slate-900/60 border border-slate-800 rounded-xl p-2.5">
          <div className="relative w-16 h-16 rounded-lg overflow-hidden bg-black/60 border border-slate-700/80 flex-shrink-0 flex items-center justify-center">
            {outputPreviewUrl || currentEvent?.previewUrl ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={outputPreviewUrl || currentEvent?.previewUrl || ''}
                alt="Latent Preview"
                className="w-full h-full object-cover animate-fade-in"
              />
            ) : (
              <Eye className="w-6 h-6 text-slate-700" />
            )}

            {isExecuting && (
              <div className="absolute inset-0 bg-cyan-900/20 backdrop-blur-[1px] flex items-center justify-center">
                <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
              </div>
            )}
          </div>

          <div className="flex-1 min-w-0">
            <div className="text-xs font-semibold text-slate-200 truncate flex items-center gap-1.5">
              <span>{isCompleted ? 'Render Complete' : isExecuting ? 'Streaming Latent' : 'Preview Target'}</span>
              {isCompleted && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />}
            </div>
            <div className="text-[10px] font-mono text-slate-400 truncate">
              {outputPreviewUrl ? 'VAEDecode: 1024x1024 PNG' : isExecuting ? `Denoise Step ${step}` : 'No render yet'}
            </div>
            {outputPreviewUrl && (
              <a
                href={outputPreviewUrl}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1 text-[10px] text-cyan-400 hover:text-cyan-300 font-mono mt-1"
              >
                <Download className="w-3 h-3" />
                View Fullscreen
              </a>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
