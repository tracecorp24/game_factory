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
  ChevronDown,
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
    <div className="h-13 border-b border-white/[0.06] bg-[#0c101a]/70 backdrop-blur-2xl px-4 py-2 flex items-center justify-between z-10 select-none">
      {/* Left: Version & Apple Segmented View Switcher */}
      <div className="flex items-center gap-3">
        {/* Version Capsule */}
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-white/[0.04] border border-white/[0.07] text-[11px] font-mono text-neutral-400">
          <Layers className="w-3 h-3 text-apple-blue" />
          <span>v{workflowVersion}</span>
        </div>

        {/* Apple Segmented Switcher: DAG Canvas vs Factory Swimlane */}
        <div className="apple-segmented">
          <button
            onClick={() => onViewModeChange('canvas')}
            className={cn(
              'apple-segmented-item flex items-center gap-1.5',
              viewMode === 'canvas' && 'apple-segmented-item-active'
            )}
            title="React Flow Node DAG View"
          >
            <GitFork className="w-3.5 h-3.5" />
            <span>DAG Canvas</span>
          </button>

          <button
            onClick={() => onViewModeChange('swimlane')}
            className={cn(
              'apple-segmented-item flex items-center gap-1.5',
              viewMode === 'swimlane' && 'apple-segmented-item-active'
            )}
            title="Horizontal Factory Floor Concurrency Swimlanes"
          >
            <Kanban className="w-3.5 h-3.5" />
            <span>Factory Swimlane</span>
          </button>
        </div>

        {/* Template Presets Picker */}
        <div className="hidden lg:flex items-center gap-2">
          <div className="relative">
            <select
              onChange={(e) => onLoadTemplate(e.target.value)}
              className="bg-white/[0.04] hover:bg-white/[0.07] border border-white/[0.08] rounded-lg px-2.5 py-1 text-xs text-neutral-200 focus:outline-none focus:border-apple-blue font-sans cursor-pointer transition-colors pr-7 appearance-none"
              defaultValue="Full Campaign"
            >
              <option value="Full Campaign" className="bg-[#121724] text-neutral-200">Full Campaign 360 (Image, Video, Playable)</option>
              <option value="Trend Concept Mockup" className="bg-[#121724] text-neutral-200">Trend → Concept → Mockup</option>
              <option value="Selected Concept Static Ad" className="bg-[#121724] text-neutral-200">Selected Concept → Static Ad</option>
              <option value="Selected Concept Video Ad" className="bg-[#121724] text-neutral-200">Selected Concept → Video Ad</option>
              <option value="Selected Concept Basic Playable" className="bg-[#121724] text-neutral-200">Selected Concept → Basic Playable</option>
            </select>
            <ChevronDown className="w-3 h-3 text-neutral-500 absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none" />
          </div>
        </div>

        {/* Validation Errors Notice */}
        {validationErrors.length > 0 && (
          <div className="flex items-center gap-1.5 text-apple-red text-xs font-mono px-2 py-0.5 rounded-full bg-apple-red/10 border border-apple-red/25">
            <AlertCircle className="w-3 h-3" />
            <span>{validationErrors.length} Issue{validationErrors.length > 1 ? 's' : ''}</span>
          </div>
        )}
      </div>

      {/* Right: Actions Hierarchy (Secondary Tools + Primary Action) */}
      <div className="flex items-center gap-2">
        {/* Device Emulator Toggle */}
        <button
          onClick={onToggleDeviceEmulator}
          className={cn(
            'px-2.5 py-1.5 rounded-lg border text-xs font-medium transition-all flex items-center gap-1.5',
            showDeviceEmulator
              ? 'bg-apple-blue/15 text-apple-blue border-apple-blue/30 font-semibold shadow-sm'
              : 'border-white/[0.08] bg-white/[0.04] hover:bg-white/[0.08] text-neutral-300'
          )}
          title="Open Live Device Emulator with TikTok Safe-Zone Overlay"
        >
          <Smartphone className="w-3.5 h-3.5 text-apple-teal" />
          <span className="hidden sm:inline">Preview Emulator</span>
        </button>

        {/* ComfyUI Sub-Canvas Modal Trigger */}
        {onOpenComfySubCanvas && (
          <button
            onClick={onOpenComfySubCanvas}
            className="px-2.5 py-1.5 rounded-lg border border-apple-purple/30 bg-apple-purple/10 hover:bg-apple-purple/20 text-apple-purple text-xs font-medium transition-all flex items-center gap-1.5"
            title="Open ComfyUI Micro-Graph Sub-Canvas (Tier 2)"
          >
            <Sparkles className="w-3.5 h-3.5 text-apple-purple" />
            <span className="hidden sm:inline">Comfy Sub-Canvas</span>
          </button>
        )}

        <div className="w-[1px] h-5 bg-white/[0.08] mx-1 hidden sm:block" />

        {/* Validate DAG */}
        <button
          onClick={onValidate}
          className="apple-btn-secondary hidden sm:flex items-center gap-1.5"
          title="Type Check Edge Ports and Cycle Prevention"
        >
          <CheckCircle2 className="w-3.5 h-3.5 text-neutral-400" />
          Validate
        </button>

        {/* Dry Run */}
        <button
          onClick={onDryRun}
          className="apple-btn-secondary hidden sm:flex items-center gap-1.5"
          title="Verify Models, Token Quotas and DAG Toposort without Executing"
        >
          <Sparkles className="w-3.5 h-3.5 text-apple-amber" />
          Dry Run
        </button>

        {/* Primary Action: Run Workflow */}
        <button
          onClick={onRun}
          disabled={workflowStatus === 'running'}
          className={cn(
            'apple-btn-primary flex items-center gap-1.5',
            workflowStatus === 'running' && 'opacity-60 cursor-not-allowed'
          )}
        >
          <Play className="w-3.5 h-3.5 fill-current" />
          <span>{workflowStatus === 'running' ? 'Running...' : 'Run Pipeline'}</span>
        </button>

        {/* Pause & Cancel Controls */}
        <div className="flex items-center gap-1 bg-white/[0.04] p-0.5 rounded-lg border border-white/[0.08]">
          <button
            onClick={onPause}
            disabled={workflowStatus !== 'running'}
            className="p-1 rounded-md text-neutral-400 hover:text-neutral-200 hover:bg-white/[0.08] transition-colors disabled:opacity-30"
            title="Pause Execution"
          >
            <Pause className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={onCancel}
            disabled={workflowStatus === 'idle' || workflowStatus === 'completed'}
            className="p-1 rounded-md text-neutral-400 hover:text-apple-red hover:bg-apple-red/10 transition-colors disabled:opacity-30"
            title="Cancel Execution"
          >
            <Square className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
}
