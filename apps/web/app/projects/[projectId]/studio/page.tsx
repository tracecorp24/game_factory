'use client';

import React from 'react';
import { useSearchParams, useRouter, useParams } from 'next/navigation';
import { GitFork, Radio, Sparkles } from 'lucide-react';
import { WorkflowCanvas } from '@/components/workflow/WorkflowCanvas';
import { AgentGalaxy } from '@/components/observatory/AgentGalaxy';
import { cn } from '@/lib/utils';
import { useAppStore } from '@/lib/store';

export default function StudioPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const params = useParams();
  const projectId = (params?.projectId as string) || 'prj_match3_hero';

  const tab = searchParams.get('tab') || 'workflow';
  const { runStatus, activeRunId } = useAppStore();

  const handleTabChange = (newTab: 'workflow' | 'agents') => {
    router.push(`/projects/${projectId}/studio?tab=${newTab}${newTab === 'agents' ? `&run=${activeRunId}` : ''}`);
  };

  return (
    <div className="flex flex-col h-full overflow-hidden bg-[#090d16]">
      {/* Studio Top Navigation Bar */}
      <div className="h-12 border-b border-slate-800 bg-[#070b14] px-6 flex items-center justify-between z-20 select-none">
        <div className="flex items-center gap-1 bg-slate-900 p-1 rounded-lg border border-slate-800">
          <button
            onClick={() => handleTabChange('workflow')}
            className={cn(
              'px-3.5 py-1 text-xs font-medium rounded-md transition-all flex items-center gap-2',
              tab === 'workflow'
                ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-sm shadow-cyan-500/20'
                : 'text-slate-400 hover:text-slate-200'
            )}
          >
            <GitFork className="w-3.5 h-3.5" />
            <span>Workflow Studio</span>
            <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-black/20">Canvas</span>
          </button>

          <button
            onClick={() => handleTabChange('agents')}
            className={cn(
              'px-3.5 py-1 text-xs font-medium rounded-md transition-all flex items-center gap-2',
              tab === 'agents'
                ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-sm shadow-purple-500/20'
                : 'text-slate-400 hover:text-slate-200'
            )}
          >
            <Radio className="w-3.5 h-3.5" />
            <span>Agent Observatory</span>
            <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-emerald-950 text-emerald-300 border border-emerald-800/60 flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
              Live
            </span>
          </button>
        </div>

        {/* Status Pill */}
        <div className="hidden sm:flex items-center gap-2 font-mono text-xs text-slate-400">
          <span>Active Run:</span>
          <span className="text-cyan-300 font-semibold">{activeRunId}</span>
          <span className="text-slate-600">•</span>
          <span className="text-emerald-400 font-semibold">{runStatus.toUpperCase()}</span>
        </div>
      </div>

      {/* Main Tab Content */}
      <div className="flex-1 min-h-0 overflow-hidden">
        {tab === 'workflow' ? <WorkflowCanvas /> : <AgentGalaxy />}
      </div>
    </div>
  );
}
