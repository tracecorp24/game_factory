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
    <div className="flex flex-col h-full overflow-hidden bg-[#0a0d14]">
      {/* Studio Top Navigation Bar */}
      <div className="h-12 border-b border-white/[0.06] bg-[#0c101a]/70 backdrop-blur-2xl px-5 flex items-center justify-between z-20 select-none">
        <div className="apple-segmented">
          <button
            onClick={() => handleTabChange('workflow')}
            className={cn(
              'apple-segmented-item flex items-center gap-2',
              tab === 'workflow' && 'apple-segmented-item-active'
            )}
          >
            <GitFork className="w-3.5 h-3.5" />
            <span>Workflow Studio</span>
            <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-white/[0.08] text-neutral-300">DAG</span>
          </button>

          <button
            onClick={() => handleTabChange('agents')}
            className={cn(
              'apple-segmented-item flex items-center gap-2',
              tab === 'agents' && 'apple-segmented-item-active'
            )}
          >
            <Radio className="w-3.5 h-3.5" />
            <span>Agent Observatory</span>
            <span className="text-[10px] font-mono px-1.5 py-0.2 rounded-full bg-apple-emerald/15 text-apple-emerald flex items-center gap-1 font-semibold">
              <span className="w-1.5 h-1.5 rounded-full bg-apple-emerald animate-pulse" />
              Live
            </span>
          </button>
        </div>

        {/* Status Capsule */}
        <div className="hidden sm:flex items-center gap-2 font-mono text-xs text-neutral-400 bg-white/[0.03] px-3 py-1 rounded-full border border-white/[0.06]">
          <span>Run:</span>
          <span className="text-apple-teal font-medium">{activeRunId}</span>
          <span className="text-neutral-600">•</span>
          <span className="text-apple-emerald font-semibold uppercase text-[11px]">{runStatus}</span>
        </div>
      </div>

      {/* Main Tab Content */}
      <div className="flex-1 min-h-0 overflow-hidden">
        {tab === 'workflow' ? <WorkflowCanvas /> : <AgentGalaxy />}
      </div>
    </div>
  );
}
