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
  const [activeTab, setActiveTab] = useState<'events' | 'logs' | 'artifacts' | 'qa' | 'tokens'>('events');
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
        'border-t border-white/[0.06] bg-[#0c101a]/85 backdrop-blur-2xl transition-all duration-300 flex flex-col z-20 select-none shadow-2xl',
        isOpen ? 'h-64' : 'h-9'
      )}
    >
      {/* Drawer Bar Header */}
      <div className="h-9 px-3.5 border-b border-white/[0.04] flex items-center justify-between bg-black/20">
        <div className="flex items-center gap-2">
          {/* Collapse Toggle */}
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="p-1 rounded-md text-neutral-400 hover:text-neutral-200 hover:bg-white/[0.06] transition-colors"
            title={isOpen ? 'Collapse Activity Bar' : 'Expand Activity Bar'}
          >
            {isOpen ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronUp className="w-3.5 h-3.5" />}
          </button>

          {/* Apple Segmented Activity Bar Tabs */}
          <div className="apple-segmented">
            <button
              onClick={() => { setActiveTab('events'); setIsOpen(true); }}
              className={cn(
                'apple-segmented-item flex items-center gap-1.5',
                activeTab === 'events' && 'apple-segmented-item-active'
              )}
            >
              <Activity className="w-3 h-3 text-apple-teal" />
              <span>Events ({events.length})</span>
            </button>

            <button
              onClick={() => { setActiveTab('logs'); setIsOpen(true); }}
              className={cn(
                'apple-segmented-item flex items-center gap-1.5',
                activeTab === 'logs' && 'apple-segmented-item-active'
              )}
            >
              <Terminal className="w-3 h-3 text-apple-emerald" />
              <span>Console Log</span>
            </button>

            <button
              onClick={() => { setActiveTab('artifacts'); setIsOpen(true); }}
              className={cn(
                'apple-segmented-item flex items-center gap-1.5',
                activeTab === 'artifacts' && 'apple-segmented-item-active'
              )}
            >
              <FileCheck className="w-3 h-3 text-apple-amber" />
              <span>Artifacts (3)</span>
            </button>

            <button
              onClick={() => { setActiveTab('qa'); setIsOpen(true); }}
              className={cn(
                'apple-segmented-item flex items-center gap-1.5',
                activeTab === 'qa' && 'apple-segmented-item-active'
              )}
            >
              <ShieldAlert className="w-3 h-3 text-apple-purple" />
              <span>QA Gates</span>
            </button>

            <button
              onClick={() => { setActiveTab('tokens'); setIsOpen(true); }}
              className={cn(
                'apple-segmented-item flex items-center gap-1.5',
                activeTab === 'tokens' && 'apple-segmented-item-active'
              )}
            >
              <Zap className="w-3 h-3 text-apple-blue" />
              <span>Tokens & Cost</span>
            </button>
          </div>
        </div>

        {/* Right Tools & Active Run Status */}
        <div className="flex items-center gap-3 text-xs font-mono">
          <label className="flex items-center gap-1.5 text-neutral-400 cursor-pointer">
            <input
              type="checkbox"
              checked={autoScroll}
              onChange={(e) => setAutoScroll(e.target.checked)}
              className="rounded bg-black/40 border-white/[0.1] text-apple-blue focus:ring-0 w-3 h-3"
            />
            <span className="text-[10px]">Auto-scroll</span>
          </label>
          <span className="text-neutral-700">|</span>
          <span className="text-neutral-400 text-[11px]">
            Run: <span className="text-apple-teal font-medium">{activeRunId}</span> ({runStatus})
          </span>
        </div>
      </div>

      {/* Drawer Body */}
      {isOpen && (
        <div className="flex-1 overflow-y-auto p-3 text-xs font-mono bg-[#070a11]">
          {activeTab === 'events' && (
            <div className="space-y-0.5">
              {events.map((evt) => (
                <div
                  key={evt.event_id}
                  className="flex items-center justify-between py-1.5 px-2.5 rounded-lg hover:bg-white/[0.04] transition-colors"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <span className="text-neutral-500 text-[10px] w-6">#{evt.run_seq}</span>
                    <span className="text-neutral-400 text-[11px]">{formatTimestamp(evt.occurred_at)}</span>
                    <span className="text-apple-teal font-medium">{evt.event_type}</span>
                    <span className="text-neutral-400 truncate max-w-sm">
                      {evt.agent_id ? `[${evt.agent_id}]` : `[${evt.actor_type}]`} - {JSON.stringify(evt.payload_preview).slice(0, 75)}...
                    </span>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <span className="text-neutral-500 text-[10px]">{evt.integrity_hash.slice(0, 10)}...</span>
                    <button
                      onClick={() => copyToClipboard(JSON.stringify(evt, null, 2), evt.event_id)}
                      className="p-1 rounded text-neutral-400 hover:text-white hover:bg-white/[0.08]"
                      title="Copy JSON Envelope"
                    >
                      {copiedId === evt.event_id ? <Check className="w-3 h-3 text-apple-emerald" /> : <Copy className="w-3 h-3" />}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'logs' && (
            <div className="space-y-1 text-neutral-300">
              <div className="text-neutral-500">[14:00:00.120] INFO [Orchestrator] Received creative request req_7 for project prj_match3_hero</div>
              <div className="text-neutral-500">[14:00:01.005] INFO [WorkflowEngine] Frozen workflow_version_4 and game_profile_version_2 (SHA-256 verified)</div>
              <div className="text-neutral-500">[14:00:01.500] INFO [TrendScout] Ingesting Apple App Store match-3 trend charts</div>
              <div className="text-apple-teal">[14:00:03.110] DEBUG [LiteLLMGateway] Invocating gpt-4o for HypothesisAgent (prompt_version: pt_hypothesis_v3)</div>
              <div className="text-apple-emerald">[14:00:04.850] SUCCESS [HypothesisAgent] 4 candidates ideated. Billed 1,200 input, 250 output tokens.</div>
              <div className="text-apple-purple">[14:00:06.400] INFO [ComfyUIWorker] Keyframe generation finished. Created artifact_a and artifact_b.</div>
              <div className="text-apple-amber">[14:00:15.220] WARN [RemotionWorker] Attempt #1 timed out after 9000ms. Applying exponential backoff retry.</div>
              <div className="text-apple-teal">[14:00:18.010] INFO [RemotionWorker] Attempt #2 started with high-memory fallback GPU cluster.</div>
              <div className="text-apple-emerald">[14:00:28.400] SUCCESS [RemotionWorker] Rendered 15s 9:16 vertical video asset (art_video_rescue_final).</div>
              <div className="text-apple-red">[14:00:34.100] WARN [LLMJudge] 7-Gate QA passed. Advisory warning: Similarity cosine 0.74 against reference corpus.</div>
              <div className="text-apple-blue">[14:01:12.300] INFO [HumanReview] Creative Lead approved with reason: King asset aligned with Game DNA v2.</div>
              <div className="text-apple-emerald font-semibold">[14:01:13.800] SUCCESS [Orchestrator] Run run_88 completed successfully. Manifest hashed.</div>
            </div>
          )}

          {activeTab === 'artifacts' && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div className="p-3 rounded-xl bg-white/[0.03] border border-white/[0.06] space-y-1">
                <div className="text-apple-teal font-semibold text-xs">art_video_rescue_final.mp4</div>
                <div className="text-neutral-400 text-[11px]">Type: 9:16 Vertical Video (1080x1920)</div>
                <div className="text-neutral-500 text-[10px]">SHA-256: 9f83c12a78129b0a...</div>
                <div className="text-apple-emerald text-[10px] font-semibold">Technical QA Passed</div>
              </div>
              <div className="p-3 rounded-xl bg-white/[0.03] border border-white/[0.06] space-y-1">
                <div className="text-apple-purple font-semibold text-xs">artifact_a (Rescue Keyframe)</div>
                <div className="text-neutral-400 text-[11px]">Type: High-Res PNG Image Asset</div>
                <div className="text-neutral-500 text-[10px]">SHA-256: a1b2c3d4e5f67890...</div>
                <div className="text-apple-emerald text-[10px] font-semibold">Visual QA Passed</div>
              </div>
              <div className="p-3 rounded-xl bg-white/[0.03] border border-white/[0.06] space-y-1">
                <div className="text-apple-emerald font-semibold text-xs">art_playable_match3_bundle_v1.zip</div>
                <div className="text-neutral-400 text-[11px]">Type: Isolated HTML5 Phaser Playable</div>
                <div className="text-neutral-500 text-[10px]">SHA-256: c3d4e5f6a1b27890...</div>
                <div className="text-apple-emerald text-[10px] font-semibold">Playwright Smoke: 0 JS Errors</div>
              </div>
            </div>
          )}

          {activeTab === 'qa' && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-[11px]">
              <div className="p-2.5 rounded-xl bg-white/[0.03] border border-white/[0.06]">
                <span className="text-neutral-400">1. Schema Gate:</span> <span className="text-apple-emerald font-semibold ml-1">PASSED</span>
              </div>
              <div className="p-2.5 rounded-xl bg-white/[0.03] border border-white/[0.06]">
                <span className="text-neutral-400">2. Technical Gate:</span> <span className="text-apple-emerald font-semibold ml-1">PASSED</span>
              </div>
              <div className="p-2.5 rounded-xl bg-white/[0.03] border border-white/[0.06]">
                <span className="text-neutral-400">3. Game Truth Gate:</span> <span className="text-apple-emerald font-semibold ml-1">0.95</span>
              </div>
              <div className="p-2.5 rounded-xl bg-white/[0.03] border border-white/[0.06]">
                <span className="text-neutral-400">4. Visual QA Gate:</span> <span className="text-apple-emerald font-semibold ml-1">9:16 OK</span>
              </div>
              <div className="p-2.5 rounded-xl bg-white/[0.03] border border-white/[0.06]">
                <span className="text-neutral-400">5. Similarity Gate:</span> <span className="text-apple-amber font-semibold ml-1">0.74 (Advisory)</span>
              </div>
              <div className="p-2.5 rounded-xl bg-white/[0.03] border border-white/[0.06]">
                <span className="text-neutral-400">6. LLM Judge Gate:</span> <span className="text-apple-emerald font-semibold ml-1">4.8 / 5.0</span>
              </div>
              <div className="p-2.5 rounded-xl bg-white/[0.03] border border-white/[0.06] col-span-2">
                <span className="text-neutral-400">7. Human Review:</span> <span className="text-apple-blue font-semibold ml-1">APPROVED by usr_creative_lead</span>
              </div>
            </div>
          )}

          {activeTab === 'tokens' && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <div className="p-3 rounded-xl bg-white/[0.03] border border-white/[0.06]">
                <div className="text-neutral-400 text-[10px]">Total Ingested</div>
                <div className="text-base font-semibold text-neutral-100">3,850</div>
                <div className="text-neutral-500 text-[10px]">Tokens billed</div>
              </div>
              <div className="p-3 rounded-xl bg-white/[0.03] border border-white/[0.06]">
                <div className="text-neutral-400 text-[10px]">Cached Tokens</div>
                <div className="text-base font-semibold text-apple-teal">920</div>
                <div className="text-neutral-500 text-[10px]">Deduplicated</div>
              </div>
              <div className="p-3 rounded-xl bg-white/[0.03] border border-white/[0.06]">
                <div className="text-neutral-400 text-[10px]">Total Run Cost</div>
                <div className="text-base font-semibold text-apple-emerald">$0.2347</div>
                <div className="text-neutral-500 text-[10px]">LiteLLM catalog</div>
              </div>
              <div className="p-3 rounded-xl bg-white/[0.03] border border-white/[0.06]">
                <div className="text-neutral-400 text-[10px]">Unpriced Calls</div>
                <div className="text-base font-semibold text-neutral-400">0</div>
                <div className="text-neutral-500 text-[10px]">Full reconciliation</div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
