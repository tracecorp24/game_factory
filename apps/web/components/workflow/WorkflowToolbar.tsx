'use client';

import React from 'react';
import {
  Play,
  Pause,
  Square,
  CheckCircle2,
  AlertCircle,
  Sparkles,
  Layers,
  Smartphone,
  GitFork,
  Kanban,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useAppStore } from '@/lib/store';

interface WorkflowToolbarProps {
  onValidate: () => void;
  onDryRun: () => void;
  onRun: () => void;
  onPause: () => void;
  onCancel: () => void;
  onLoadTemplate: (templateName: string) => void;
  validationErrors: string[];
  viewMode: 'canvas' | 'swimlane';
  onViewModeChange: (mode: 'canvas' | 'swimlane') => void;
  showDeviceEmulator: boolean;
  onToggleDeviceEmulator: () => void;
  onOpenComfySubCanvas?: () => void;
}

export function WorkflowToolbar({
  onValidate,
  onDryRun,
  onRun,
  onPause,
  onCancel,
  onLoadTemplate,
  validationErrors,
  viewMode,
  onViewModeChange,
  showDeviceEmulator,
  onToggleDeviceEmulator,
  onOpenComfySubCanvas,
}: WorkflowToolbarProps) {
  const { workflowVersion, workflowStatus } = useAppStore();

  return (
    <div className="h-14 border-b border-slate-800 bg-[#070b14]/90 backdrop-blur-md px-4 flex items-center justify-between z-10 select-none">
      {/* Left: Version, View Switcher & Template Selector */}
      <div className="flex items-center gap-3">
        {/* Workflow Version Badge */}
        <div className="flex items-center gap-2 px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono">
          <Layers className="w-3.5 h-3.5 text-cyan-400" />
          <span className="text-slate-400">Version:</span>
          <span className="text-cyan-300 font-semibold">{workflowVersion}</span>
        </div>

        {/* View Mode Switcher: DAG Canvas vs Factory Swimlane */}
        <div className="flex items-center rounded-lg bg-slate-900 p-0.5 border border-slate-800 text-xs font-mono">
          <button
            onClick={() => onViewModeChange('canvas')}
            className={cn(
              'px-2.5 py-1 rounded-md transition-all flex items-center gap-1.5',
              viewMode === 'canvas'
                ? 'bg-cyan-500/20 text-cyan-300 font-semibold shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            )}
            title="React Flow Node DAG View"
          >
            <GitFork className="w-3.5 h-3.5" />
            <span>DAG Canvas</span>
          </button>

          <button
            onClick={() => onViewModeChange('swimlane')}
            className={cn(
              'px-2.5 py-1 rounded-md transition-all flex items-center gap-1.5',
              viewMode === 'swimlane'
                ? 'bg-purple-500/20 text-purple-300 font-semibold shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            )}
            title="Horizontal Factory Floor Concurrency Swimlanes"
          >
            <Kanban className="w-3.5 h-3.5" />
            <span>Factory Swimlane</span>
          </button>
        </div>

        {/* Template Presets Dropdown */}
        <div className="hidden lg:flex items-center gap-1.5 text-xs">
          <span className="text-slate-500 font-mono text-[11px]">Template:</span>
          <select
            onChange={(e) => onLoadTemplate(e.target.value)}
            className="bg-slate-900 border border-slate-800 rounded-md px-2.5 py-1 text-xs text-slate-200 focus:outline-none focus:border-cyan-500 font-mono"
            defaultValue="Full Campaign"
          >
            <option value="Full Campaign">Full Campaign 360 (Image, Video, Playable)</option>
            <option value="Trend Concept Mockup">Trend → Concept → Mockup</option>
            <option value="Selected Concept Static Ad">Selected Concept → Static Ad</option>
            <option value="Selected Concept Video Ad">Selected Concept → Video Ad</option>
            <option value="Selected Concept Basic Playable">Selected Concept → Basic Playable</option>
          </select>
        </div>

        {/* Validation Errors Notice */}
        {validationErrors.length > 0 && (
          <div className="flex items-center gap-1.5 text-rose-400 text-xs font-mono px-2 py-0.5 rounded bg-rose-950/60 border border-rose-800/50">
            <AlertCircle className="w-3.5 h-3.5" />
            <span>{validationErrors.length} Errors</span>
          </div>
        )}
      </div>

      {/* Right: Device Emulator & Actions (Validate, Dry Run, Run, Pause, Cancel) */}
      <div className="flex items-center gap-2">
        {/* Docked Mobile Safe-Zone Emulator Toggle */}
        <button
          onClick={onToggleDeviceEmulator}
          className={cn(
            'px-3 py-1.5 rounded-lg border text-xs font-mono transition-all flex items-center gap-1.5',
            showDeviceEmulator
              ? 'bg-cyan-950 text-cyan-300 border-cyan-500/60 font-semibold shadow-sm shadow-cyan-500/20'
              : 'border-slate-800 bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-slate-200'
          )}
          title="Open Live Device Emulator with TikTok Safe-Zone Overlay"
        >
          <Smartphone className="w-3.5 h-3.5 text-cyan-400" />
          <span className="hidden sm:inline">Device Emulator</span>
        </button>

        {/* ComfyUI Sub-Canvas Modal Trigger */}
        {onOpenComfySubCanvas && (
          <button
            onClick={onOpenComfySubCanvas}
            className="px-3 py-1.5 rounded-lg border border-cyan-800/80 bg-cyan-950/60 hover:bg-cyan-900/80 text-cyan-300 text-xs font-mono font-medium transition-all flex items-center gap-1.5 shadow-sm shadow-cyan-950"
            title="Open ComfyUI Micro-Graph Sub-Canvas (Tier 2)"
          >
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
            <span className="hidden sm:inline">Comfy Sub-Canvas</span>
          </button>
        )}

        <span className="text-slate-700 hidden sm:inline">|</span>

        {/* Validate */}
        <button
          onClick={onValidate}
          className="px-3 py-1.5 rounded-lg border border-slate-700 bg-slate-900 hover:bg-slate-800 text-slate-200 text-xs font-medium transition-colors hidden sm:flex items-center gap-1.5"
          title="Type Check Edge Ports and Cycle Prevention"
        >
          <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400" />
          Validate
        </button>

        {/* Dry Run */}
        <button
          onClick={onDryRun}
          className="px-3 py-1.5 rounded-lg border border-slate-700 bg-slate-900 hover:bg-slate-800 text-slate-200 text-xs font-medium transition-colors hidden sm:flex items-center gap-1.5"
          title="Verify Models, Token Quotas and DAG Toposort without Executing"
        >
          <Sparkles className="w-3.5 h-3.5 text-amber-400" />
          Dry Run
        </button>

        {/* Run Workflow */}
        <button
          onClick={onRun}
          disabled={workflowStatus === 'running'}
          className={cn(
            'px-4 py-1.5 rounded-lg text-white text-xs font-semibold shadow-md transition-all flex items-center gap-1.5',
            workflowStatus === 'running'
              ? 'bg-cyan-900 text-cyan-300 cursor-not-allowed opacity-70'
              : 'bg-gradient-to-r from-cyan-500 to-blue-600 hover:shadow-cyan-500/30 hover:scale-[1.02]'
          )}
        >
          <Play className="w-3.5 h-3.5 fill-current" />
          Run
        </button>

        {/* Pause */}
        <button
          onClick={onPause}
          disabled={workflowStatus !== 'running'}
          className="p-1.5 rounded-lg border border-slate-800 bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-slate-200 text-xs transition-colors disabled:opacity-40"
          title="Pause Workflow Execution"
        >
          <Pause className="w-4 h-4" />
        </button>

        {/* Cancel */}
        <button
          onClick={onCancel}
          disabled={workflowStatus === 'idle' || workflowStatus === 'completed'}
          className="p-1.5 rounded-lg border border-slate-800 bg-slate-900 hover:bg-rose-950/60 text-slate-400 hover:text-rose-400 text-xs transition-colors disabled:opacity-40"
          title="Cancel Execution"
        >
          <Square className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
