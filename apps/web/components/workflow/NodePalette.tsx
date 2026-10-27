'use client';

import React, { useState } from 'react';
import {
  Search,
  Plus,
  TrendingUp,
  Dna,
  Lightbulb,
  Cpu,
  ShieldCheck,
  GitBranch,
  Download,
  ChevronDown,
  ChevronRight,
  GripVertical,
  Sliders,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { NodeCategory } from '@/lib/types';

interface PaletteItem {
  id: string;
  title: string;
  category: NodeCategory;
  executor: string;
  defaultModel?: string;
  desc: string;
}

const PALETTE_DATA: Record<NodeCategory, PaletteItem[]> = {
  'Market Intelligence': [
    { id: 'source_fetch', title: 'Source Fetch', category: 'Market Intelligence', executor: 'Worker: Scraper/API', defaultModel: 'Deterministic', desc: 'Syncs Apple App Store & TikTok ad feeds' },
    { id: 'deduplicate', title: 'Deduplicate', category: 'Market Intelligence', executor: 'Worker: Hashing', defaultModel: 'SHA-256', desc: 'Dedupes raw snapshots by content hash' },
    { id: 'genre_classifier', title: 'Genre Classifier', category: 'Market Intelligence', executor: 'Agent: TrendScout', defaultModel: 'claude-3-5-sonnet', desc: 'Classifies match-3 / puzzle game mechanics' },
    { id: 'ad_pattern_extract', title: 'Ad Pattern Extract', category: 'Market Intelligence', executor: 'Agent: TrendScout', defaultModel: 'gpt-4o', desc: 'Extracts viral hook mechanics and ad formats' },
    { id: 'trend_synthesis', title: 'Trend Synthesis', category: 'Market Intelligence', executor: 'Agent: EvidenceResolver', defaultModel: 'gemini-1.5-pro', desc: 'Compiles grounded TrendReport artifact' },
  ],
  'Game DNA': [
    { id: 'game_asset_import', title: 'Game Asset Import', category: 'Game DNA', executor: 'Storage Worker', defaultModel: 'S3 Adapter', desc: 'Imports 2D sprites, characters, audio palettes' },
    { id: 'game_dna_extract', title: 'Game DNA Extract', category: 'Game DNA', executor: 'Agent: GameDNAKeeper', defaultModel: 'gpt-4o', desc: 'Freezes game mechanics & brand constraints' },
    { id: 'human_confirm_mechanics', title: 'Human Confirm Mechanics', category: 'Game DNA', executor: 'Human Reviewer', defaultModel: 'Human Gate', desc: 'Requires human sign-off on locked DNA' },
  ],
  'Ideation': [
    { id: 'creative_brief', title: 'Creative Brief', category: 'Ideation', executor: 'User / Strategy', defaultModel: 'Input Spec', desc: 'Brief input and target audience constraints' },
    { id: 'hypothesis_generate', title: 'Hypothesis Generate', category: 'Ideation', executor: 'Agent: HypothesisAgent', defaultModel: 'gpt-4o', desc: 'Ideates 3-8 distinct creative hypotheses' },
    { id: 'hypothesis_rank', title: 'Hypothesis Rank', category: 'Ideation', executor: 'Ranking Engine', defaultModel: 'Heuristic 6-Factor', desc: 'Applies normalized multi-factor rank score' },
    { id: 'concept_board_render', title: 'Concept Board Render', category: 'Ideation', executor: 'Worker: BoardGen', defaultModel: 'Deterministic', desc: 'Assembles interactive mockup board' },
    { id: 'user_select_board', title: 'User Select Board', category: 'Ideation', executor: 'Human User', defaultModel: 'Interactive UI', desc: 'User pins winning concept to trigger build' },
  ],
  'Generation': [
    { id: 'prompt_builder', title: 'Prompt Builder', category: 'Generation', executor: 'Agent: PromptEngineer', defaultModel: 'Template Engine', desc: 'Interpolates versioned golden prompts' },
    { id: 'image_generator', title: 'Image Generator', category: 'Generation', executor: 'Worker: ComfyUI', defaultModel: 'sdxl-turbo / flux', desc: 'Generates high-res visual ad keyframes' },
    { id: 'storyboard_planner', title: 'Storyboard Planner', category: 'Generation', executor: 'Agent: StoryboardAgent', defaultModel: 'claude-3-5-sonnet', desc: 'Plans 15s 9:16 vertical video pacing' },
    { id: 'remotion_render', title: 'Remotion Render', category: 'Generation', executor: 'Worker: Remotion SSR', defaultModel: 'remotion-v4-ssr', desc: 'Renders vertical MP4 video with animations' },
    { id: 'playable_spec', title: 'Playable Spec', category: 'Generation', executor: 'Agent: PlayableSpecAgent', defaultModel: 'gpt-4o', desc: 'Defines 8x8 match-3 gameplay params' },
    { id: 'phaser_codegen', title: 'Phaser Codegen', category: 'Generation', executor: 'Agent: PhaserCoder', defaultModel: 'claude-3-5-sonnet', desc: 'Generates TypeScript HTML5 game bundle' },
    { id: 'sandbox_build', title: 'Sandbox Build', category: 'Generation', executor: 'Worker: IsolatedSandbox', defaultModel: 'esbuild/vite', desc: 'Bundles isolated playable zip with timeout' },
  ],
  'Evaluation': [
    { id: 'browser_qa', title: 'Browser QA', category: 'Evaluation', executor: 'Worker: Playwright', defaultModel: 'Chromium Headless', desc: 'Simulates mobile swipes, zero JS errors' },
    { id: 'schema_validate', title: 'Schema Validate', category: 'Evaluation', executor: 'Validator: Pydantic', defaultModel: 'Pydantic v2', desc: 'Validates JSON output contracts' },
    { id: 'visual_qa', title: 'Visual QA', category: 'Evaluation', executor: 'Worker: VisualQA', defaultModel: 'CV Probe', desc: 'Checks 9:16 aspect ratio & contrast' },
    { id: 'similarity_risk', title: 'Similarity Risk', category: 'Evaluation', executor: 'Worker: pHash', defaultModel: 'Cosine Similarity', desc: 'Detects competitor copyright overlap' },
    { id: 'quality_gate', title: 'Quality Gate', category: 'Evaluation', executor: 'Agent: LLMJudge', defaultModel: 'gpt-4o Rubric v3', desc: 'Executes 7-step quality gate evaluation' },
    { id: 'human_approval', title: 'Human Approval', category: 'Evaluation', executor: 'Creative Lead', defaultModel: 'Human Gate', desc: 'Reasoned approval / rejection decision' },
  ],
  'Control': [
    { id: 'branch', title: 'Branch', category: 'Control', executor: 'Orchestrator', defaultModel: 'DAG Router', desc: 'Conditional workflow branching' },
    { id: 'merge', title: 'Merge', category: 'Control', executor: 'Orchestrator', defaultModel: 'Barrier Sync', desc: 'Consolidates parallel task branches' },
    { id: 'retry_policy', title: 'Retry Policy', category: 'Control', executor: 'Temporal Engine', defaultModel: 'Exp Backoff', desc: 'Exponential backoff & attempt limit' },
    { id: 'budget_gate', title: 'Budget Gate', category: 'Control', executor: 'LiteLLM Guard', defaultModel: 'Hard Limit Guard', desc: 'Blocks run if cost exceeds quota' },
  ],
  'Export': [
    { id: 'artifact_save', title: 'Artifact Save', category: 'Export', executor: 'Storage Worker', defaultModel: 'S3 + SHA256', desc: 'Persists and hashes final assets' },
    { id: 'export_package', title: 'Export Package', category: 'Export', executor: 'Worker: Packager', defaultModel: 'Zip Exporter', desc: 'Bundles Unity / AppLovin creative packs' },
  ],
};

interface NodePaletteProps {
  onAddNode: (item: PaletteItem) => void;
}

export function NodePalette({ onAddNode }: NodePaletteProps) {
  const [search, setSearch] = useState('');
  const [collapsedCategories, setCollapsedCategories] = useState<Record<string, boolean>>({});

  const toggleCategory = (cat: string) => {
    setCollapsedCategories((prev) => ({ ...prev, [cat]: !prev[cat] }));
  };

  const categories = Object.keys(PALETTE_DATA) as NodeCategory[];

  return (
    <div className="w-68 border-r border-white/[0.06] bg-[#0c101a]/75 backdrop-blur-2xl flex flex-col flex-shrink-0 select-none overflow-hidden h-full">
      {/* Palette Header */}
      <div className="p-3.5 border-b border-white/[0.06] space-y-2.5">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold tracking-tight text-neutral-200">
            Node Library
          </span>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-white/[0.06] text-neutral-400 border border-white/[0.08]">
            28 Blocks
          </span>
        </div>

        {/* Apple Style Search Bar */}
        <div className="relative">
          <Search className="w-3.5 h-3.5 text-neutral-500 absolute left-2.5 top-2.5" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Filter blocks..."
            className="w-full bg-white/[0.04] border border-white/[0.07] rounded-lg pl-8 pr-3 py-1.5 text-xs text-neutral-200 placeholder-neutral-500 focus:outline-none focus:border-apple-blue/60 transition-colors font-sans"
          />
        </div>
      </div>

      {/* Palette Items Tree */}
      <div className="flex-1 overflow-y-auto p-2 space-y-2">
        {categories.map((cat) => {
          const items = PALETTE_DATA[cat].filter((item) =>
            search ? item.title.toLowerCase().includes(search.toLowerCase()) || item.desc.toLowerCase().includes(search.toLowerCase()) : true
          );

          if (items.length === 0) return null;
          const isCollapsed = collapsedCategories[cat];

          return (
            <div key={cat} className="rounded-xl bg-white/[0.02] border border-white/[0.05] overflow-hidden">
              <button
                onClick={() => toggleCategory(cat)}
                className="w-full px-3 py-2 flex items-center justify-between text-xs font-medium text-neutral-300 hover:bg-white/[0.04] transition-colors"
              >
                <span className="text-[11px] font-semibold tracking-tight text-neutral-300">{cat}</span>
                <div className="flex items-center gap-1.5 text-neutral-500 text-[10px]">
                  <span>{items.length}</span>
                  {isCollapsed ? <ChevronRight className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                </div>
              </button>

              {!isCollapsed && (
                <div className="p-1 space-y-1">
                  {items.map((item) => (
                    <div
                      key={item.id}
                      onClick={() => onAddNode(item)}
                      className="group p-2 rounded-lg bg-white/[0.03] border border-white/[0.04] hover:border-apple-blue/30 hover:bg-apple-blue/5 transition-all cursor-pointer flex items-center justify-between"
                      title={item.desc}
                    >
                      <div className="min-w-0 pr-2">
                        <div className="text-xs font-medium text-neutral-200 group-hover:text-apple-blue transition-colors truncate">
                          {item.title}
                        </div>
                        <div className="text-[10px] font-mono text-neutral-500 truncate">
                          {item.executor}
                        </div>
                      </div>
                      <button
                        className="w-5 h-5 rounded-md bg-white/[0.06] group-hover:bg-apple-blue text-neutral-400 group-hover:text-white flex items-center justify-center transition-all flex-shrink-0"
                      >
                        <Plus className="w-3 h-3" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
