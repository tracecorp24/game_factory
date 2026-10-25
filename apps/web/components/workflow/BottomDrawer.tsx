'use client';

import React, { useState } from 'react';
import {
  ChevronUp,
  ChevronDown,
  Terminal,
  Layers,
  FileCheck,
  ShieldAlert,
  Zap,
  Activity,
  Maximize2,
  Copy,
  Check,
} from 'lucide-react';
import { cn, formatTimestamp, formatTokens } from '@/lib/utils';
import { useAppStore } from '@/lib/store';

export function BottomDrawer() {
  const [isOpen, setIsOpen] = useState(true);
  const [activeTab, setActiveTab] = useState<'queue' | 'logs' | 'artifacts' | 'qa' | 'events' | 'tokens'>('events');
  const [autoScroll, setAutoScroll] = useState(true);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const { events, activeRunId, runStatus } = useAppStore();

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div
      className={cn(
        'border-t border-slate-800 bg-[#070b14]/98 transition-all duration-300 flex flex-col z-20 select-none shadow-2xl',
        isOpen ? 'h-72' : 'h-10'
      )}
    >
      {/* Drawer Bar Header */}
      <div className="h-10 px-4 border-b border-slate-800/80 flex items-center justify-between bg-slate-950/70">
        <div className="flex items-center gap-2">
          {/* Collapse Toggle */}
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="p-1 rounded text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
          >
            {isOpen ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />}
          </button>

          {/* Tabs */}
          <div className="flex items-center gap-1 font-mono text-xs">
            <button
              onClick={() => { setActiveTab('events'); setIsOpen(true); }}
              className={cn(
                'px-2.5 py-1 rounded text-xs transition-colors flex items-center gap-1.5',
                activeTab === 'events' ? 'bg-cyan-500/20 text-cyan-300 font-semibold' : 'text-slate-400 hover:text-slate-200'
              )}
            >
              <Activity className="w-3.5 h-3.5 text-cyan-400" />
              Event Stream ({events.length})
            </button>

            <button
              onClick={() => { setActiveTab('logs'); setIsOpen(true); }}
              className={cn(
                'px-2.5 py-1 rounded text-xs transition-colors flex items-center gap-1.5',
                activeTab === 'logs' ? 'bg-cyan-500/20 text-cyan-300 font-semibold' : 'text-slate-400 hover:text-slate-200'
              )}
            >
              <Terminal className="w-3.5 h-3.5 text-emerald-400" />
              Live Execution Log
            </button>

            <button
              onClick={() => { setActiveTab('artifacts'); setIsOpen(true); }}
              className={cn(
                'px-2.5 py-1 rounded text-xs transition-colors flex items-center gap-1.5',
                activeTab === 'artifacts' ? 'bg-cyan-500/20 text-cyan-300 font-semibold' : 'text-slate-400 hover:text-slate-200'
              )}
            >
              <FileCheck className="w-3.5 h-3.5 text-amber-400" />
              Artifacts (3)
            </button>

            <button
              onClick={() => { setActiveTab('qa'); setIsOpen(true); }}
              className={cn(
                'px-2.5 py-1 rounded text-xs transition-colors flex items-center gap-1.5',
                activeTab === 'qa' ? 'bg-cyan-500/20 text-cyan-300 font-semibold' : 'text-slate-400 hover:text-slate-200'
              )}
            >
              <ShieldAlert className="w-3.5 h-3.5 text-purple-400" />
              QA Gate Summary
            </button>

            <button
              onClick={() => { setActiveTab('tokens'); setIsOpen(true); }}
              className={cn(
                'px-2.5 py-1 rounded text-xs transition-colors flex items-center gap-1.5',
                activeTab === 'tokens' ? 'bg-cyan-500/20 text-cyan-300 font-semibold' : 'text-slate-400 hover:text-slate-200'
              )}
            >
              <Zap className="w-3.5 h-3.5 text-blue-400" />
              Token & Cost Delta
            </button>
          </div>
        </div>

        {/* Right tools */}
        <div className="flex items-center gap-3 text-xs font-mono">
          <label className="flex items-center gap-1.5 text-slate-400 cursor-pointer">
            <input
              type="checkbox"
              checked={autoScroll}
              onChange={(e) => setAutoScroll(e.target.checked)}
              className="rounded bg-slate-800 border-slate-700 text-cyan-500 focus:ring-0"
            />
            <span className="text-[11px]">Auto-scroll</span>
          </label>
          <span className="text-slate-600">|</span>
          <span className="text-slate-400 text-[11px]">
            Run: <span className="text-cyan-300 font-semibold">{activeRunId}</span> ({runStatus})
          </span>
        </div>
      </div>

      {/* Drawer Body */}
      {isOpen && (
        <div className="flex-1 overflow-y-auto p-3 text-xs font-mono bg-[#050811]">
          {activeTab === 'events' && (
            <div className="space-y-1">
              {events.map((evt) => (
                <div
                  key={evt.event_id}
                  className="flex items-center justify-between p-2 rounded hover:bg-slate-900/60 border border-transparent hover:border-slate-800/80 transition-colors"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <span className="text-slate-500 text-[10px] w-6">#{evt.run_seq}</span>
                    <span className="text-slate-400 text-[11px]">{formatTimestamp(evt.occurred_at)}</span>
                    <span className="text-cyan-400 font-semibold">{evt.event_type}</span>
                    <span className="text-slate-500 truncate max-w-sm">
                      {evt.agent_id ? `[${evt.agent_id}]` : `[${evt.actor_type}]`} - {JSON.stringify(evt.payload_preview).slice(0, 70)}...
                    </span>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <span className="text-slate-600 text-[10px]">{evt.integrity_hash.slice(0, 10)}...</span>
                    <button
                      onClick={() => copyToClipboard(JSON.stringify(evt, null, 2), evt.event_id)}
                      className="p-1 rounded text-slate-500 hover:text-slate-300 hover:bg-slate-800"
                      title="Copy JSON Envelope"
                    >
                      {copiedId === evt.event_id ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'logs' && (
            <div className="space-y-1 text-slate-300">
              <div className="text-slate-500">[14:00:00.120] INFO [Orchestrator] Received creative request req_7 for project prj_match3_hero</div>
              <div className="text-slate-500">[14:00:01.005] INFO [WorkflowEngine] Frozen workflow_version_4 and game_profile_version_2 (SHA-256 verified)</div>
              <div className="text-slate-500">[14:00:01.500] INFO [TrendScout] Ingesting Apple App Store match-3 trend charts</div>
              <div className="text-cyan-400">[14:00:03.110] DEBUG [LiteLLMGateway] Invocating gpt-4o for HypothesisAgent (prompt_version: pt_hypothesis_v3)</div>
              <div className="text-emerald-400">[14:00:04.850] SUCCESS [HypothesisAgent] 4 candidates ideated. Billed 1,200 input, 250 output tokens.</div>
              <div className="text-purple-400">[14:00:06.400] INFO [ComfyUIWorker] Keyframe generation finished. Created artifact_a and artifact_b.</div>
              <div className="text-amber-400">[14:00:15.220] WARN [RemotionWorker] Attempt #1 timed out after 9000ms. Applying exponential backoff retry.</div>
              <div className="text-cyan-400">[14:00:18.010] INFO [RemotionWorker] Attempt #2 started with high-memory fallback GPU cluster.</div>
              <div className="text-emerald-400">[14:00:28.400] SUCCESS [RemotionWorker] Rendered 15s 9:16 vertical video asset (art_video_rescue_final).</div>
              <div className="text-rose-400">[14:00:34.100] WARN [LLMJudge] 7-Gate QA passed. Advisory warning: Similarity cosine 0.74 against reference corpus.</div>
              <div className="text-blue-400">[14:01:12.300] INFO [HumanReview] Creative Lead approved with reason: King asset aligned with Game DNA v2.</div>
              <div className="text-emerald-300 font-semibold">[14:01:13.800] SUCCESS [Orchestrator] Run run_88 completed successfully. Manifest hashed.</div>
            </div>
          )}

          {activeTab === 'artifacts' && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 space-y-1">
                <div className="text-cyan-400 font-semibold text-xs">art_video_rescue_final.mp4</div>
                <div className="text-slate-400 text-[11px]">Type: 9:16 Vertical Video (1080x1920)</div>
                <div className="text-slate-500 text-[10px]">SHA-256: 9f83c12a78129b0a...</div>
                <div className="text-emerald-400 text-[10px] font-semibold">Technical QA Passed</div>
              </div>
              <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 space-y-1">
                <div className="text-purple-400 font-semibold text-xs">artifact_a (Rescue Keyframe)</div>
                <div className="text-slate-400 text-[11px]">Type: High-Res PNG Image Asset</div>
                <div className="text-slate-500 text-[10px]">SHA-256: a1b2c3d4e5f67890...</div>
                <div className="text-emerald-400 text-[10px] font-semibold">Visual QA Passed</div>
              </div>
              <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 space-y-1">
                <div className="text-emerald-400 font-semibold text-xs">art_playable_match3_bundle_v1.zip</div>
                <div className="text-slate-400 text-[11px]">Type: Isolated HTML5 Phaser Playable</div>
                <div className="text-slate-500 text-[10px]">SHA-256: c3d4e5f6a1b27890...</div>
                <div className="text-emerald-400 text-[10px] font-semibold">Playwright Smoke: 0 JS Errors</div>
              </div>
            </div>
          )}

          {activeTab === 'qa' && (
            <div className="space-y-2">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-[11px]">
                <div className="p-2 rounded bg-slate-900 border border-slate-800">
                  <span className="text-slate-400">1. Schema Gate:</span> <span className="text-emerald-400 font-semibold">PASSED</span>
                </div>
                <div className="p-2 rounded bg-slate-900 border border-slate-800">
                  <span className="text-slate-400">2. Technical Gate:</span> <span className="text-emerald-400 font-semibold">PASSED (0 Errors)</span>
                </div>
                <div className="p-2 rounded bg-slate-900 border border-slate-800">
                  <span className="text-slate-400">3. Game Truth Gate:</span> <span className="text-emerald-400 font-semibold">PASSED (0.95)</span>
                </div>
                <div className="p-2 rounded bg-slate-900 border border-slate-800">
                  <span className="text-slate-400">4. Visual QA Gate:</span> <span className="text-emerald-400 font-semibold">PASSED (9:16 OK)</span>
                </div>
                <div className="p-2 rounded bg-slate-900 border border-slate-800">
                  <span className="text-slate-400">5. Similarity Gate:</span> <span className="text-amber-400 font-semibold">WARNING (0.74)</span>
                </div>
                <div className="p-2 rounded bg-slate-900 border border-slate-800">
                  <span className="text-slate-400">6. LLM Judge Gate:</span> <span className="text-emerald-400 font-semibold">PASSED (4.8 / 5.0)</span>
                </div>
                <div className="p-2 rounded bg-slate-900 border border-slate-800 col-span-2">
                  <span className="text-slate-400">7. Human Review Gate:</span> <span className="text-cyan-400 font-semibold">APPROVED by usr_creative_lead</span>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'tokens' && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <div className="p-3 rounded bg-slate-900 border border-slate-800">
                <div className="text-slate-400 text-[10px]">Total Tokens Ingested</div>
                <div className="text-lg font-bold text-slate-100">3,850</div>
                <div className="text-slate-500 text-[10px]">Provider reported</div>
              </div>
              <div className="p-3 rounded bg-slate-900 border border-slate-800">
                <div className="text-slate-400 text-[10px]">Cached Tokens Saved</div>
                <div className="text-lg font-bold text-cyan-400">920</div>
                <div className="text-slate-500 text-[10px]">Deduplicated (No double-bill)</div>
              </div>
              <div className="p-3 rounded bg-slate-900 border border-slate-800">
                <div className="text-slate-400 text-[10px]">Total Run Cost</div>
                <div className="text-lg font-bold text-emerald-400">$0.2347</div>
                <div className="text-slate-500 text-[10px]">Reconciled with catalog</div>
              </div>
              <div className="p-3 rounded bg-slate-900 border border-slate-800">
                <div className="text-slate-400 text-[10px]">Unpriced Calls</div>
                <div className="text-lg font-bold text-slate-400">0</div>
                <div className="text-slate-500 text-[10px]">All media & tokens accounted</div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
